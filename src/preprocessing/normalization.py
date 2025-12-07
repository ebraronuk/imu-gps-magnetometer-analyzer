"""Normalization helpers for sensor channels."""
from typing import Iterable, List, Optional

import pandas as pd


def normalize_columns(
    df: pd.DataFrame,
    exclude_columns: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    Apply z-score normalization to numeric columns, excluding specified columns.

    Args:
        df: Input DataFrame.
        exclude_columns: Columns to skip normalization.

    Returns:
        DataFrame with normalized numeric columns.
    """
    exclude = set(exclude_columns or [])
    numeric_cols: List[str] = [
        col for col in df.select_dtypes(include=["number"]).columns if col not in exclude
    ]
    normalized = df.copy()
    for col in numeric_cols:
        std = df[col].std()
        if std == 0 or pd.isna(std):
            continue
        normalized[col] = (df[col] - df[col].mean()) / std
    return normalized
