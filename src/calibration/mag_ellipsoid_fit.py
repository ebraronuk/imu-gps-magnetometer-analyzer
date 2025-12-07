"""Magnetometer ellipsoid fitting and calibration helpers."""
import numpy as np
import pandas as pd


def fit_ellipsoid(df: pd.DataFrame, mag_cols=("mag_x", "mag_y", "mag_z")):
    """
    Fit an ellipsoid to raw magnetometer samples.

    Hard-iron bias is the ellipsoid center; soft-iron scale/shear is captured by a 3x3 transform.
    Returns None values when data is insufficient or ill-conditioned to avoid unsafe calibration.

    Args:
        df: DataFrame containing magnetometer samples.
        mag_cols: Column names for magnetometer axes.

    Returns:
        center: Hard-iron bias vector or None.
        transform_matrix: Soft-iron inverse square-root matrix or None.
    """
    min_samples = 50
    missing = set(mag_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing magnetometer columns for ellipsoid fit: {missing}")
    if len(df) < min_samples:
        return None, None

    x, y, z = (df[col].astype(float).to_numpy() for col in mag_cols)

    # Quadratic form: v^T A v + 2 b^T v + c = 0
    D = np.column_stack(
        [
            x ** 2,
            y ** 2,
            z ** 2,
            2 * x * y,
            2 * x * z,
            2 * y * z,
            2 * x,
            2 * y,
            2 * z,
            np.ones_like(x),
        ]
    )

    # Least squares solution for full quadratic including constant term
    beta, *_ = np.linalg.lstsq(D, np.ones_like(x), rcond=None)

    A = np.array(
        [
            [beta[0], beta[3], beta[4]],
            [beta[3], beta[1], beta[5]],
            [beta[4], beta[5], beta[2]],
        ]
    )
    b = np.array([beta[6], beta[7], beta[8]])
    c = beta[9]

    A_inv = np.linalg.pinv(A)
    center = -A_inv.dot(b)

    offset_term = 1.0 + center.T @ A @ center - c
    if offset_term == 0:
        return None, None

    A_norm = A / offset_term

    # Enforce PSD to stabilize soft-iron correction
    eigvals, eigvecs = np.linalg.eigh(A_norm)
    eigvals_clipped = np.clip(eigvals, a_min=1e-9, a_max=None)
    A_psd = eigvecs @ np.diag(eigvals_clipped) @ eigvecs.T

    transform_inv_sqrt = eigvecs @ np.diag(1.0 / np.sqrt(eigvals_clipped)) @ eigvecs.T

    cond_number = np.linalg.cond(transform_inv_sqrt)
    if cond_number > 1e6:
        return None, None

    shifted = (np.vstack((x, y, z)).T - center) @ transform_inv_sqrt.T
    norms = np.linalg.norm(shifted, axis=1)
    scale = np.median(norms)
    scale = 1.0 if scale == 0 or np.isnan(scale) else scale
    transform_matrix = transform_inv_sqrt / scale

    return center, transform_matrix


def apply_ellipsoid_calibration(
    df: pd.DataFrame,
    center: np.ndarray,
    transform_matrix: np.ndarray,
    mag_cols=("mag_x", "mag_y", "mag_z"),
) -> pd.DataFrame:
    """
    Apply ellipsoid calibration: remove hard-iron bias, correct soft-iron distortion.

    Args:
        df: DataFrame with magnetometer measurements.
        center: Hard-iron bias vector.
        transform_matrix: Soft-iron inverse square-root matrix.
        mag_cols: Magnetometer axis column names.

    Returns:
        Copy of DataFrame with calibrated magnetometer columns.
    """
    missing = set(mag_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing magnetometer columns for calibration: {missing}")
    if center is None or transform_matrix is None:
        return df.copy()

    corrected = df.copy()
    raw_vecs = corrected.loc[:, mag_cols].to_numpy(dtype=float)

    shifted = raw_vecs - center
    corrected_vecs = (transform_matrix @ shifted.T).T

    norms = np.linalg.norm(corrected_vecs, axis=1)
    median_norm = np.median(norms) if len(norms) else 1.0
    if median_norm and not np.isnan(median_norm):
        corrected_vecs /= median_norm

    for idx, col in enumerate(mag_cols):
        corrected[col] = corrected_vecs[:, idx]

    return corrected
