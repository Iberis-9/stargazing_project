def cloud_visibility_chart(night_df: pd.DataFrame):
    """Line chart: cloud cover + visibility over night hours."""
    cloud_vis = night_df[["datetime", "cloud_cover", "visibility_km"]].copy()
    cloud_vis["time"] = cloud_vis["datetime"].dt.strftime("%H:%M")

    # Shared color scale + legend for both layers
    color = alt.Color(
        "series:N",
        scale=alt.Scale(
            domain=["Cloud cover", "Visibility"],
            range=["#79B6DC", "#4C3E78"],  # pick whatever colors you like
        ),
        legend=alt.Legend(title="Metric"),
    )
    # Cloud cover line
    cloud_line = (
        alt.Chart(cloud_vis)
        .transform_calculate(series="'Cloud cover'")
        .mark_line()
        .encode(
            x=alt.X("datetime:T", title="Time"),
            y=alt.Y("cloud_cover:Q", title="Cloud cover (%)"),
            color=color,
            tooltip=["time", "cloud_cover", "visibility_km"],
        )
    )
    # Visibility line (dashed, separate y-axis)
    vis_line = (
        alt.Chart(cloud_vis)
        .transform_calculate(series="'Visibility'")
        .mark_line(strokeDash=[4, 4])
        .encode(
            x="datetime:T",
            y=alt.Y("visibility_km:Q", title="Visibility (km)"),
            color=color,
            tooltip=["time", "cloud_cover", "visibility_km"],
        )
    )
    st.altair_chart(
        (cloud_line + vis_line).resolve_scale(y="independent"),
        use_container_width=True,
    )
