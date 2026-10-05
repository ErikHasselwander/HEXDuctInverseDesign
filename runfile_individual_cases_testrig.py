from driver import inverseDesignDriver
from helpers.tesrig_geometry import straightwalledWithRadii2DGeometryInletHEXOutlet
from helpers.inverse_design import no_inv
from pathlib import Path

cwd = Path.cwd()
casepath = cwd / "basecases" / "kwcc200k_RWfillet"
casepath.mkdir(parents=True, exist_ok=True)

inv_fnc = no_inv
inv_kwargs = {}

geom_generator = straightwalledWithRadii2DGeometryInletHEXOutlet

lengths = [100e-3, 80e-3, 60e-3, 40e-3, 20e-3]
angles = [8,7,6,5,4,2,0]
fillet_R_over_Ws = [0.25, 0.5, 0.75, 1]

driver = inverseDesignDriver(inv_fnc, geom_generator, casepath, cwd / "refFiles")
from datetime import datetime

driver.set_inv_kwargs(inv_kwargs)
driver.set_current_variables({"Kp_streamwise": 0})

cases = [(length, angle, fillet_R_over_W) for length in lengths for angle in angles for fillet_R_over_W in fillet_R_over_Ws]
n = len(cases)

for i, (length, angle, fillet_R_over_W) in enumerate(cases, start=1):
    casename = f"length_{length:.2f}_angle_{angle}_RW_{fillet_R_over_W}"
    ts = datetime.now().strftime("%H:%M")
    print(f"[{ts}]: [{i}/{n}] {casename}", flush=True)

    geom_kwargs = {
        "input_dict": {
            "AR": None,
            "wall_angle": angle,
            "L_diffuser": length,
            "fillet_R_over_W": fillet_R_over_W
        }
    }
    driver.set_geometry_kwargs(geom_kwargs)
    driver.run_basecase(casepath / casename)