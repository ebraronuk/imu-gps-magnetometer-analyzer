"""Manyetometre + IMU simülasyon üreticisi."""
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


def _rotation_matrix(yaw: np.ndarray, pitch: np.ndarray, roll: np.ndarray) -> np.ndarray:
    """Z-Y-X rotasyon matrislerini vektörize üretir."""
    cy, sy = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cr, sr = np.cos(roll), np.sin(roll)

    R = np.empty((len(yaw), 3, 3))
    R[:, 0, 0] = cy * cp
    R[:, 0, 1] = cy * sp * sr - sy * cr
    R[:, 0, 2] = cy * sp * cr + sy * sr
    R[:, 1, 0] = sy * cp
    R[:, 1, 1] = sy * sp * sr + cy * cr
    R[:, 1, 2] = sy * sp * cr - cy * sr
    R[:, 2, 0] = -sp
    R[:, 2, 1] = cp * sr
    R[:, 2, 2] = cp * cr
    return R


def _soft_iron_matrix(rng: np.random.Generator) -> np.ndarray:
    """Simetrik pozitif tanımlı soft-iron matrisi üretir."""
    m = rng.normal(scale=0.2, size=(3, 3))
    sym = m @ m.T
    return np.eye(3) + 0.3 * sym


def generate_simulated_rotation(
    out_path: Path,
    samples: int = 800,
    dt: float = 0.02,
    seed: int = 42,
    field_vector: Tuple[float, float, float] = (20.0, 5.0, 45.0),
) -> pd.DataFrame:
    """
    Gerçekçi manyetometre + IMU hareket verisi üretir ve diske yazar.

    Args:
        out_path: Çıkış CSV yolu.
        samples: Örnek sayısı (>=500 önerilir).
        dt: Örnekleme aralığı (s).
        seed: Rastgelelik tekrarlanabilirliği için tohum.
        field_vector: Dünya manyetik alanı (uT).

    Returns:
        Üretilen veri çerçevesi.
    """
    rng = np.random.default_rng(seed)

    t = np.arange(samples) * dt
    timestamps = pd.to_datetime("2024-01-01") + pd.to_timedelta(t, unit="s")

    # Yaw/pitch/roll akıcı değişim: yaw tam tur, pitch/roll sinüzoid
    yaw = np.linspace(0, 2 * np.pi, samples)
    pitch = 0.25 * np.sin(np.linspace(0, 4 * np.pi, samples))
    roll = 0.2 * np.sin(np.linspace(0, 3 * np.pi, samples) + 0.5)

    # Gyro yaw hızı (rad/s) + küçük gürültü
    yaw_rate = np.gradient(yaw, dt) + rng.normal(scale=0.002, size=samples)

    R = _rotation_matrix(yaw, pitch, roll)  # shape (N,3,3)

    field_world = np.array(field_vector)  # uT
    # Dünya alanını gövdeye döndür (body = R^T * world)
    mag_body = np.einsum("nij,j->ni", R.transpose(0, 2, 1), field_world)

    # Soft-iron ve hard-iron uygulaması
    hard_bias = rng.normal(scale=2.0, size=3)
    soft_matrix = _soft_iron_matrix(rng)
    mag_distorted = (soft_matrix @ (mag_body + hard_bias).T).T
    mag_noisy = mag_distorted + rng.normal(scale=0.15, size=mag_distorted.shape)

    # İvme: sadece yerçekimi gövdede, küçük gürültü + hafif doğrusal ivme
    g_world = np.array([0.0, 0.0, 9.81])
    accel_body = np.einsum("nij,j->ni", R.transpose(0, 2, 1), g_world)
    linear_accel = 0.1 * np.sin(2 * np.pi * t / t[-1])[:, None] * np.array([0.5, 0.2, 0.1])
    accel_body = accel_body + linear_accel + rng.normal(scale=0.03, size=accel_body.shape)

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "accel_x": accel_body[:, 0],
            "accel_y": accel_body[:, 1],
            "accel_z": accel_body[:, 2],
            "mag_x": mag_noisy[:, 0],
            "mag_y": mag_noisy[:, 1],
            "mag_z": mag_noisy[:, 2],
            "gyro_z": yaw_rate,
        }
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return df
