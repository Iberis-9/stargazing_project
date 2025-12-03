import pandas as pd
import streamlit as st
import altair as alt

# Mapping of moon phases with explanations and little matching moon icons
phase_info = {
    "New Moon": (
        "🌑",
        "The Moon’s sunlit side faces away from Earth, making it essentially invisible. "
        "It rises and sets with the Sun since both are in nearly the same direction in the sky."
    ),
    "Waxing Crescent": (
        "🌒",
        "A thin sliver of the Moon’s dayside becomes visible as it moves east of the Sun. "
        "The illuminated portion grows a little each day, and the Moon rises slightly later each evening."
    ),
    "First Quarter": (
        "🌓",
        "We see half of the Moon’s sunlit hemisphere. The Moon is about 90° east of the Sun, "
        "rising around noon and setting near midnight—high in the sky during the evening."
    ),
    "Waxing Gibbous": (
        "🌔",
        "More than half of the Moon’s dayside is visible. The illuminated area continues to increase "
        "as the Moon moves toward its opposite position from the Sun."
    ),
    "Full Moon": (
        "🌕",
        "The Moon is opposite the Sun from Earth, and the entire dayside faces us. "
        "It rises near sunset and sets near sunrise, appearing full for about two nights."
    ),
    "Waning Gibbous": (
        "🌖",
        "The illuminated portion starts decreasing after the Full Moon as the Moon moves back toward the Sun. "
        "It rises later each night and is most visible in the late-night and morning hours."
    ),
    "Last Quarter": (
        "🌗",
        "We again see half of the Moon’s sunlit hemisphere, but the opposite half from First Quarter. "
        "It rises around midnight and sets around noon, making it prominent in the morning sky."
    ),
    "Waning Crescent": (
        "🌘",
        "Only a thin curve of the dayside remains visible as the Moon approaches alignment with the Sun. "
        "It rises shortly before sunrise and marks the final phase of the lunar cycle."
    ),
}

def get_phase_info(phase: str):
    return phase_info.get(
        phase,
        ("🌙", "The Moon is in this phase as it orbits Earth.")
    )
