import base64
import os
from pathlib import Path

import streamlit as st
import validators

def add_logo(logo_path: str):
    """Add a logo (from logo_url) on the top of the navigation page of a multipage app.
    The url can either be a url to the image, or a local path to the image.

    Args:
        logo_path (str): URL/local path of the logo
    """

    logo_url = os.path.join(os.path.dirname(__file__), logo_path)

    if validators.url(logo_url) is True:
        logo = f"{logo_url}"
    else:
        logo = f"data:image/png;base64,{base64.b64encode(Path(logo_url).read_bytes()).decode()}"

    st.image(logo)
