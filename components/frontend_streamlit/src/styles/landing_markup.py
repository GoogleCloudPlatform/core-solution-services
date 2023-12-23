import streamlit as st
import os
from styles.sidebar_logo import display_side_logo

def landing_theme():
  styles_path = os.path.join(os.path.dirname(__file__), 'main.css')

  with open(styles_path) as f:
    MAIN_STYLES = f.read()
  
  # Contains global styles that will be used across all pages
  st.markdown(f'<style>{MAIN_STYLES}</style>', unsafe_allow_html=True)

  display_side_logo()

  LANDING_STYLES = """
    <style>
      /* Text input styling */
      [data-testid="textInputRootElement"] > div:nth-child(1) {
        background-color: #FFFFFF;
      }
      [data-testid="textInputRootElement"] {
        background-color: #FFFFFF;
        border: 1px solid #90989f;
        transition: border-color 0.1s ease-in, border-width 0.08s ease-in;
        border-radius: 18px;
      }
      [data-testid="textInputRootElement"]:has(input:focus) {
        border: 2px solid #4285f4;
      }
      [data-testid="textInputRootElement"] input {
        font-family: Arial;
        color: #5f6368;
        -webkit-text-fill-color: black;
        padding: 0.85rem;
      }
      .main [data-testid="stFormSubmitButton"] button {
        border: none;
        padding-bottom: .35rem;
        padding-left: 0;
        float: right;
        color: rgb(0 0 0 / 64%);
        background-color: transparent;
      }
      .main [data-testid="stFormSubmitButton"] button:hover {
        color: #4285f4;
      }
      .main [data-testid="stFormSubmitButton"] button::after {
        content: "➤";
        font-size: 26px;
        transition: color 0.1s ease-in;
      }
      .main [data-baseweb=select] > div:nth-child(1) {
        cursor: pointer;
        border-color: #90989f;
        background-color: #FFFFFF;
        border-radius: 0.7rem;
      }
      .main [data-testid=stSelectbox] svg {
        color: #5f6368;
      }
      [data-testid=stVirtualDropdown] li {
        background-color: #FFFFFF;
      }
    </style>
  """
  st.markdown(LANDING_STYLES, unsafe_allow_html=True)
