import requests
import streamlit as st

NOAA_KP_URL = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"

def get_kp() -> float:
    resp = requests.get(NOAA_KP_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    latest = data[-1]
    return float(latest["kp_index"])

