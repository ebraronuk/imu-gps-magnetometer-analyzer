"""Analysis pipeline coordinating load, calibration, sync, and downstream products."""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

from src.data_loaders.csv_loader import load_sensor_csv
from src.calibration.mag_ellipsoid_fit import apply_ellipsoid_calibration, fit_ellipsoid
from src.preprocessing.normalization import normalize_columns
from src.preprocessing.time_sync import synchronize_streams
from src.visualization.plot_fft import plot_fft_spectrum
from src.orientation.orientation_estimator import (
    compute_complementary_heading,
    compute_tilt_compensated_heading,
)


@dataclass
class PipelineConfig:
    """Temel analiz hattı konfigürasyonu."""

    input_path: Path
    time_column: str = "timestamp"
    resample_rate: str = "10ms"
    normalize: bool = True
    compute_fft: bool = True


@dataclass
class AnalysisArtifacts:
    """Analiz çıktılarının tutulduğu yapı."""

    raw_df: pd.DataFrame
    synced_main_df: pd.DataFrame
    normalized_df: pd.DataFrame
    synced_streams: Dict[str, pd.DataFrame]
    fft_figure: Optional[object]
    mag_heading: Optional[pd.Series] = None
    fused_heading: Optional[pd.Series] = None
    mag_center: Optional[np.ndarray] = None
    mag_transform_matrix: Optional[np.ndarray] = None
    mag_corrected_df: Optional[pd.DataFrame] = None


def run_basic_pipeline(config: PipelineConfig) -> AnalysisArtifacts:
    """
    Temel analizi çalıştırır: yükleme, opsiyonel normalizasyon, zaman hizalama, kalibrasyon ve opsiyonel FFT.

    Args:
        config: Analiz hattı konfigürasyonu.

    Returns:
        Hazırlanan veri çerçeveleri, hizalanmış akış ve opsiyonel FFT/başlık çıktıları.
    """
    # Ham veri yükleme
    raw_df = load_sensor_csv(config.input_path, time_column=config.time_column)

    mag_axes = ("mag_x", "mag_y", "mag_z")
    accel_axes = ("accel_x", "accel_y", "accel_z")

    mag_center: Optional[np.ndarray] = None
    mag_transform_matrix: Optional[np.ndarray] = None
    mag_corrected_df: Optional[pd.DataFrame] = None

    has_mag = set(mag_axes).issubset(set(raw_df.columns))
    if has_mag:
        mag_center, mag_transform_matrix = fit_ellipsoid(raw_df, mag_cols=mag_axes)
        mag_corrected_df = apply_ellipsoid_calibration(
            raw_df, center=mag_center, transform_matrix=mag_transform_matrix, mag_cols=mag_axes
        )

    # Analiz tabanı: kalibre edilmiş manyetometre varsa onu kullan
    analysis_base_df = mag_corrected_df if mag_corrected_df is not None else raw_df

    # Zaman hizalama: ana akış kalibre edilmiş (varsa) ve ham ölçekle
    streams = {"main": analysis_base_df}
    synced_streams = synchronize_streams(
        streams, time_column=config.time_column, resample_rate=config.resample_rate
    )
    synced_main_df = synced_streams["main"]

    # Opsiyonel z-score normalizasyon senkronize akış üzerinden (zaman kolonu hariç)
    normalized_df = (
        normalize_columns(synced_main_df, exclude_columns=[config.time_column])
        if config.normalize
        else synced_main_df.copy()
    )

    # FFT senkronize akıştan hesaplanır
    fft_figure = (
        plot_fft_spectrum(synced_main_df, time_column=config.time_column, show=False)
        if config.compute_fft
        else None
    )

    mag_heading = None
    fused_heading = None

    has_accel = set(accel_axes).issubset(set(synced_main_df.columns))
    has_gyro = "gyro_z" in synced_main_df.columns

    if has_mag and has_accel:
        mag_heading = compute_tilt_compensated_heading(
            synced_main_df,
            mag_cols=mag_axes,
            accel_cols=accel_axes,
            corrected_mag_df=synced_main_df if mag_center is not None else None,
        )
        if has_gyro:
            fused_heading = compute_complementary_heading(
                gyro_df=synced_main_df,
                mag_heading_series=mag_heading,
                time_column=config.time_column,
            )

    return AnalysisArtifacts(
        raw_df=raw_df,
        synced_main_df=synced_main_df,
        normalized_df=normalized_df,
        synced_streams=synced_streams,
        fft_figure=fft_figure,
        mag_heading=mag_heading,
        fused_heading=fused_heading,
        mag_center=mag_center,
        mag_transform_matrix=mag_transform_matrix,
        mag_corrected_df=synced_main_df if mag_center is not None else None,
    )
