import requests
import streamlit as st

# NOAA SWPC endpoints (no keys)

OVATION_URL = "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"
KP_FORECAST_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json"
SOLAR_WIND_MAG_URL = "https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json"
SOLAR_WIND_PLASMA_URL = "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json"


@st.cache_data(ttl=1800)  # 30 min
def get_ovation_aurora():
    """
    OVATION aurora probability grid (global, ~30 min cadence).
    """
    r = requests.get(OVATION_URL, timeout=15)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=3600)  # 1 hour
def get_kp_forecast():
    """
    Planetary Kp index forecast (NOAA).
    """
    r = requests.get(KP_FORECAST_URL, timeout=15)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=300)  # 5 min
def get_solar_wind():
    """
    Near-real-time solar wind data.
    Returns empty payloads if NOAA is temporarily unreachable.
    """
    try:
        mag = requests.get(SOLAR_WIND_MAG_URL, timeout=15)
        plasma = requests.get(SOLAR_WIND_PLASMA_URL, timeout=15)

        mag.raise_for_status()
        plasma.raise_for_status()

        return {
            "mag": mag.json(),
            "plasma": plasma.json(),
        }

    except requests.RequestException:
        # NOAA endpoint occasionally goes down / DNS fails
        return {
            "mag": [],
            "plasma": [],
        }

