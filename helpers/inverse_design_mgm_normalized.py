import numpy as np
from scipy.interpolate import CubicSpline

from helpers.inverse_design_helpers import poly4_segment, arc_segment
from helpers.plotting import save_plots
from helpers.numerical import gaussian_kernel_smooth, fd_weights

def normalize_to_unit(x):
    return (x - x[0]) / (x[-1] - x[0])


def normalized_mgm_on_wall_shear_stress(
    geometry,
    target_wss,
    current_wss,
    n_interpolation,
    direction,
    plot_path=None,
    beta=(1.2, 0.0, 0.4),
    inlet_tangent=(1.0, 0.0),
    delta_power_scale=2,
    pace_exponent=0.5,
    circle_section_x=None,
    max_step_size=None,
):
    beta0, beta1, beta2 = beta
    if (current_wss.shape == target_wss.shape) and (current_wss == target_wss).all():
        return geometry
    # ------------------------------------------------------------------
    # Interpolate geometry to x_lin using arc-length based sampling
    # ------------------------------------------------------------------
    x_dense = geometry[:, 0]
    y_dense = geometry[:, 1]

    ds = np.sqrt(np.diff(x_dense)**2 + np.diff(y_dense)**2)
    s_dense = np.concatenate(([0.0], np.cumsum(ds)))
    s_lin = np.linspace(s_dense[0], s_dense[-1], n_interpolation)

    x_lin = np.interp(s_lin, s_dense, x_dense)

    geom_spline = CubicSpline(x_dense, y_dense)

    if circle_section_x is not None:
        circle_section_x_plot = geometry[-1, 0] - circle_section_x
        s_circle = np.interp(circle_section_x_plot, x_dense, s_dense)

        frac = (s_circle - s_dense[0]) / (s_dense[-1] - s_dense[0])
        n1 = max(int(round(n_interpolation * frac)), 2)
        n2 = max(n_interpolation - n1 + 1, 2)

        s_lin_1 = np.linspace(s_dense[0], s_circle, n1, endpoint=True)
        s_lin_2 = np.linspace(s_circle, s_dense[-1], n2, endpoint=True)
        s_lin = np.concatenate([s_lin_1, s_lin_2[1:]])

        circle_section_idx = n1 - 1
        x_lin = np.interp(s_lin, s_dense, x_dense)
        circle_section_x_plot = x_lin[circle_section_idx]
    else:
        s_lin = np.linspace(s_dense[0], s_dense[-1], n_interpolation)
        x_lin = np.interp(s_lin, s_dense, x_dense)
        circle_section_idx = 0

    geom = np.column_stack((x_lin, geom_spline(x_lin)))

    
    n_active = circle_section_idx + 1 if circle_section_idx is not None else len(x_lin)
    x_active = x_lin[:n_active]
    normalized_x_active = normalize_to_unit(x_active)

    # interpolate WSS only on active region
    target_spline = CubicSpline(target_wss[:, 0], target_wss[:, 1])
    current_spline = CubicSpline(current_wss[:, 0], current_wss[:, 1])
    raw_delta = -(target_spline(x_lin) - current_spline(x_lin))[:n_active]

    # interpolate WSS only on active region
    target_spline = CubicSpline(target_wss[:, 0], target_wss[:, 1])
    current_spline = CubicSpline(current_wss[:, 0], current_wss[:, 1])

    # raw residual - no pre-smoothing needed, the MGM system itself will regularize it
    raw_delta= -(target_spline(x_lin) - current_spline(x_lin))
    smoothed_delta = gaussian_kernel_smooth(normalize_to_unit(x_lin), raw_delta)
    delta_active = smoothed_delta[:n_active]
    # delta_active -= delta_active[0]

    # ------------------------------------------------------------------
    # MGM system on active region only
    # ------------------------------------------------------------------
    inlet_slope = inlet_tangent[1] / inlet_tangent[0]
    delta_active_abs = np.abs(delta_active)
    delta_active_sign = np.sign(delta_active)

    M = np.max(delta_active_abs)
    print(f"Max |delta_active|: {M}")

    pace_correction = M ** (pace_exponent - delta_power_scale)
    rhs = direction * np.power(delta_active_abs, delta_power_scale) * delta_active_sign * pace_correction
    
    n = len(normalized_x_active)
    A = np.zeros((n, n), dtype=float)
    b = np.zeros(n, dtype=float)

    # BC 1: exact left point
    A[0, 0] = 1.0
    b[0] = 0.0

    # BC 2: exact inlet tangent
    w = fd_weights(normalized_x_active[:3], normalized_x_active[0], deriv_order=1)
    A[1, :3] = w
    b[1] = inlet_slope

    # Interior rows
    for i in range(2, n - 1):
        h0 = normalized_x_active[i] - normalized_x_active[i - 1]
        h1 = normalized_x_active[i + 1] - normalized_x_active[i]

        d1_im1 = -h1 / (h0 * (h0 + h1))
        d1_i   = (h1 - h0) / (h0 * h1)
        d1_ip1 =  h0 / (h1 * (h0 + h1))

        d2_im1 =  2.0 / (h0 * (h0 + h1))
        d2_i   = -2.0 / (h0 * h1)
        d2_ip1 =  2.0 / (h1 * (h0 + h1))

        A[i, i - 1] = beta2 * d2_im1 + beta1 * d1_im1
        A[i, i    ] = beta2 * d2_i   + beta1 * d1_i + beta0
        A[i, i + 1] = beta2 * d2_ip1 + beta1 * d1_ip1
        b[i] = rhs[i]

    # Last row: membrane equation at end of active region
    d1w = fd_weights(x_active[-3:], x_active[-1], deriv_order=1)
    d2w = fd_weights(x_active[-3:], x_active[-1], deriv_order=2)
    A[-1, -3:] = beta2 * d2w + beta1 * d1w
    A[-1, -1] += beta0
    b[-1] = rhs[-1]

    
    dY_active = np.linalg.solve(A, b)
    if np.max(np.abs(dY_active)) > max_step_size:
        print(f"Step size limited to {max_step_size} m from: {np.max(np.abs(dY_active))} m.")
        dY_active *= max_step_size / np.max(np.abs(dY_active))


    # ------------------------------------------------------------------
    # Apply displacement only on active region
    # ------------------------------------------------------------------
    new_geometry = geom.copy()
    new_geometry[:n_active, 1] += dY_active - dY_active[0]  # shift to keep inlet point fixed

    # ------------------------------------------------------------------
    # Arc replacement from attachment point onward
    # ------------------------------------------------------------------
    if circle_section_x is not None:
        _p1 = x1, y1 = new_geometry[circle_section_idx]
        _p2 = x2, y2 = new_geometry[circle_section_idx - 1]
        _p3 = x3, y3 = new_geometry[circle_section_idx - 2]

        ypp0 = 2 * (
            (y3 - y1) / (x3 - x1)
            - (y2 - y1) / (x2 - x1)
        ) / (x3 - x2)
        
        circle_section_pts = poly4_segment(
            new_geometry[circle_section_idx],
            -(_p2 - _p1),
            [1, 0],
            ypp0,
            new_geometry[-1, 0],
            8
        )

        new_geometry = np.vstack((new_geometry[:circle_section_idx], circle_section_pts))

    # ------------------------------------------------------------------
    # Plots
    # ------------------------------------------------------------------
    if plot_path is not None:

        # make full-length arrays for plotting, NaN outside active solve region
        delta_plot = np.full_like(x_lin, np.nan, dtype=float)
        disp_plot = np.full_like(x_lin, np.nan, dtype=float)
        raw_delta_plot = np.full_like(x_lin, np.nan, dtype=float)

        raw_delta_plot[:n_active] = raw_delta[:n_active]
        delta_plot[:n_active] = delta_active
        disp_plot[:n_active] = dY_active
        save_plots(
            plot_path / "p_comp.png",
            {
                "p_current": (current_wss[:, 0], current_wss[:, 1]),
                "p_target": (target_wss[:, 0], target_wss[:, 1]),
            },
            circle_section_x_plot
        )
        save_plots(
            plot_path / "delta_p.png",
            {
                "Smoothed Ptar-Pcur": (x_lin, delta_plot), 
                "Raw Ptar-Pcur": (x_lin, raw_delta_plot)
            },
            circle_section_x_plot
        )
        save_plots(
            plot_path / "displacement.png",
            {"Displacement": (x_lin, disp_plot)},
            circle_section_x_plot
        )


    return new_geometry