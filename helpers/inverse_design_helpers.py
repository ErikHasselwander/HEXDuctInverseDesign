import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

def arc_segment(P0, t0, t1, x_target=0.0, n_points=100, eps=1e-12):
    P0 = np.asarray(P0, float)
    t0 = np.asarray(t0, float)
    t1 = np.asarray(t1, float)

    t0 /= np.linalg.norm(t0)
    t1 /= np.linalg.norm(t1)

    perp = lambda v: np.array([-v[1], v[0]])
    cross2 = lambda a, b: a[0] * b[1] - a[1] * b[0]

    n0 = perp(t0)
    n1 = perp(t1)

    denom = n0[0] - n1[0]
    if abs(denom) < eps:
        P1 = np.array([x_target, P0[1]])
        pts = np.linspace(P0, P1, n_points)
        return None, P1, pts

    # signed radius
    r = (x_target - P0[0]) / denom

    # center and endpoint
    C = P0 + r * n0
    P1 = C - r * n1

    # radius vectors
    v0 = P0 - C
    v1 = P1 - C

    # shortest signed angle from v0 to v1
    sweep = np.arctan2(cross2(v0, v1), np.dot(v0, v1))

    # choose the branch consistent with the direction of travel
    # r > 0 => CCW, r < 0 => CW
    if r > 0 and sweep < 0:
        sweep += 2 * np.pi
    elif r < 0 and sweep > 0:
        sweep -= 2 * np.pi

    s = np.linspace(0.0, 1.0, n_points)
    pts = np.array([
        C + np.cos(a * sweep) * v0 + np.sin(a * sweep) * perp(v0)
        for a in s
    ])

    # optional, just to kill floating point noise
    pts[0] = P0
    pts[-1] = P1

    return pts

def poly4_segment(P0, t0, t1, ypp0, x_target=0.0, n_points=100):
    P0 = np.asarray(P0, float)
    t0 = np.asarray(t0, float)
    t1 = np.asarray(t1, float)

    t0 /= np.linalg.norm(t0)
    t1 /= np.linalg.norm(t1)

    x0, y0 = P0
    x1 = float(x_target)
    dx = x1 - x0

    m0 = t0[1] / t0[0]
    m1 = t1[1] / t1[0]

    a0 = y0
    a1 = m0
    a2 = 0.5 * ypp0

    A = np.array([
        [3 * dx**2, 4 * dx**3],
        [6 * dx,    12 * dx**2]
    ])
    b = np.array([
        m1 - (a1 + 2 * a2 * dx),
        -2 * a2
    ])
    a3, a4 = np.linalg.solve(A, b)

    x = np.linspace(x0, x1, n_points)
    u = x - x0
    y = a0 + a1*u + a2*u**2 + a3*u**3 + a4*u**4
    pts = np.column_stack([x, y])

    P1 = pts[-1]
    coeffs = np.array([a4, a3, a2, a1, a0])  # y = a4*(x-x0)^4 + ... + a0

    pts[0] = P0
    pts[-1] = P1

    return pts

def largest_index_leq_xmax(x_lin, x_max):
    """
    Returns the largest index i such that x_lin[i] <= x_max.
    If all values are > x_max, returns -1.
    Assumes x_lin is sorted ascending.
    """
    return int(np.searchsorted(x_lin, x_max, side="right") - 1)

