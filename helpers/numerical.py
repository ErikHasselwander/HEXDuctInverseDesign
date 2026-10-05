import math
import numpy as np

def fd_weights(x_stencil, x0, deriv_order):
    """
    Finite-difference weights from local polynomial interpolation.
    Works for arbitrary nonuniform small stencils.
    """
    n = len(x_stencil)
    A = np.zeros((n, n), dtype=float)
    dx = x_stencil - x0

    for row in range(n):
        A[row, :] = dx**row / math.factorial(row)

    b = np.zeros(n, dtype=float)
    b[deriv_order] = 1.0
    return np.linalg.solve(A, b)

def gaussian_kernel_smooth(x, y, sigma0=None):
    x = np.asarray(x)
    y = np.asarray(y)

    if sigma0 is None:
        sigma0 = np.median(np.diff(x))

    y_smooth = np.empty_like(y)

    x0 = x.min()
    x1 = x.min() + 0.5 * (x.max() - x.min())

    for i in range(len(x)):
        if x[i] <= x1:
            t = (x[i] - x0) / (x1 - x0)  # t ∈ [0, 1]
            sigma = sigma0 * (5 - 4 * t)
        else:
            sigma = sigma0

        dx = x - x[i]
        w = np.exp(-(dx**2) / (2 * sigma**2))
        y_smooth[i] = np.sum(w * y) / np.sum(w)

    return y_smooth
