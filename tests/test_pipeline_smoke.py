"""Pipeline için temel smoke testi."""
from pathlib import Path

import pandas as pd

from src.pipeline.config_builder import build_pipeline_config
from src.pipeline.pipeline import run_basic_pipeline


def _pick_example_csv() -> Path:
    candidates = [
        Path("example_logs/heading_demo.csv"),
        Path("example_logs/simulated_rotation.csv"),
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("Örnek CSV bulunamadı (heading_demo.csv veya simulated_rotation.csv).")


def test_pipeline_smoke_runs_and_returns_artifacts(tmp_path):
    """Pipeline temel akışı veriyle çalışmalı."""
    csv_path = _pick_example_csv()
    cfg = build_pipeline_config(input_path=csv_path)
    artifacts = run_basic_pipeline(cfg)

    assert artifacts.raw_df is not None
    assert not artifacts.synced_main_df.empty

    # Heading hesaplanabildiyse fused_heading dolu olmalı; kolon yoksa bu kısım atlanır.
    df = pd.read_csv(csv_path, nrows=1)
    required_heading_cols = {"mag_x", "mag_y", "mag_z", "accel_x", "accel_y", "accel_z", "gyro_z"}
    if required_heading_cols.issubset(df.columns):
        assert artifacts.fused_heading is not None
