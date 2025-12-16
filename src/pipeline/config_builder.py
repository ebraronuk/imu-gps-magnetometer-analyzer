"""PipelineConfig üretimi ve giriş doğrulaması."""
from pathlib import Path
from typing import Iterable, Set

import pandas as pd

from src.pipeline.pipeline import PipelineConfig

SENSOR_COLUMNS: Set[str] = {
    "accel_x",
    "accel_y",
    "accel_z",
    "mag_x",
    "mag_y",
    "mag_z",
    "gyro_x",
    "gyro_y",
    "gyro_z",
}


def _validate_input(path: Path, time_column: str, required_any: Iterable[str]) -> None:
    """CSV dosyasını ve kolon varlığını kontrol eder."""
    if not path.exists():
        raise FileNotFoundError("CSV dosyası bulunamadı.")
    sample = pd.read_csv(path, nrows=1)
    if time_column not in sample.columns:
        raise ValueError(f"Zaman kolonu eksik: {time_column}")
    if not set(sample.columns).intersection(set(required_any)):
        raise ValueError("Sensör kolonu bulunamadı (accel/mag/gyro bekleniyor).")


def build_pipeline_config(
    input_path: Path,
    time_column: str = "timestamp",
    resample_rate: str = "10ms",
    normalize: bool = True,
    compute_fft: bool = True,
) -> PipelineConfig:
    """Doğrulama sonrası PipelineConfig üretir."""
    _validate_input(input_path, time_column=time_column, required_any=SENSOR_COLUMNS)
    return PipelineConfig(
        input_path=input_path,
        time_column=time_column,
        resample_rate=resample_rate,
        normalize=normalize,
        compute_fft=compute_fft,
    )
