"""Time synchronization utilities for multi-sensor streams."""
from typing import Dict

import pandas as pd


def synchronize_streams(
    streams: Dict[str, pd.DataFrame],
    time_column: str = "timestamp",
    resample_rate: str = "10ms",
) -> Dict[str, pd.DataFrame]:
    """
    Resample and forward-fill multiple sensor streams to a common time grid.

    Args:
        streams: Mapping of stream name to DataFrame.
        time_column: Column holding timestamp values.
        resample_rate: Pandas offset alias for resampling interval.

    Returns:
        Mapping of stream name to synchronized DataFrame.
    """
    synced = {}
    for name, df in streams.items():
        if time_column not in df.columns:
            raise ValueError(f"Stream '{name}' missing time column '{time_column}'")
        indexed = df.set_index(time_column).sort_index()
        resampled = indexed.resample(resample_rate).mean().ffill()
        resampled.reset_index(inplace=True)
        synced[name] = resampled
    return synced
