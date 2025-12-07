"""IMU bias estimation utilities for accelerometer and gyroscope."""
from typing import Iterable, Tuple

import numpy as np
import pandas as pd


def estimate_bias(
    df: pd.DataFrame,
    columns: Iterable[str],
    steady_state_slice: slice = slice(0, 500),
) -> Tuple[np.ndarray, float]:
    """
    Estimate bias as mean over a steady-state window.

    Args:
        df: Input DataFrame.
        columns: Iterable of column names to estimate bias for.
        steady_state_slice: Slice indicating steady region.

    Returns:
        Tuple of (bias_vector, window_duration_seconds).
    """
    cols = list(columns)
    missing = set(cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing IMU columns: {missing}")

    window = df.iloc[steady_state_slice]
    bias = window[cols].mean(axis=0).to_numpy()
    duration = len(window)
    return bias, float(duration)


def remove_bias(df: pd.DataFrame, columns: Iterable[str], bias: np.ndarray) -> pd.DataFrame:
    """
    Subtract bias from specified columns.

    Args:
        df: Input DataFrame.
        columns: Columns to correct.
        bias: Bias vector.

    Returns:
        Corrected DataFrame.
    """
    corrected = df.copy()
    for idx, col in enumerate(columns):
        corrected[col] = df[col] - bias[idx]
    return corrected
