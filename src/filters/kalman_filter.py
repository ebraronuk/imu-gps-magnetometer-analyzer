"""Kalman filter skeleton for 1D signal smoothing."""
from typing import Tuple

import numpy as np
import pandas as pd


def kalman_1d(
    measurements: pd.Series,
    process_variance: float = 1e-3,
    measurement_variance: float = 1e-2,
) -> Tuple[pd.Series, pd.Series]:
    """
    Apply a simple 1D Kalman filter to a measurement series.

    Args:
        measurements: Input measurement series.
        process_variance: Process noise variance.
        measurement_variance: Measurement noise variance.

    Returns:
        Tuple of (filtered_series, variance_series).
    """
    n = len(measurements)
    filtered = np.zeros(n)
    variance = np.zeros(n)

    x_est = 0.0
    p_est = 1.0

    for i, z in enumerate(measurements):
        p_pred = p_est + process_variance
        k = p_pred / (p_pred + measurement_variance)
        x_est = x_est + k * (z - x_est)
        p_est = (1 - k) * p_pred
        filtered[i] = x_est
        variance[i] = p_est

    return pd.Series(filtered, index=measurements.index), pd.Series(variance, index=measurements.index)
