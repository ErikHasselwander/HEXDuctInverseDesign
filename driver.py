import os
import subprocess
from pathlib import Path
from SGMG.star_geometry_macro_generator import StarGeometryMacroGenerator
from helpers.misc import load_csv, load_x_y, replace_starccm_savefile
from datetime import datetime

import numpy as np

class inverseDesignDriver:
    def __init__(self, inverse_geometry_function, geometry_generator, case_path: Path, refFiles_path: Path):
        self.STARCCM_path = "starccm+"
        self.starccm_host = "c22ghrt.tfd.chalmers.se:47830"

        self.refFiles_path = refFiles_path
        self.save_macro_path = self.refFiles_path / "save.java"
        self.replace_geometry_macro_path = self.refFiles_path / "replace_geometry.java"
        self.post_macro_path = self.refFiles_path / "post_star.java"
        self.constant_variables_macro_path = self.refFiles_path / "updates_variables.java"

        self.inverse_geometry_function = inverse_geometry_function
        self.inv_kwargs = {}

        self.geometry_generator = geometry_generator
        self.geometry_kwargs = {}

        self.case_path = case_path
        self.current_iteration = 0
        
        self.current_case_path = self.case_path / self.__get_dir_name(self.current_iteration)
        self.geometry_macro_name = "geometry"
        self.lower_pd_filename = "lower_diff_p.csv"
        self.upper_pd_filename = "upper_diff_p.csv"
        self.curve_dir = "curves"
        self.lower_x_y_filename = "inlet_diff_wall_lower.csv"
        self.upper_x_y_filename = "inlet_diff_wall_upper.csv"
        self.exit_early = False
        self.target_field = ""

    def set_exit(self, exit_early: bool):
        self.exit_early = exit_early

    def set_inv_target_field(self, field: str):
        self.target_field = field

    def set_inv_kwargs(self, inv_kwargs):
        self.inv_kwargs = inv_kwargs

    def set_geometry_kwargs(self, geometry_kwargs):
        self.geometry_kwargs = geometry_kwargs

    def run_basecase(self, basecase_path: Path):
        self.basecase_path = basecase_path
        self.current_case_path = self.basecase_path
        self.current_case_path.mkdir(parents=True, exist_ok=True)
        beforevalue = self.constant_star_variables
        self.constant_star_variables = False
        self.__generate_next_case(basecase=True)
        self.constant_star_variables = beforevalue
        self.__run_current_case()
        self.lower_target = None
        self.upper_target = None
        self.last_case_path = self.basecase_path
        self.current_iteration = 1

    def set_current_variables(self, inputdict: dict):
        self.constant_star_variables = False
        self.current_star_variables = inputdict

    def set_restart(self, basecase_path, current_n):
        self.basecase_path = basecase_path
        self.current_case_path = self.basecase_path
        if current_n > 1:
            self.last_case_path = self.case_path / self.__get_dir_name(current_n-1)
        else:
            self.last_case_path = self.basecase_path
        self.lower_target = load_csv(self.basecase_path / self.lower_pd_filename, self.target_field)
        self.upper_target = load_csv(self.basecase_path / self.upper_pd_filename, self.target_field)
        self.current_iteration = current_n

    def run_inverse_iteration(self):
        print(f"[{datetime.now():%H:%M:%S}] Iteration: {self.current_iteration}")        
        self.current_case_path = self.case_path / self.__get_dir_name(self.current_iteration)
        self.__generate_next_case()
        self.__run_current_case()
        self.last_case_path = self.current_case_path
        self.current_iteration = self.current_iteration + 1

    def __get_dir_name(self, iteration):
        return f"it_{iteration}"

    def __generate_next_save_dir_macro(self):
        replace_starccm_savefile(self.save_macro_path, self.current_case_path / "case.sim")
        return self.save_macro_path

    def __generate_next_geometry_macro(self):
        current_geometry_lower = load_x_y(self.last_case_path / self.curve_dir / self.lower_x_y_filename)
        current_pressure_lower = load_csv(self.last_case_path / self.lower_pd_filename, self.target_field)
        lower_curve = self.inverse_geometry_function(current_geometry_lower, self.lower_target, current_pressure_lower, 350, -1, self.current_case_path / "lower_inv_outp", **self.inv_kwargs)

        current_geometry_upper = load_x_y(self.last_case_path / self.curve_dir / self.upper_x_y_filename)
        current_pressure_upper = load_csv(self.last_case_path / self.upper_pd_filename, self.target_field)
        upper_curve = self.inverse_geometry_function(current_geometry_upper, self.upper_target, current_pressure_upper, 350, 1, self.current_case_path / "upper_inv_outp", **self.inv_kwargs)

        upper_curve = np.copy(lower_curve)
        upper_curve[:,1] = -upper_curve[:,1]

        geometry = self.geometry_generator(lower_curve, upper_curve, **self.geometry_kwargs)
        geometry_storage = geometry.geometry
        geometry_storage.plot_geometry(savepath = self.current_case_path / "geometry.png")
        geometry_storage.export_curves_to_csv(self.current_case_path / "curves")
        macro_path = self.current_case_path
        return StarGeometryMacroGenerator(geometry_storage, self.geometry_macro_name, macro_path).getPath()
    
    def __generate_basecase_geometry_macro(self):
        geometry = self.geometry_generator(**self.geometry_kwargs)
        geometry_storage = geometry.geometry
        geometry_storage.plot_geometry(savepath = self.current_case_path / "geometry.png")
        geometry_storage.export_curves_to_csv(self.current_case_path / "curves")
        macro_path = self.current_case_path
        return StarGeometryMacroGenerator(geometry_storage, self.geometry_macro_name, macro_path).getPath()

    def __generate_next_case(self, basecase=False):
        if basecase:
            geometry_macro_path = self.__generate_basecase_geometry_macro()
        else:
            geometry_macro_path = self.__generate_next_geometry_macro()

        save_new_dir_macro = self.__generate_next_save_dir_macro()

        self.current_batch_commands = []
        self.current_batch_commands.append(save_new_dir_macro)
        variables_macro_path = self.__generate_variable_macro(self.current_star_variables, self.current_case_path)
        self.current_batch_commands.append(variables_macro_path)
        self.current_batch_commands.append(geometry_macro_path)
        self.current_batch_commands.append(self.replace_geometry_macro_path)
        self.current_batch_commands.append("run")
        self.current_batch_commands.append(self.post_macro_path)


    def __run_current_case(self) -> None:
        """Run a STAR-CCM+ case and write stdout/stderr to log files."""
        if self.exit_early:
            exit()
        self.logFilePath: Path = self.current_case_path / "CFD_out.txt"
        self.logErrorFilePath: Path = self.current_case_path / "CFD_err.txt"
        batch = ",".join(map(str, self.current_batch_commands))
        star = str(self.STARCCM_path)

        cmd: list[str] = [
            star,
            "-host", self.starccm_host,
            "-batch", batch,
            "-noexit"
        ]

        with (
            open(self.logFilePath, "w", encoding="utf-8", buffering=1) as stdout_f,
            open(self.logErrorFilePath, "w", encoding="utf-8", buffering=1) as stderr_f,
        ):
            result = subprocess.run(
                cmd,
                cwd=self.current_case_path,
                stdout=stdout_f,
                stderr=stderr_f,
                text=True,
                check=False,
                start_new_session=True
            )

    def __generate_variable_macro(self, starInputDict: dict, path: Path) -> Path:
        macroName = "update_variables"
        macroPath = path / (macroName + ".java")
        with open(macroPath, "w+") as macroFile:
            macroFile.write(f"package macro;\n")
            macroFile.write(f"import java.util.*;\n")
            macroFile.write(f"import star.common.*;\n")
            macroFile.write(f"import star.base.neo.*;\n")
            macroFile.write(f"\n")
            macroFile.write(f"public class {macroName} extends StarMacro {{\n")
            macroFile.write(f"  public void execute() {{\n")
            macroFile.write(f"    execute0();\n")
            macroFile.write(f"  }}\n")
            macroFile.write(f"\n")
            macroFile.write(f"  private void execute0() {{\n")
            macroFile.write(f"    Simulation simulation_0 = getActiveSimulation();\n")
            macroFile.write(f"\n")
            for index, (key, value) in enumerate(starInputDict.items()):
                macroFile.write(
                    f'    ScalarGlobalParameter scalarGlobalParameter_{index} = ((ScalarGlobalParameter) simulation_0.get(GlobalParameterManager.class).getObject("{key}"));\n'
                )
                macroFile.write(
                    f"    scalarGlobalParameter_{index}.getQuantity().setValue({value});\n"
                )
            macroFile.write(f"\n")
            macroFile.write(f"  }}\n")
            macroFile.write(f"}}\n")

        return macroPath
