"""FIR/IIR filter helpers using SciPy."""
import numpy as np
from scipy import signal


def design_lowpass_fir(
    cutoff_hz: float,
    fs: float,
    numtaps: int = 101,
    window: str = "hamming",
) -> np.ndarray:
    """
    Design a lowpass FIR filter.

    Args:
        cutoff_hz: Cutoff frequency in Hz.
        fs: Sampling frequency in Hz.
        numtaps: Number of filter taps.
        window: Window type.

    Returns:
        FIR coefficients.
    """
    return signal.firwin(numtaps, cutoff_hz, fs=fs, window=window)


def apply_filter(coeffs: np.ndarray, data: np.ndarray) -> np.ndarray:
    """
    Apply FIR filter coefficients to data.

    Args:
        coeffs: FIR coefficients.
        data: Input data array.

    Returns:
        Filtered data array.
    """
    return signal.lfilter(coeffs, 1.0, data)
