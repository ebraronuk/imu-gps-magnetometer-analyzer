"""FFT spectrum plotting using Plotly."""
from typing import Iterable, Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go


def compute_fft(df: pd.DataFrame, time_column: str, value_columns: Iterable[str]) -> pd.DataFrame:
    """
    Compute FFT magnitude for selected columns.

    Args:
        df: Input DataFrame.
        time_column: Timestamp column for sampling interval.
        value_columns: Columns to transform.

    Returns:
        DataFrame with frequency and magnitude for each column.
    """
    if len(df) < 2:
        raise ValueError("Not enough samples for FFT")

    dt = (df[time_column].iloc[1] - df[time_column].iloc[0]).total_seconds()
    freqs = np.fft.rfftfreq(len(df), dt)
    spectra = {"frequency": freqs}
    for col in value_columns:
        spectra[col] = np.abs(np.fft.rfft(df[col].to_numpy()))
    return pd.DataFrame(spectra)


def plot_fft_spectrum(
    df: pd.DataFrame,
    time_column: str = "timestamp",
    value_columns: Optional[Iterable[str]] = None,
    show: bool = False,
):
    """
    Plot FFT magnitude for numeric columns.

    Args:
        df: Input DataFrame.
        time_column: Timestamp column.
        value_columns: Columns to include; defaults to numeric columns.
        show: Whether to immediately display.

    Returns:
        Plotly Figure.
    """
    numeric_cols = df.select_dtypes(include=["number"]).columns
    cols = list(value_columns) if value_columns is not None else list(numeric_cols)
    fft_df = compute_fft(df, time_column, cols)

    fig = go.Figure()
    for col in cols:
        fig.add_trace(
            go.Scatter(x=fft_df["frequency"], y=fft_df[col], mode="lines", name=col)
        )
    fig.update_layout(title="FFT Spectrum", xaxis_title="Frequency (Hz)", yaxis_title="Magnitude")
    if show:
        fig.show()
    return fig
