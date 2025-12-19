from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from data.dataframes.aurora_df import SolarWindNow

@dataclass
class AuroraResult:
    chance_0_100: float
    ovation_prob: Optional[float]
    kp: Optional[float]
    bz_gsm: Optional[float]
    speed: Optional[float]
    density: Optional[float]
    note: str

def _nearest_ovation_prob(ovation_df: pd.DataFrame, lat: float, lon: float) -> Optional[float]:
    """
    OVATION grid is a bunch of points with lon/lat/prob.
    We find the nearest point to the user location and return its probability.
    """
    if ovation_df is None or ovation_df.empty:
        return None

    df = ovation_df.dropna(subset=["lat", "lon", "prob"]).copy()
    if df.empty:
        return None

    # Handle lon wrap: convert both to [-180, 180]
    def wrap180(x):
        x = float(x)
        return ((x + 180.0) % 360.0) - 180.0

    lat0 = float(lat)
    lon0 = wrap180(lon)

    df["lon_w"] = df["lon"].map(wrap180)
    # Cheap distance metric (good enough for grid-nearest)
    df["d2"] = (df["lat"] - lat0) ** 2 + (df["lon_w"] - lon0) ** 2

    row = df.sort_values("d2").iloc[0]
    try:
        return float(row["prob"])
    except Exception:
        return None


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def compute_aurora_chance(
    lat: float,
    lon: float,
    ovation_df: pd.DataFrame,
    kp_latest: Optional[float],
    sw_now: SolarWindNow,
) -> AuroraResult:
    """
    Simple, interpretable score:
      - Base signal: OVATION probability at nearest grid point (0–100-ish)
      - Modulators:
          * Kp increases odds (especially >=5)
          * Bz southward (negative) boosts odds
          * Higher speed slightly boosts odds
    Output: chance_0_100 + a short note.
    """

    ov_prob = _nearest_ovation_prob(ovation_df, lat, lon)  # typically 0..100
    if ov_prob is None:
        return AuroraResult(
            chance_0_100=0.0,
            ovation_prob=None,
            kp=kp_latest,
            bz_gsm=sw_now.bz_gsm,
            speed=sw_now.speed_kps,
            density=sw_now.density_pcc,
            note="OVATION data unavailable right now.",
        )

    # Normalize base (cap to [0,100])
    base = max(0.0, min(100.0, float(ov_prob)))

    # Kp factor: mild boost above ~4, stronger above ~5–6
    kp = kp_latest
    if kp is None or not math.isfinite(kp):
        kp_factor = 1.0
    else:
        # centered ~4.5
        kp_factor = 0.85 + 0.35 * _sigmoid((kp - 4.5) * 1.2)  # ~0.9..1.2-ish

    # Bz factor: negative Bz is good (southward IMF)
    bz = sw_now.bz_gsm
    if bz is None or not math.isfinite(bz):
        bz_factor = 1.0
    else:
        # If bz = -10 -> boost, bz = +5 -> slight penalty
        bz_factor = 0.85 + 0.4 * _sigmoid((-bz - 2.0) / 3.0)  # ~0.9..1.2-ish

    # Speed factor: higher speed helps a bit
    speed = sw_now.speed_kps
    if speed is None or not math.isfinite(speed):
        sp_factor = 1.0
    else:
        # 350 km/s baseline, 600+ is better
        sp_factor = 0.90 + 0.25 * _sigmoid((speed - 420.0) / 80.0)  # ~0.95..1.15

    # Combine
    chance = base * kp_factor * bz_factor * sp_factor
    chance = max(0.0, min(100.0, chance))

    # Friendly note
    note_bits = []
    if kp is not None:
        note_bits.append(f"Kp {kp:.1f}")
    if bz is not None:
        note_bits.append(f"Bz {bz:.1f} nT")
    if speed is not None:
        note_bits.append(f"Speed {speed:.0f} km/s")

    if bz is not None and bz < -5:
        verdict = "Southward Bz — good conditions."
    elif bz is not None and bz > 2:
        verdict = "Northward Bz — harder to get aurora."
    else:
        verdict = "Mixed solar wind conditions."

    return AuroraResult(
        chance_0_100=float(chance),
        ovation_prob=float(base),
        kp=kp,
        bz_gsm=bz,
        speed=speed,
        density=sw_now.density_pcc,
        note=f"{verdict} ({', '.join(note_bits)})" if note_bits else verdict,
    )
