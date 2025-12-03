
import streamlit as st
import altair as alt
import pandas as pd


def neo_summary_metrics(neo_df: pd.DataFrame) -> None:
    """Show small KPI-style metrics for today's NEOs."""
    if neo_df is None or neo_df.empty:
        st.info("No near-Earth objects available for today.")
        return

    total = len(neo_df)

    # closest object (by miss_distance_lunar)
    closest_name = "Unknown"
    closest_text = "N/A"

    if "miss_distance_lunar" in neo_df.columns:
        df_dist = neo_df.dropna(subset=["miss_distance_lunar"])
        if not df_dist.empty:
            closest = df_dist.sort_values("miss_distance_lunar").iloc[0]
            closest_name = closest.get("name", "Unknown")
            closest_lunar = closest.get("miss_distance_lunar", None)
            if pd.notna(closest_lunar):
                closest_text = f"{closest_lunar:.2f} × Lunar distance"

    # largest object (by diameter_km_avg)
    largest_name = "Unknown"
    largest_text = "N/A"

    if "diameter_km_avg" in neo_df.columns:
        df_size = neo_df.dropna(subset=["diameter_km_avg"])
        if not df_size.empty:
            largest = df_size.loc[df_size["diameter_km_avg"].idxmax()]
            largest_size = largest.get("diameter_km_avg", None)
            if pd.notna(largest_size):
                largest_text = f"{largest_size:.2f} km"
            largest_name = largest.get("name", "Unknown")

    # hazardous count
    if "hazardous" in neo_df.columns:
        hazardous_count = int(neo_df["hazardous"].fillna(False).astype(bool).sum())
    else:
        hazardous_count = 0

    # layout
    col1, col2, col3, col4 = st.columns([1, 1.6, 1.6, 1], gap="large")

    with col1:
        with st.container(border=True):
            st.metric("☄️ NEOs today", total)
            st.caption(" ")

    with col2:
        with st.container(border=True):
            st.metric("🛰 Closest pass", closest_text)
            st.caption(closest_name)

    with col3:
        with st.container(border=True):
            st.metric("🪨 Largest object", largest_text)
            st.caption(largest_name)

    with col4:
        with st.container(border=True):
            st.metric("⚠️ Potentially hazardous", hazardous_count)
            st.caption(" ")



def neo_scatter_plot(neo_df: pd.DataFrame):
    """Scatter: distance vs size, colored by hazardous."""
    if neo_df is None or neo_df.empty:
        st.info("No near-Earth objects available for today.")
        return

    required = ["miss_distance_lunar", "diameter_km_avg"]
    if not all(col in neo_df.columns for col in required):
        st.info("Not enough data to plot NEO scatter (missing distance or size).")
        return

    df = neo_df.copy()
    df = df.dropna(subset=["miss_distance_lunar", "diameter_km_avg"])

    if df.empty:
        st.info("No NEOs with both distance and size available.")
        return

    chart = (
        alt.Chart(df)
        .mark_circle(size=280, opacity=0.8)
        .encode(
            x=alt.X(
                "miss_distance_lunar:Q",
                title="Closest approach (× Lunar distance)"
            ),
            y=alt.Y(
                "diameter_km_avg:Q",
                title="Estimated diameter (km)"
            ),
            color=alt.Color(
                "hazardous:N",
                title="Potentially hazardous",
                scale=alt.Scale(domain=[False, True], range=["#E6D8F7", "#B51747"])
            ),
            tooltip=[
                "name:N",
                "miss_distance_lunar:Q",
                "diameter_km_avg:Q",
                "velocity_km_s:Q",
                "hazardous:N",
            ],
        ).properties(
            width = 1300, 
            height = 360,
            padding={"top": 30, "right": 10, "bottom": 5, "left": 20}
    ).configure_view(stroke = None)
)
    st.altair_chart(chart, use_container_width=False)
