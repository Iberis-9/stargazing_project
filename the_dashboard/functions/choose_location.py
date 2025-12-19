import streamlit as st
import unicodedata
import pandas as pd

from data.api.geo_api import search_locations_raw
from data.dataframes.geo_df import locations_to_df


def _normalize_for_search(s: str) -> str:
    """
    Normalize Swedish characters for APIs that don't handle å/ä/ö well.
    Västerås -> Vasteras, Örebro -> Orebro, Åre -> Are
    """
    return (
        unicodedata.normalize("NFKD", s)
        .encode("ascii", "ignore")
        .decode("ascii")
    )

@st.cache_data(ttl=86400)
def _search_locations_df_cached(query: str) -> pd.DataFrame:
    api_key = st.secrets["WEATHER_KEY"]
    hits = search_locations_raw(query, api_key)
    return locations_to_df(hits, country="Sweden")


def choose_location(popular_locations: dict | None = None):
    """
    UI component for choosing a location in Sweden.

    Returns:
        (location_name, lat, lon) or (None, None, None)
    """

    st.header("Choose your location")

    # Optional preset locations
    if popular_locations:
        mode = st.radio(
            "Location type",
            ["Popular locations", "Search Sweden"],
            horizontal=True,
            label_visibility="collapsed",
        )
    else:
        mode = "Search Sweden"

    # --- Popular locations ---
    if mode == "Popular locations":
        name = st.selectbox("Location", list(popular_locations.keys()))
        lat, lon = popular_locations[name]
        return name, float(lat), float(lon)

    # --- Free search ---
    raw_q = st.text_input(
        "Sök plats i Sverige",
        placeholder="t.ex. Västerås, Örebro, Åre",
    ).strip()

    if len(raw_q) < 2:
        return None, None, None

    # Try native Swedish spelling first
    df = _search_locations_df_cached(raw_q)

    # If nothing found, retry with normalized query
    if df.empty:
        df = _search_locations_df_cached(_normalize_for_search(raw_q))

    if df.empty:
        st.warning("Ingen plats hittades i Sverige.")
        return None, None, None

    # If only one match, auto-select
    if len(df) == 1:
        row = df.iloc[0]
    else:
        label = st.selectbox("Välj rätt plats", df["label"].tolist())
        row = df[df["label"] == label].iloc[0]

    return row["label"], float(row["lat"]), float(row["lon"])
