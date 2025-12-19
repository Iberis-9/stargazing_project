from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import pandas as pd

# Generic helpers

def _is_table_json(x) -> bool:
    """
    NOAA SWPC 'products' JSON often looks like:
      [
        ["time_tag", "kp", ...],   <- header row
        ["2025-12-19 00:00:00", "3.67", ...],
        ...
      ]
    """
    return (
        isinstance(x, list)
        and len(x) > 1
        and isinstance(x[0], list)
        and all(isinstance(c, str) for c in x[0])
    )


def table_json_to_df(data) -> pd.DataFrame:
    """
    Convert NOAA SWPC table-style JSON (header row + rows) into a DataFrame.
    If the payload isn't in the expected format (e.g. API hiccup), return empty df.
    """
    if not _is_table_json(data):
        return pd.DataFrame()

    header = data[0]
    rows = data[1:]
    df = pd.DataFrame(rows, columns=header)

    # Try to parse any obvious time columns
    for col in df.columns:
        if "time" in col.lower() or col.lower().endswith("_tag"):
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

    return df



def _coerce_numeric(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _pick_col(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    """Pick first candidate that exists in df (case-insensitive match)."""
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None


# OVATION (aurora oval)

def ovation_to_df(ovation_json: dict) -> pd.DataFrame:
    """
    OVATION JSON commonly includes:
      - 'Forecast Time' (string)
      - 'Observation Time' (string) (sometimes)
      - 'coordinates': list of [lon, lat, value]
    Returns df with: time_utc, lon, lat, prob
    """
    coords = ovation_json.get("coordinates") or ovation_json.get("Coordinates")
    if not coords:
        return pd.DataFrame(columns=["time_utc", "lon", "lat", "prob"])

    df = pd.DataFrame(coords, columns=["lon", "lat", "prob"])
    df = _coerce_numeric(df, ["lon", "lat", "prob"])

    # Attach forecast time if available
    t = ovation_json.get("Forecast Time") or ovation_json.get("forecast_time") or ovation_json.get("time")
    time_utc = pd.to_datetime(t, errors="coerce", utc=True)
    df.insert(0, "time_utc", time_utc)

    # Clean
    df = df.dropna(subset=["lon", "lat", "prob"]).reset_index(drop=True)
    return df

# Kp forecast

def kp_forecast_to_df(kp_json: list) -> pd.DataFrame:
    """
    Parse NOAA planetary Kp forecast table JSON into a DataFrame.
    Keeps whatever columns NOAA provides; we only normalize:
      - time column
      - kp numeric
    """
    df = table_json_to_df(kp_json)

    # Find a time column
    time_col = _pick_col(df, ["time_tag", "time", "datetime", "timestamp"])
    if time_col and time_col != "time_utc":
        df = df.rename(columns={time_col: "time_utc"})
    if "time_utc" not in df.columns:
        df.insert(0, "time_utc", pd.NaT)

    # Find kp column
    kp_col = _pick_col(df, ["kp", "kp_index", "kp_value"])
    if kp_col and kp_col != "kp":
        df = df.rename(columns={kp_col: "kp"})

    df = _coerce_numeric(df, ["kp"])
    return df


def latest_kp(df_kp: pd.DataFrame) -> Optional[float]:
    """
    Return the most recent non-null Kp value from a kp forecast/obs dataframe.
    """
    if df_kp is None or df_kp.empty or "kp" not in df_kp.columns:
        return None

    tmp = df_kp.dropna(subset=["kp"]).copy()
    if tmp.empty:
        return None

    if "time_utc" in tmp.columns and pd.api.types.is_datetime64_any_dtype(tmp["time_utc"]):
        tmp = tmp.sort_values("time_utc")
    return float(tmp["kp"].iloc[-1])


# Solar wind (mag + plasma)

@dataclass
class SolarWindNow:
    time_utc: Optional[pd.Timestamp]
    bz_gsm: Optional[float]
    speed_kps: Optional[float]
    density_pcc: Optional[float]


def solar_wind_to_dfs(mag_json: list, plasma_json: list) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convert NOAA SWPC solar wind mag/plasma table JSON into dataframes.
    Returns (mag_df, plasma_df), with normalized time column name: time_utc
    """
    mag_df = table_json_to_df(mag_json)
    plasma_df = table_json_to_df(plasma_json)

    # Normalize time column name
    mag_time = _pick_col(mag_df, ["time_tag", "time", "timestamp"])
    plasma_time = _pick_col(plasma_df, ["time_tag", "time", "timestamp"])

    if mag_time and mag_time != "time_utc":
        mag_df = mag_df.rename(columns={mag_time: "time_utc"})
    if plasma_time and plasma_time != "time_utc":
        plasma_df = plasma_df.rename(columns={plasma_time: "time_utc"})

    # Coerce numeric for common columns (we'll detect actual names below too)
    if not mag_df.empty:
        mag_df = _coerce_numeric(mag_df, mag_df.columns)
    if not plasma_df.empty:
        plasma_df = _coerce_numeric(plasma_df, plasma_df.columns)

    return mag_df, plasma_df


def solar_wind_now(mag_df: pd.DataFrame, plasma_df: pd.DataFrame) -> SolarWindNow:
    """
    Extract a "latest snapshot" (Bz, speed, density) from the two dfs.
    This is robust to column name variations by using candidate lists.
    """
    # Candidate columns (NOAA uses variants across products)
    bz_candidates = ["bz_gsm", "bz", "bz_gse", "bz_bt", "bzgsm"]
    speed_candidates = ["speed", "proton_speed", "flow_speed", "v_sw", "vx"]
    dens_candidates = ["density", "proton_density", "np", "n_p", "dens"]

    bz_col = _pick_col(mag_df, bz_candidates) if mag_df is not None and not mag_df.empty else None
    sp_col = _pick_col(plasma_df, speed_candidates) if plasma_df is not None and not plasma_df.empty else None
    dn_col = _pick_col(plasma_df, dens_candidates) if plasma_df is not None and not plasma_df.empty else None

    # Sort by time if present
    def _latest_row(df: pd.DataFrame) -> pd.Series | None:
        if df is None or df.empty:
            return None
        if "time_utc" in df.columns and pd.api.types.is_datetime64_any_dtype(df["time_utc"]):
            df2 = df.dropna(subset=["time_utc"]).sort_values("time_utc")
            if not df2.empty:
                return df2.iloc[-1]
        return df.iloc[-1]

    mag_last = _latest_row(mag_df)
    plasma_last = _latest_row(plasma_df)

    t = None
    if plasma_last is not None and "time_utc" in plasma_last.index:
        t = plasma_last["time_utc"]
    elif mag_last is not None and "time_utc" in mag_last.index:
        t = mag_last["time_utc"]

    bz = float(mag_last[bz_col]) if (mag_last is not None and bz_col and pd.notna(mag_last[bz_col])) else None
    sp = float(plasma_last[sp_col]) if (plasma_last is not None and sp_col and pd.notna(plasma_last[sp_col])) else None
    dn = float(plasma_last[dn_col]) if (plasma_last is not None and dn_col and pd.notna(plasma_last[dn_col])) else None

    return SolarWindNow(time_utc=t, bz_gsm=bz, speed_kps=sp, density_pcc=dn)


# Convenience: full parse bundle

def parse_aurora_bundle(
    ovation_json: dict,
    kp_json: list,
    solar_wind_json: dict,
) -> dict:
    """
    Convenience function if you want one call in app.py:
    returns dict with:
      - ovation_df
      - kp_df
      - mag_df
      - plasma_df
      - solar_wind_now (dataclass)
      - kp_latest (float|None)
    """
    ov_df = ovation_to_df(ovation_json)
    kp_df = kp_forecast_to_df(kp_json)

    mag_json = solar_wind_json.get("mag", [])
    plasma_json = solar_wind_json.get("plasma", [])
    mag_df, plasma_df = solar_wind_to_dfs(mag_json, plasma_json)

    sw_now = solar_wind_now(mag_df, plasma_df)
    kp_now = latest_kp(kp_df)

    return {
        "ovation_df": ov_df,
        "kp_df": kp_df,
        "mag_df": mag_df,
        "plasma_df": plasma_df,
        "solar_wind_now": sw_now,
        "kp_latest": kp_now,
    }
