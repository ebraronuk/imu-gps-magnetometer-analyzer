"""Timeseries plotting using Plotly."""
from typing import Iterable, Optional

import pandas as pd
import plotly.express as px


def plot_timeseries(
    df: pd.DataFrame,
    time_column: str = "timestamp",
    value_columns: Optional[Iterable[str]] = None,
    show: bool = False,
):
    """
    Render interactive timeseries plot.

    Args:
        df: Input DataFrame.
        time_column: Timestamp column.
        value_columns: Columns to plot; defaults to all numeric columns.
        show: Whether to immediately display the plot.

    Returns:
        Plotly Figure.
    """
    cols = value_columns or df.select_dtypes(include=["number"]).columns
    fig = px.line(df, x=time_column, y=cols, title="Timeseries")
    if show:
        fig.show()
    return fig
