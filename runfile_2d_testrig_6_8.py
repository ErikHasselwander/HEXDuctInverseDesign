from driver import inverseDesignDriver
from helpers.tesrig_geometry import defined2DGeometryInletHEXVariableContractionOutlet
from helpers.inverse_design_mgm_normalized import normalized_mgm_on_wall_shear_stress
from pathlib import Path

cwd = Path.cwd()
casepath = cwd / "testrig_cases" / "6_7_05_rc_kp65_dps20_pe05"
basecasepath = casepath / "basecase"
refpath = cwd / "refFiles"

inv_fnc = normalized_mgm_on_wall_shear_stress

t = 9e-4 / 4
inv_kwargs = {
    "beta": (1 / t, 0 / t, -0.0002 / t),
    "circle_section_x": 1e-3,
    "delta_power_scale": 2,
    "pace_exponent": 0.5,
    "max_step_size": 0.002,
}

Kp_streamwise = 65

geom_generator = defined2DGeometryInletHEXVariableContractionOutlet
geom_kwargs = {
    "input_dict":
    {
        "AR": None,
        "wall_angle": 8,
        "L_diffuser": 0.06,
    }
}

exit_early = False
restart_point = 101
n_iter = 100

driver = inverseDesignDriver(inv_fnc, geom_generator, casepath, refpath)
driver.set_exit(exit_early)

driver.set_inv_kwargs(inv_kwargs)
driver.set_geometry_kwargs(geom_kwargs)
driver.set_current_variables({"Kp_streamwise": Kp_streamwise})

# driver.set_inv_target_field("Pressure (Pa)")
driver.set_inv_target_field("Wall Tangential Shear Stress (Pa)")

# driver.run_basecase(basecasepath)
driver.set_restart(basecasepath, current_n=restart_point)
driver.set_current_variables({"Kp_streamwise": Kp_streamwise})
# driver.run_inverse_iteration()
# driver.run_inverse_iteration()
# exit()
# driver.set_newton(True)
for _ in range(n_iter):
    driver.run_inverse_iteration()
