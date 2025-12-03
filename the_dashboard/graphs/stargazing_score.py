# graphs/stargazing_score.py

import pandas as pd
import altair as alt
import streamlit as st


def compute_stargazing_score(night_df: pd.DataFrame, astro_info: dict) -> pd.DataFrame:
    """
    Compute a 0–100 stargazing score for each night-time hour.

    night_df must have columns:
      - datetime
      - cloud_cover (0–100)
      - visibility_km
      - humidity (0–100)

    astro_info must contain:
      - "moon_illumination" (string or number, 0–100)
    """
    if night_df is None or night_df.empty:
        return pd.DataFrame(columns=["datetime", "score"])

    df = night_df.copy()

    # Make sure required columns exist
    required_cols = ["datetime", "cloud_cover", "visibility_km", "humidity"]
    if not all(col in df.columns for col in required_cols):
        return pd.DataFrame(columns=["datetime", "score"])

    # Normalise inputs
    # Clouds: 0 (no clouds) -> best, 100 -> worst
    df["cloud_norm"] = 1 - (df["cloud_cover"].clip(0, 100) / 100.0)

    # Visibility: scale to [0,1] using max visibility for that night
    max_vis = df["visibility_km"].max()
    if pd.isna(max_vis) or max_vis <= 0:
        df["vis_norm"] = 0.0
    else:
        df["vis_norm"] = (df["visibility_km"] / max_vis).clip(0, 1)

    # Humidity: 0 -> best, 100 -> worst
    df["hum_norm"] = 1 - (df["humidity"].clip(0, 100) / 100.0)

    # Moon illumination from astro_info (string like "57" or "57%")
    moon_raw = astro_info.get("moon_illumination", 50)
    try:
        moon_val = float(str(moon_raw).replace("%", ""))
    except ValueError:
        moon_val = 50.0

    moon_norm = 1 - (max(min(moon_val, 100), 0) / 100.0)  # 1 = dark, 0 = full moon

    # Weights: clouds (40%), visibility (30%), humidity (15%), moon (15%)
    w_cloud = 0.4
    w_vis = 0.3
    w_hum = 0.15
    w_moon = 0.15

    df["score_raw"] = (
        df["cloud_norm"] * w_cloud
        + df["vis_norm"] * w_vis
        + df["hum_norm"] * w_hum
        + moon_norm * w_moon
    )

    # Scale to 0–100 and clip
    df["score"] = (df["score_raw"] * 100).clip(0, 100)

    return df[["datetime", "score"]]


def plot_stargazing_score(score_df: pd.DataFrame, location_name: str):
    if score_df is None or score_df.empty:
        st.info("No stargazing score available for tonight.")
        return

    df = score_df.copy()
    df["time"] = df["datetime"].dt.strftime("%H:%M")

    chart = (
        alt.Chart(df)
        .mark_line(strokeWidth=2, opacity=0.9, color = "#E27ECF")
        .encode(
            x=alt.X("datetime:T", title="Time"),
            y=alt.Y("score:Q", title="Stargazing score (0–100)", scale=alt.Scale(domain=[0, 100])),
            tooltip=["time", "score"],
        )        ).properties(
            width = 1300, 
            height = 360,
            padding={"top": 30, "right": 20, "bottom": 5, "left": 5}
    ).configure_view( stroke=None)
    
    st.altair_chart(chart, use_container_width=False)

