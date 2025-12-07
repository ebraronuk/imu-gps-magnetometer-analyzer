"""Placeholder test module."""
import pandas as pd

from src.preprocessing.normalization import normalize_columns


def test_normalize_columns_no_error():
    """Ensure normalization runs without errors on simple data."""
    df = pd.DataFrame(
        {"timestamp": pd.date_range("2024-01-01", periods=3, freq="S"), "a": [1, 2, 3]}
    )
    result = normalize_columns(df, exclude_columns=["timestamp"])
    assert "a" in result.columns
