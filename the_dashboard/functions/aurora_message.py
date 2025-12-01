import requests
import streamlit as st

def aurora_message(kp: float) -> str:
    if kp < 3:
        return "Low activity — auroras are unlikely at this latitude tonight."
    elif kp < 5:
        return "Moderate activity — faint auroras possible in northern Sweden under dark skies."
    elif kp < 7:
        return "Strong activity — good chances for auroras in northern Sweden if skies are clear."
    else:
        return "Severe geomagnetic storm — auroras may be visible much further south than usual."
