from dataclasses import dataclass, field
from pathlib import Path
import re

import numpy as np
import matplotlib.pyplot as plt

def _safe_filename(s: str, max_len: int = 80) -> str:
    """
    Make a string safe to use as a filename across platforms.
    Keeps letters/numbers/._- and replaces everything else with '_'.
    """
    s = s.strip()
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    s = s.strip("._-")
    return (s[:max_len] or "curve")


@dataclass
class Curve:
    points: np.ndarray
    face_name: str

    def length(self):
        return len(self.points)

    def export_csv(self, filepath: str | Path, *, fmt: str = "%.18e") -> Path:
        """
        Export this curve to a CSV file as two columns: x,y.
        The CSV is directly loadable via e.g.:
            pts = np.loadtxt(filepath, delimiter=",")
        """
        p = np.asarray(self.points)

        if p.ndim != 2 or p.shape[1] != 2:
            raise TypeError("Curve points must be a numpy array of shape (N, 2).")

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # No header -> simplest possible numpy load:
        np.savetxt(filepath, p, delimiter=",", fmt=fmt)
        return filepath


@dataclass
class Sketch:
    name: str
    curves: list[Curve] = field(default_factory=list)
    unite: bool = False
    type: str = "extrude"

    def add_curve(self, curve: Curve):
        if not isinstance(curve.points, np.ndarray) or curve.points.shape[1] != 2:
            raise TypeError("Curve must be a numpy array of shape (N, 2).")
        self.curves.append(curve)

    def length(self):
        return len(self.curves)


@dataclass
class GeometryStorage:
    name: str
    sketches: dict[str, Sketch] = field(default_factory=dict)

    def add_sketch(self, sketch: Sketch):
        if sketch.name in self.sketches:
            raise ValueError(f"Sketch '{sketch.name}' already exists.")
        self.sketches[sketch.name] = sketch

    def add_curve(self, sketch_name: str, curve: Curve):
        if sketch_name not in self.sketches:
            raise ValueError(
                f"Sketch '{sketch_name}' does not exist. Add the sketch first."
            )
        self.sketches[sketch_name].add_curve(curve)

    def get_sketches(self) -> dict[str, Sketch]:
        return self.sketches

    def plot_geometry(self, savepath: Path = None):
        fig, ax = plt.subplots()

        for sketch in self.sketches.values():
            for curve in sketch.curves:
                points = curve.points
                if len(points) == 2:
                    midpoint = (points[0] + points[1]) / 2
                    points = np.vstack([points[0], midpoint, points[1]])

                curve_mid_idx = int(np.floor(len(points) / 2))
                ax.plot(points[:, 0], points[:, 1], label=curve.face_name)
                ax.annotate(
                    f"${curve.face_name}$",
                    (points[curve_mid_idx, 0], points[curve_mid_idx, 1]),
                )

        # Get current y-axis limits
        ymin, ymax = ax.get_ylim()
        # Only set ylim to 0 if the current lower limit is greater than 0
        if ymin > 0:
            ax.set_ylim(bottom=0)
        if savepath is not None:
            savepath = Path(savepath)
            savepath.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(savepath, bbox_inches="tight", dpi=300)

            plt.close(fig)
            return None, None

        return fig, ax

    def export_curves_to_csv(
        self,
        target_folder: str | Path,
        *,
        per_sketch_subfolders: bool = False,
        fmt: str = "%.6e",
    ) -> dict[tuple[str, int, str], Path]:
        """
        Export every curve in every sketch into a CSV file (two columns: x,y).

        Parameters
        ----------
        target_folder:
            Directory where CSVs will be written. Created if missing.
        per_sketch_subfolders:
            If True, files go into subfolders: target_folder/<sketch_name>/...
        fmt:
            Floating point format passed to numpy.savetxt.

        Returns
        -------
        A mapping from (sketch_name, curve_index, face_name) -> Path to the CSV.
        """
        target_folder = Path(target_folder)
        target_folder.mkdir(parents=True, exist_ok=True)

        out: dict[tuple[str, int, str], Path] = {}

        storage_name = _safe_filename(self.name)

        for sketch_name, sketch in self.sketches.items():
            safe_sketch = _safe_filename(sketch_name)

            base_dir = (
                (target_folder / safe_sketch) if per_sketch_subfolders else target_folder
            )
            base_dir.mkdir(parents=True, exist_ok=True)

            for i, curve in enumerate(sketch.curves):
                safe_face = _safe_filename(curve.face_name)

                filename = f"{safe_sketch}_{safe_face}.csv"
                path = base_dir / filename

                curve.export_csv(path, fmt=fmt)
                out[(sketch_name, i, curve.face_name)] = path

        return out
