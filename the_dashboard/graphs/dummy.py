
"""OG Stargazing score chart code, kept for reference."""


def plot_stargazing_score(score_df: pd.DataFrame, location_name: str):
    if score_df is None or score_df.empty:
        st.info("No stargazing score available for tonight.")
        return

    df = score_df.copy()
    df["time"] = df["datetime"].dt.strftime("%H:%M")

    chart = (
        alt.Chart(df)
        .mark_line(strokeWidth=2, opacity=0.9, color = "#79B6DC")
        .encode(
            x=alt.X("datetime:T", title="Time"),
            y=alt.Y("score:Q", title="Stargazing score (0–100)", scale=alt.Scale(domain=[0, 100])),
            tooltip=["time", "score"],
        )
    )

    st.altair_chart(chart, use_container_width=True)





    #CHART_BG = "rgba(255, 255, 255, 0.9)"

st.markdown(
    """
    <style>
    /* Style the container that holds Altair/Vega-Lite charts */
    div[data-testid="stVegaLiteChart"] {
        background-color: rgba(255, 255, 255, 0.9);  /* light card background */
        border-radius: 18px;                         /* rounded corners */
        padding: 1rem 1.2rem 1.2rem 1.2rem;          /* space around chart */
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        overflow: hidden;                           /* optional: soft shadow */
    }
    </style>
    """,
    unsafe_allow_html=True,
)



# og backgr function:
import streamlit as st
import base64

def set_bg_local(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )