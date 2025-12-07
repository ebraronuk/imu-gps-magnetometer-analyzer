"""Orientation and heading estimation utilities."""
import numpy as np
import pandas as pd


def compute_tilt_compensated_heading(
    df: pd.DataFrame,
    mag_cols=("mag_x", "mag_y", "mag_z"),
    accel_cols=("accel_x", "accel_y", "accel_z"),
    corrected_mag_df: pd.DataFrame | None = None,
    eps: float = 1e-6,
):
    """
    Compute tilt-compensated magnetic heading using accelerometer roll/pitch.

    Tercihen kalibre edilmiş manyetometre vektörleri kullanılır; yoksa ham veriye düşer.
    Vektörler normalize edilir, roll/pitch hesaplarında küçük epsilon ile bölme hataları engellenir.

    Args:
        df: Base DataFrame with time and sensor data.
        mag_cols: Magnetometer axis columns.
        accel_cols: Accelerometer axis columns.
        corrected_mag_df: Optional calibrated magnetometer DataFrame aligned to df.
        eps: Small guard to prevent division blow-up.

    Returns:
        Heading series in degrees aligned to df index, NaN-safe.
    """
    mag_source = corrected_mag_df if corrected_mag_df is not None else df

    missing_mag = set(mag_cols) - set(mag_source.columns)
    missing_accel = set(accel_cols) - set(df.columns)
    if missing_mag:
        raise ValueError(f"Magnetometer columns missing: {missing_mag}")
    if missing_accel:
        raise ValueError(f"Accelerometer columns missing: {missing_accel}")

    mx, my, mz = (mag_source[col].astype(float).to_numpy() for col in mag_cols)
    ax, ay, az = (df[col].astype(float).to_numpy() for col in accel_cols)

    # Roll/pitch ivmeden; epsilon ile sıfıra yaklaşan eksenler korunur
    az_safe = np.where(np.abs(az) < eps, eps, az)
    roll = np.arctan2(ay, az_safe)
    denom_pitch = np.sqrt(ay ** 2 + az_safe ** 2)
    denom_pitch = np.where(denom_pitch < eps, eps, denom_pitch)
    pitch = np.arctan2(-ax, denom_pitch)

    # Manyetik vektörü normalize et; sıfır normlar NaN olarak işlenir
    mag_norm = np.linalg.norm(np.vstack((mx, my, mz)).T, axis=1)
    mag_norm = np.where(mag_norm < eps, np.nan, mag_norm)
    mx_n = mx / mag_norm
    my_n = my / mag_norm
    mz_n = mz / mag_norm

    # Roll/pitch telafisi sonrası yatay düzlem projeksiyonu
    xh = mx_n * np.cos(pitch) + mz_n * np.sin(pitch)
    yh = mx_n * np.sin(roll) * np.sin(pitch) + my_n * np.cos(roll) - mz_n * np.sin(roll) * np.cos(pitch)

    heading_rad = np.arctan2(yh, xh)
    heading_deg = (np.degrees(heading_rad) + 360.0) % 360.0
    heading_series = pd.Series(heading_deg, index=df.index)
    return heading_series


def compute_complementary_heading(
    gyro_df: pd.DataFrame,
    mag_heading_series: pd.Series,
    time_column: str = "timestamp",
    alpha: float = 0.98,
) -> pd.Series:
    """
    Fuse gyro yaw rate with magnetic heading via complementary filter.

    Gyro entegrasyonu manyetik başlık ile tohumlanır, açılar unwrap edilip sürekli alan üzerinde harmanlanır.

    Args:
        gyro_df: DataFrame containing gyro_z and time.
        mag_heading_series: Tilt-compensated magnetic heading in degrees.
        time_column: Timestamp column name.
        alpha: Gyro weight (1-alpha is magnetic weight).

    Returns:
        Fused heading in degrees wrapped to [0, 360).
    """
    if time_column not in gyro_df.columns:
        raise ValueError(f"Missing time column '{time_column}' in gyro data")
    if "gyro_z" not in gyro_df.columns:
        raise ValueError("Missing required gyro_z column for yaw rate integration")

    timestamps = pd.to_datetime(gyro_df[time_column], errors="coerce")
    if timestamps.isna().any():
        raise ValueError("Timestamp parsing failed for gyro data")

    mag_aligned = mag_heading_series.reindex(gyro_df.index).ffill().bfill()
    mag_rad = np.deg2rad(mag_aligned.to_numpy())
    mag_unwrapped = np.unwrap(mag_rad)

    yaw_rate = gyro_df["gyro_z"].astype(float).to_numpy()  # assumed rad/s
    dt = timestamps.diff().dt.total_seconds().fillna(0.0).to_numpy()

    gyro_integrated = np.zeros_like(yaw_rate)
    for i in range(1, len(gyro_integrated)):
        gyro_integrated[i] = gyro_integrated[i - 1] + yaw_rate[i] * dt[i]
    gyro_unwrapped = np.unwrap(mag_unwrapped[0] + gyro_integrated)

    fused = alpha * gyro_unwrapped + (1.0 - alpha) * mag_unwrapped
    fused_deg = (np.degrees(fused) + 360.0) % 360.0
    return pd.Series(fused_deg, index=gyro_df.index)
