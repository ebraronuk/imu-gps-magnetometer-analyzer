"""CSV loader for sensor log ingestion."""
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd


def load_sensor_csv(
    path: Path,
    time_column: str = "timestamp",
    required_columns: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    Load a sensor CSV file with minimal validation.

    Args:
        path: Path to CSV file.
        time_column: Name of the timestamp column.
        required_columns: Optional iterable of required column names.

    Returns:
        Pandas DataFrame with parsed timestamps.
    """
    df = pd.read_csv(path)
    if time_column not in df.columns:
        raise ValueError(f"Missing required time column '{time_column}' in {path}")

    if required_columns:
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns {missing} in {path}")

    df[time_column] = pd.to_datetime(df[time_column], errors="coerce")
    if df[time_column].isna().any():
        raise ValueError(f"Failed to parse some timestamps in '{time_column}'")

    return df
