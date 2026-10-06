import numpy as np
import pandas as pd
from pathlib import Path

def implicit_global_smooth(x, d_raw, sigma, lam=1.0, fix_left=True, fix_right=False):
    x = np.asarray(x, dtype=float)
    d_raw = np.asarray(d_raw, dtype=float)
    n = len(x)

    dx = x[:, None] - x[None, :]
    W = np.exp(-(dx**2) / (sigma**2))
    np.fill_diagonal(W, 0.0)

    L = np.diag(W.sum(axis=1)) - W
    A = np.eye(n) + lam * L
    b = d_raw.copy()

    if fix_left:
        A[0, :] = 0.0
        A[0, 0] = 1.0
        b[0] = 0

    if fix_right:
        A[-1, :] = 0.0
        A[-1, -1] = 1.0
        b[-1] = 0

    return np.linalg.solve(A, b)

def rotate_point(point, origin, angle):

    theta = np.deg2rad(angle)
    R = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta),  np.cos(theta)]
    ])

    return origin + R @ (point - origin)

def load_csv(csv_path: Path, y: str, x: str = "X (m)") -> np.ndarray:
    """
    Returns an (N, 2) array with columns: [x, field]

    Assumptions:
      - 2D
      - Wall shear stress vector is already tangential
      - Wall is never vertical
      - Positive tangential shear = to the right (+x)
    """
    df = pd.read_csv(csv_path).sort_values(by=x)
    x_vals = df[x].to_numpy(dtype=float)
    if "Wall Shear Stress[i] (Pa)" not in df:
        return df[[x, y]].to_numpy(dtype=float)
    if y == "Wall Shear Stress: Magnitude (Pa)":
        tau = df[[
            "Wall Shear Stress[i] (Pa)",
            "Wall Shear Stress[j] (Pa)",
        ]].to_numpy(dtype=float)

        y_vals = np.linalg.norm(tau, axis=1)

    elif y == "Wall Tangential Shear Stress (Pa)":
        tau = df[[
            "Wall Shear Stress[i] (Pa)",
            "Wall Shear Stress[j] (Pa)",
        ]].to_numpy(dtype=float)

        tau_mag = np.linalg.norm(tau, axis=1)
        sign = np.sign(tau[:, 0])  # sign from x-component only

        # Optional numerical safety
        sign[(sign == 0.0) & (tau_mag > 0.0)] = 1.0

        y_vals = sign * tau_mag

    else:
        return df[[x, y]].to_numpy(dtype=float)

    return np.column_stack((x_vals, y_vals))


def load_x_y(csv_path: Path) -> np.ndarray:
    arr = np.loadtxt(csv_path, delimiter=",")
    return arr[np.argsort(arr[:, 0])]

from pathlib import Path
import re

def replace_starccm_savefile(java_path: str | Path, new_sim_path: str | Path) -> None:
    """
    Replace the argument to simulation_0.saveState("...") in a STAR-CCM+ macro .java file.

    Parameters
    ----------
    java_path : str | Path
        Path to the save.java file to edit (in-place).
    new_sim_path : str
        New .sim file path to write into the macro.

    Raises
    ------
    FileNotFoundError
        If java_path doesn't exist.
    ValueError
        If no saveState(...) call is found (or if multiple are found).
    """
    new_sim_path = str(new_sim_path)
    java_path = Path(java_path)
    text = java_path.read_text(encoding="utf-8")

    # Match: simulation_0.saveState("..."); allowing whitespace/newlines
    pattern = re.compile(
        r'(simulation_0\s*\.\s*saveState\s*\(\s*")([^"]*)("\s*\)\s*;)',
        flags=re.MULTILINE | re.DOTALL
    )

    matches = list(pattern.finditer(text))
    if not matches:
        raise ValueError(f"No simulation_0.saveState(\"...\") call found in {java_path}")
    if len(matches) > 1:
        raise ValueError(f"Multiple saveState calls found in {java_path}; refusing to guess.")

    # Escape backslashes for Java string literals (mostly relevant on Windows paths)
    new_sim_path_escaped = new_sim_path.replace("\\", "\\\\")

    new_text = pattern.sub(rf'\1{new_sim_path_escaped}\3', text, count=1)
    java_path.write_text(new_text, encoding="utf-8")
