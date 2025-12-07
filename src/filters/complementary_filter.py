"""Complementary filter scaffold for attitude estimation."""
import pandas as pd


def complementary_filter(
    gyro_df: pd.DataFrame,
    accel_df: pd.DataFrame,
    time_column: str = "timestamp",
    alpha: float = 0.98,
) -> pd.DataFrame:
    """
    Fuse gyro and accelerometer data using a complementary filter.

    Args:
        gyro_df: Gyroscope DataFrame with angular rates.
        accel_df: Accelerometer DataFrame with linear acceleration.
        time_column: Timestamp column.
        alpha: Filter blending factor.

    Returns:
        DataFrame with fused orientation estimates.
    """
    fused = pd.DataFrame()
    fused[time_column] = gyro_df[time_column]
    fused["roll"] = alpha * gyro_df.get("gyro_x", 0) + (1 - alpha) * accel_df.get("accel_x", 0)
    fused["pitch"] = alpha * gyro_df.get("gyro_y", 0) + (1 - alpha) * accel_df.get("accel_y", 0)
    fused["yaw"] = alpha * gyro_df.get("gyro_z", 0) + (1 - alpha) * accel_df.get("accel_z", 0)
    return fused
