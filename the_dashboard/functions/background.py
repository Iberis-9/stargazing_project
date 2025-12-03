from pathlib import Path
import streamlit as st
import base64


def set_bg_local(image_path: str):
    # Get absolute path to this file’s folder: the_dashboard/functions/
    this_dir = Path(__file__).resolve().parent

    # Move up to the "the_dashboard" folder
    base_dir = this_dir.parent

    # Construct correct absolute path to the image (e.g. the_dashboard/images/backgr.jpg)
    full_path = base_dir / image_path

    # Read and encode the image
    with open(full_path, "rb") as f:
        data = f.read()

    encoded = base64.b64encode(data).decode()

    css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
    """

    st.markdown(css, unsafe_allow_html=True)
