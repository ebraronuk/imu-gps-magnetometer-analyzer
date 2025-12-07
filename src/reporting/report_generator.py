"""HTML report generator for analysis outputs."""
from typing import Optional

import pandas as pd
import plotly.io as pio


def build_basic_report(
    raw: pd.DataFrame,
    normalized: pd.DataFrame,
    fft_fig: Optional[object],
    time_column: str = "timestamp",
) -> str:
    """
    Build a minimal HTML report embedding plots and statistics.

    Args:
        raw: Raw DataFrame.
        normalized: Normalized DataFrame.
        fft_fig: Optional Plotly FFT figure.
        time_column: Timestamp column name.

    Returns:
        HTML string.
    """
    summary_html = raw.describe().to_html()
    fft_html = pio.to_html(fft_fig, full_html=False) if fft_fig else "<p>No FFT computed.</p>"

    html = f"""
    <html>
    <head>
        <title>Sensor Log Report</title>
    </head>
    <body>
        <h1>Sensor Log Report</h1>
        <h2>Raw Data Summary</h2>
        {summary_html}
        <h2>FFT Spectrum</h2>
        {fft_html}
    </body>
    </html>
    """
    return html
