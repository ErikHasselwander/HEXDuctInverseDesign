from pathlib import Path
import matplotlib.pyplot as plt

def save_plots(
    plot_path: Path,
    plots,
    vline_x = None,
    axis = None,
):    
    plot_path.parent.mkdir(exist_ok=True, parents=True)

    plt.figure()
    for key, value in plots.items():
        plt.plot(value[0], value[1], label=key)
    if vline_x is not None:
        plt.axvline(vline_x, linestyle="--", color="black")
    plt.grid()
    if axis is not None:
        plt.axis(axis)
    plt.xlabel("x")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path, dpi=200)
    plt.close()

def save_linear_inverse_floating_p0_plots(
    plot_path: Path,
    x_lin,
    delta,
    new_geometry,
    disp,
    geometry,
    target_interp,
    current_interp,
    vline_x = None,
):
    plot_path.mkdir(exist_ok=True, parents=True)

    plt.figure()
    plt.plot(x_lin, delta)
    if vline_x is not None:
        plt.axvline(vline_x)
    plt.grid()
    plt.xlabel("x")
    plt.ylabel("delta p")
    plt.tight_layout()
    plt.savefig(plot_path / "deltap.png", dpi=200)
    plt.close()

    plt.figure()
    plt.plot(new_geometry[:len(disp), 0], disp)
    plt.xlabel("x")
    plt.ylabel("disp")
    if vline_x is not None:
        plt.axvline(vline_x)
    plt.grid()
    # plt.xlim(0.475, 0.5)
    plt.tight_layout()
    plt.savefig(plot_path / "displacement.png", dpi=200)
    plt.close()

    plt.figure()
    plt.plot(new_geometry[:, 0], new_geometry[:, 1])
    plt.plot(geometry[:, 0], geometry[:, 1])
    plt.xlabel("x")
    plt.ylabel("comp")
    if vline_x is not None:
        plt.axvline(vline_x)
    plt.grid()
    plt.tight_layout()
    plt.savefig(plot_path / "geometrycomparison.png", dpi=200)
    plt.close()

    plt.figure()
    plt.plot(x_lin, target_interp, label="target")
    plt.plot(x_lin, current_interp, label="current")
    plt.legend()
    if vline_x is not None:
        plt.axvline(vline_x)
    plt.grid()
    plt.xlabel("x")
    plt.ylabel("p")
    plt.tight_layout()
    plt.savefig(plot_path / "pcomparison.png", dpi=200)
    plt.close()
