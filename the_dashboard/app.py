# Import the libraries
import streamlit as st
import streamlit.components.v1 as components  # noqa: F401
import pandas as pd  # noqa: F401
from datetime import datetime  # noqa: F401
from datetime import date
import altair as alt  # noqa: F401



# Import the data 
from data.api.apod_api import get_apod
from data.api.weather_api import get_weather
from data.api.neo_api import get_neo
from data.dataframes.weather_df import weather_to_df
from data.dataframes.neo_df import neo_to_dataframe
from data.dataframes.locations import LOCATIONS_SWEDEN
from data.api.neo_api import get_neo
from data.api.aurora_api import get_ovation_aurora, get_kp_forecast, get_solar_wind
from data.dataframes.aurora_df import parse_aurora_bundle


# Import the graphs & functions
from graphs.weather_charts import cloud_visibility_chart, temp_humidity_chart  # noqa: E402
from graphs.neo_charts import neo_summary_metrics, neo_scatter_plot  # noqa: E402
from graphs.stargazing_score import compute_stargazing_score, plot_stargazing_score  # noqa: E402
from functions.background import set_bg_url  # noqa: E402
from functions.moon_phase import get_phase_info
from functions.choose_location import choose_location
from functions.aurora_score import compute_aurora_chance


# Fetching/Loading and caching data from APIs

# Wrapping the apis in @st.cache_data to cache results and avoid hitting rate limits/reduce lag
@st.cache_data(ttl = 36000) #72000 setting it to 20 hours as APOD only updates once a day
def get_apod_cached():
    return get_apod()

@st.cache_data(ttl = 10800)  #1800 og weather timer
def get_weather_cached(lat, lon):
    raw_weather = get_weather(lat, lon)
    df_hours, astro_info = weather_to_df(raw_weather)
    return df_hours, astro_info

@st.cache_data(ttl = 3600)
def get_neo_cached(date):
    raw_neo = get_neo(date)
    neo_df = neo_to_dataframe(raw_neo)
    return neo_df

@st.cache_data(ttl=86400)  # 24h
def _search_locations_df_cached(q: str):
    hits = search_locations_raw(q)
    return locations_to_df(hits, country="Sweden")


# helper function for the APOD banner
def apod_banner(url: str, height: int = 350):
    st.markdown(
        f"""
        <div style="
            width: 100%;
            max-height: {height}px;
            overflow: hidden;
            border-radius: 10px;
        ">
            <img src="{url}"
                 style="width: 100%; height: 100%; object-fit: cover;">
        </div>
        """,
        unsafe_allow_html=True
    )
## Set up the layout of the dashboard
st.set_page_config(page_title="Stargazing Forecast", layout="wide")

# Changing background to something cooler once I have time to fix it
set_bg_url("https://raw.githubusercontent.com/Iberis-9/streamlit_nod/93f63806a3964ef47eaa24f2c53580dbbf260ba5/the_dashboard/images/backgr.jpg")


# Global setup for Altair charts, making them transparent and styling axes
alt.themes.register('transparent_theme', lambda: {
    "config": {                         # just so I remember what's exactly what:
        "background": "transparent",     # outer chart background
        "view": {
            "fill": "transparent",       # plot area background
            "stroke": "transparent",      # border
        },
    "axis": {
            "grid": True,
            "gridColor": "#FFFFFF",      
            "gridOpacity": 0.3,          # grid transparency
            "tickColor": "#FFFFFF",     # axis tick marks
            "labelColor": "#FFFFFF",   # axis label text
            "titleColor": "#FFFFFF",     # axis title text
        }
    }
})

alt.themes.enable('transparent_theme')

st.markdown(
    """
    <style>
    /* Style the container that holds Altair/Vega-Lite charts */
    div[data-testid="stVegaLiteChart"] {
        background-color: rgba(255, 255, 255, 0.12);  /* light card background */
        border-radius: 18px;                         /* rounded corners */
        padding: 1rem 1.2rem 1.2rem 1.2rem;          /* space around chart */
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                                  /* optional: soft shadow */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# get the apod image and data
data = get_apod_cached()

#st.caption("🔭 Astronomy Picture of the Day")
st.markdown("## Stargazing Forecast — *Tonight’s Skies in Sweden*")

# Short intro
st.write("NASA’s Astronomy Picture of the Day.")

# Banner using the helper function
apod_banner(data["url"], height=350)


# Explanation text and link to full-res image
with st.expander("About today's image"):
    st.write(data["explanation"])
    if "hdurl" in data:
        st.markdown(f"[🔗 View full-resolution image]({data['hdurl']})")
    else:
        st.markdown(f"[🔗 View full image]({data['url']})")

st.markdown("---")

# Short description of what my dash/app does
st.write("See where Sweden gets the best stars tonight—watch the clouds, visibility, moonlight, and the asteroids cruising by.")

# old location selector
#st.header("Choose your location")

#location_name = st.selectbox("Location", list(LOCATIONS_SWEDEN.keys()))
#coords = LOCATIONS_SWEDEN[location_name]

# LOCATION SELECTION 
location_name, lat, lon = choose_location(LOCATIONS_SWEDEN)

if lat is None:
    st.info("Pick a location to load tonight’s forecast.")
    st.stop()


night = None
astro_info = None
neo_df = None


# lat/lon now come directly from choose_location
df_hours, astro_info = get_weather_cached(lat, lon)

today = date.today()
neo_df = get_neo_cached(today)

night = df_hours[df_hours["is_day"] == 0].copy()


# Different sections/tabs for different parts of the dashboard
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Weather Overview", "Near-Earth Objects", "Stargazing Score", "Northern Lights"]
)

#  Tab 1: Overview 
# The brighter the Moon, the fewer stars you’ll see. Low illumination gives the darkest skies.
with tab1:
    if night is None or astro_info is None:
        st.warning("Select a location to see tonight's overview.")
    else:
        st.subheader(f"Tonight in {location_name}")

        col_a, col_b, col_c, col_d = st.columns(4, border=True)
        
        with col_a:
            st.metric(
                "🌙 Moon phase",
                astro_info["moon_phase"],
                f"{astro_info['moon_illumination']}% illuminated"
            )
            with st.expander("About this Moon phase"):
                emoji, explanation = get_phase_info(astro_info["moon_phase"])
                st.markdown(f"### {emoji} {astro_info['moon_phase']}")
                st.write(explanation)

        with col_b:
            min_cloud = int(night["cloud_cover"].min())
            st.metric("☁️ Cloud coverage (night)", f"{min_cloud}%")
            with col_b:
                st.caption("Lower cloud cover = more visible sky")


        with col_c:
            max_vis = night["visibility_km"].max()
            st.metric("🔭 Max visibility (night)", f"{max_vis:.1f} km")
            st.caption("Higher visibility = clearer atmosphere")

        with col_d:
            st.metric("☀️ Sunset", astro_info["sunset"])

# Tab 2: Weather Overview 

with tab2:
    if night is None:
        st.warning("Select a location to see weather details.")
    else:
        st.subheader("Cloud cover & visibility (night hours)")
        st.write("Cloud cover and visibility are the two main factors that determine how clear the night sky will look. Fewer clouds mean more stars are unobstructed, and higher visibility means less haze or moisture in the air. Together, they give a quick sense of how good the sky will be for stargazing tonight.")
        st.write("")
        #with st.container(border=True):
        cloud_visibility_chart(night)
        st.caption("Higher visibility = clearer atmosphere")
            
        
        st.subheader("Temperature & humidity (night hours)")
        st.write("Temperature and humidity also impact stargazing conditions. Cooler temperatures often correlate with clearer skies, while high humidity can lead to haze or fog that obscures the stars. Monitoring these metrics helps you anticipate both how clear the sky will be and how comfortable you’ll be standing outside. Basically: this tells you whether you’ll enjoy the view of the Milky Way or just turn into a popsicle. Check both before heading out so you know whether to bring a jacket, a thermos, or… just stay inside.”")
        st.write("")
        #with st.container(border=True):
        temp_humidity_chart(night)
        st.caption("High humidity can cause haze and reduce clarity")
            

# Tab 3: Near-Earth Objects 

with tab3:

    st.caption("Near-Earth Objects visibile today.")

    if neo_df is None:
        st.warning("Select a location to see NEO data.")
    else:
        st.subheader("Today's near-Earth objects")

        neo_summary_metrics(neo_df)

        st.markdown("#### Size vs distance")
        neo_scatter_plot(neo_df)
        st.caption(
            "Points further left are closer to Earth (in Moon–Earth distances); "
            "points higher up are larger asteroids. Red markers are classified as potentially hazardous."
        )

# Tab 4: Stargazing Score 

with tab4:
    if night is None or astro_info is None:
        st.warning("Select a location to see the stargazing score.")
    else:
        st.subheader(f"✨ Stargazing score for tonight in {location_name}")

        score_df = compute_stargazing_score(night, astro_info)
        overall_score = score_df["score"].mean()

        col1, col2 = st.columns(2, gap="large", border=True)

        with col1:
            st.metric("Overall stargazing score (night)", f"{overall_score:.0f} / 100")

        with st.expander("How this score is calculated"):
            st.write("""
        This score reflects tonight’s overall sky quality. It takes into account cloud cover, visibility, humidity, and moon illumination. Each component is scaled and blended into a 0–100 rating.The higher the score, the better the stargazing conditions!
        """)

        st.markdown("---")

        # Score verdict
        score_10 = overall_score / 10
        if score_10 >= 8:
            verdict = "✨ Incredible night — go outside!"
        elif score_10 >= 6:
            verdict = "🌙 Pretty good — worth a look."
        elif score_10 >= 4:
            verdict = "🌥 Meh — sky conditions mixed."
        else:
            verdict = "☁ Not a great night for stargazing."

        with col2:
            st.markdown(f"### {verdict}")

        # Chart
        st.markdown("#### Score by hour (night only)")
        plot_stargazing_score(score_df, location_name)

# Tab 5: The Northern Lights

with tab5:
    st.subheader(f"🌌 Northern Lights chance tonight in {location_name}")

    bundle = parse_aurora_bundle(get_ovation_aurora(), get_kp_forecast(), get_solar_wind())
    result = compute_aurora_chance(lat, lon, bundle["ovation_df"], bundle["kp_latest"], bundle["solar_wind_now"])

    score = result.chance_0_100

    if score >= 70:
        verdict = "💫 High chance — look north tonight!"
    elif score >= 40:
        verdict = "✨ Possible — worth keeping an eye on the sky"
    elif score >= 20:
        verdict = "🌥 Unlikely — conditions are weak"
    else:
        verdict = "☁ Very unlikely tonight"


    st.metric("Northern Lights visibility chance (tonight)", f"{result.chance_0_100:.0f} / 100")
    st.caption(result.note)
    
    if result.speed is None:
        st.caption("⚠️ Live solar wind data temporarily unavailable (NOAA) — score may be less accurate.")


    c1, c2, c3 = st.columns(3, border=True)

    c1.metric(
        "🔥 Aurora activity nearby",
        "—" if result.ovation_prob is None else f"{result.ovation_prob:.0f} / 100",
    )
    c1.caption("How active the northern lights are around your location right now")

    c2.metric(
        "🧲 Aurora reach (geomagnetic activity)",
        "—" if result.kp is None else f"Kp {result.kp:.1f}",
    )
    c2.caption("Higher values mean northern lights can be seen further south")

    c3.metric(
        "☀️💨 Solar wind direction",
        "—" if result.bz_gsm is None else f"{result.bz_gsm:.1f} nT",
    )
    c3.caption("Southward flow makes northern lights more likely")


    with st.expander("🔍 What do these metrics mean?"):
        st.markdown("""
        **Northern Lights visibility** is estimated using real-time space weather data from NOAA.

        Here’s how to read the indicators above:

        **🔥 Aurora activity nearby**  
        This shows how strong the *aurora oval* is near your location right now.

        The *aurora oval* is a ring-shaped zone around the Earth’s poles where Northern Lights usually appear.  
        When this zone becomes stronger or expands southward, aurora can be seen further from the Arctic.

        **🧲 Aurora reach (geomagnetic activity / Kp)**  
        This describes how disturbed Earth’s magnetic field is.  
        Higher values mean the aurora oval expands southward, increasing the chance of seeing Northern Lights in Sweden.

        **☀️ Solar wind direction**  
        This measures how solar wind interacts with Earth’s magnetic field.  
        A *southward* flow allows more energy into the atmosphere, making aurora more likely.

        **How the score is calculated**  
        The main score combines:
        - how strong the aurora zone is near you
        - how far south aurora activity can reach
        - current solar wind conditions

        The result is a **0–100 estimate** of how likely you are to see Northern Lights from your selected location tonight.
        """)









