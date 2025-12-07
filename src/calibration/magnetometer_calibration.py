"""Magnetometer calibration scaffold (hard-iron/soft-iron)."""
from typing import Tuple

import numpy as np
import pandas as pd


def estimate_hard_soft_iron_bias(
    df: pd.DataFrame,
    mag_columns: Tuple[str, str, str] = ("mag_x", "mag_y", "mag_z"),
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Estimate hard-iron bias (offset) and soft-iron scale using a simple heuristic.

    Args:
        df: Input DataFrame with magnetometer axes.
        mag_columns: Column names for x, y, z axes.

    Returns:
        Tuple of (bias_vector, scale_vector).
    """
    missing = set(mag_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing magnetometer columns: {missing}")

    mags = df.loc[:, mag_columns].to_numpy()
    bias = mags.mean(axis=0)
    span = mags.max(axis=0) - mags.min(axis=0)
    scale = span / np.max(span)
    return bias, scale


def apply_magnetometer_calibration(
    df: pd.DataFrame,
    bias: np.ndarray,
    scale: np.ndarray,
    mag_columns: Tuple[str, str, str] = ("mag_x", "mag_y", "mag_z"),
) -> pd.DataFrame:
    """
    Apply bias and scale correction to magnetometer data.

    Args:
        df: Input DataFrame.
        bias: Hard-iron bias vector.
        scale: Soft-iron scale vector.
        mag_columns: Column names for x, y, z axes.

    Returns:
        Corrected DataFrame.
    """
    corrected = df.copy()
    for i, col in enumerate(mag_columns):
        corrected[col] = (df[col] - bias[i]) / scale[i]
    return corrected
