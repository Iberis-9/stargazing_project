import altair as alt
import streamlit as st
import pandas as pd


# Helper function for styling the graphs with a rounded background


# Visibility + cloud cover chart

def cloud_visibility_chart(night_df: pd.DataFrame):
    # Line chart: cloud cover + visibility over night hours
    cloud_vis = night_df[["datetime", "cloud_cover", "visibility_km"]].copy()
    cloud_vis["time"] = cloud_vis["datetime"].dt.strftime("%H:%M")

    # Shared color scale + legend for both layers
    color = alt.Color(
        "series:N",
        scale=alt.Scale(
            domain=["Cloud cover", "Visibility"],
            range=["#BE8BFC", "#FFFF99"],  # first colour is clouds, second is visibility
        ),
        legend=alt.Legend(title="Metric"),
    )
    # Cloud cover line
    cloud_line = (
        alt.Chart(cloud_vis)
        .transform_calculate(series="'Cloud cover'")
        .mark_line(strokeWidth=3)
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
        .mark_line(strokeDash=[4, 4], strokeWidth=3)
        .encode(
            x="datetime:T",
            y=alt.Y("visibility_km:Q", title="Visibility (km)"),
            color=color,
            tooltip=["time", "cloud_cover", "visibility_km"],
        )
    )
    main_chart = (
        (cloud_line + vis_line)
        .resolve_scale(y="independent")
        .properties(
            width=1300,    
            height=360,
            padding={"top": 30, "right": 10, "bottom": 5, "left": 20}
        )
        .configure_view(stroke=None)
    )
    # IMPORTANT: no use_container_width here, or Streamlit will stretch it again
    st.altair_chart(main_chart, use_container_width=False)

    #st.altair_chart(
    #    (cloud_line + vis_line).resolve_scale(y="independent"),
    #   width = "content", use_container_width=True,)

# Humidity + temperature chart

def temp_humidity_chart(night_df: pd.DataFrame):
    # Line chart: temperature + humidity over night hours.
    temp_hum = night_df[["datetime", "temp_c", "humidity"]].copy()
    temp_hum["time"] = temp_hum["datetime"].dt.strftime("%H:%M")

    # Shared color encoding for legend + custom colors
    color = alt.Color(
        "series:N",
        scale=alt.Scale(
            domain=["Temperature", "Humidity"],
            range=["#BE8BFC", "#FFFF99"],  
        ),
        legend=alt.Legend(title="Metric"),
    )

    temp_line = (
        alt.Chart(temp_hum)
        .transform_calculate(series="'Temperature'")
        .mark_line(strokeWidth=3)
        .encode(
            x=alt.X("datetime:T", title="Time"),
            y=alt.Y("temp_c:Q", title="Temperature (°C)"),
            color=color,
            tooltip=["time", "temp_c", "humidity"],
        )
    )

    hum_line = (
        alt.Chart(temp_hum)
        .transform_calculate(series="'Humidity'")
        .mark_line(strokeDash=[4, 4], strokeWidth=3)
        .encode(
            x="datetime:T",
            y=alt.Y("humidity:Q", title="Humidity (%)"),
            color=color,
            tooltip=["time", "temp_c", "humidity"],
        )
    )
    main_chart = (
        (temp_line + hum_line)
        .resolve_scale(y="independent")
        .properties(
            width=1300,   
            height=360,
            padding={"top": 30, "right": 20, "bottom": 5, "left": 20}
        )
        .configure_view(stroke=None)
    )

    # IMPORTANT: no use_container_width here, or Streamlit will stretch it again
    st.altair_chart(main_chart, use_container_width=False)
    
    
    #st.altair_chart(
    #   (temp_line + hum_line).resolve_scale(y="independent"),
    #    width = "content", use_container_width=True)



