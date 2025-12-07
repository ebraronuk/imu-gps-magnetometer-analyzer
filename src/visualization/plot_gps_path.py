"""GPS path plotting using Plotly."""
from typing import Optional

import pandas as pd
import plotly.express as px


def plot_gps_path(
    df: pd.DataFrame,
    lat_col: str = "lat",
    lon_col: str = "lon",
    color_col: Optional[str] = None,
    show: bool = False,
):
    """
    Plot GPS path as a 2D trajectory.

    Args:
        df: Input DataFrame.
        lat_col: Latitude column.
        lon_col: Longitude column.
        color_col: Optional column to color by (e.g., speed).
        show: Whether to immediately display.

    Returns:
        Plotly Figure.
    """
    fig = px.line_geo(df, lat=lat_col, lon=lon_col, color=color_col, title="GPS Path")
    if show:
        fig.show()
    return fig
