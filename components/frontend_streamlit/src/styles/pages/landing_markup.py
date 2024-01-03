import streamlit as st
from styles.style_constants import colors
from styles.shared_styles import main_styles

def landing_theme():
  main_styles()

  LANDING_STYLES = f"""
    <style>
      /* Hidden elements */
      .main [data-testid="stFormSubmitButton"] button p {{
        display: none;
      }}
      .main [data-testid="stVerticalBlock"] {{
        gap: 0;
      }}

      /* Heading styles */
      .main .stHeadingContainer h1 {{
        font-family: Arial;
        color: {colors['text_primary']};
      }}
      .main .stHeadingContainer h3 {{
        font-family: Arial;
        font-weight: normal;
        color: {colors['dim_text']};
        padding-bottom: 2.7rem;
      }}
      
      /* Text input positioning */
      .main [data-testid="block-container"] {{
        overflow: auto;
      }}
      .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
        position: fixed;
      }}

      /* Text input styling */
      [data-testid="textInputRootElement"] > div:nth-child(1) {{
        background-color: {colors['light_fill']};
      }}
      [data-testid="textInputRootElement"] {{
        background-color: {colors['light_fill']};
        border: 1px solid {colors['border_primary']};
        transition: border-color 0.1s ease-in, border-width 0.2s ease-in;
        border-radius: 18px;
      }}
      [data-testid="textInputRootElement"]:has(input:focus) {{
        border: 2px solid {colors['tint_primary']};
      }}
      [data-testid="textInputRootElement"] input {{
        color: {colors['input_text']};
        -webkit-text-fill-color: {colors['input_text']};
      }}

      /* Input button styling */
      .main [data-testid="stFormSubmitButton"] button {{
        border: none;
        padding-left: 0;
        float: right;
        color: {colors['dim_text']} !important;
        background-color: transparent !important;
      }}
      .main [data-testid="stFormSubmitButton"] button:hover {{
        color: {colors['tint_primary']} !important;
      }}
      .main [data-testid="stFormSubmitButton"] button::after {{
        content: "➤";
        font-size: 26px;
        transition: color 0.2s ease-in;
      }}

      /* Smartphones and small devices */
      @media screen and (max-width: 1024px) {{
        .main .stHeadingContainer h1 {{
          font-size: 26px;
          padding-top: 1.1rem;
          padding-bottom: .8rem;
        }}
        .main .stHeadingContainer h3 {{
          font-size: 16px;
        }}
        [data-testid="textInputRootElement"] input {{
          padding: 0.7rem;
        }}
        .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
          bottom: 20px;
        }}
        .main [data-testid="block-container"] {{
          padding: 25px 12px;
        }}
      }}

      /* Laptops and small displays */
      @media screen and (min-width: 1024px) and (max-width: 1366px) {{
        .main .stHeadingContainer h1 {{
          font-size: 32px;
          padding-top: 1.3rem;
          padding-bottom: 1rem;
        }}
        .main .stHeadingContainer h3 {{
          font-size: 20px;
        }}
        [data-testid="textInputRootElement"] input {{
          padding: 0.72rem;
        }}
        .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
          bottom: 44px;
        }}
        .main [data-testid="stFormSubmitButton"] button {{
          padding-bottom: 2px;
        }}
        .main [data-testid="block-container"] {{
          padding: 28px 20px;
        }}
      }}

      /* Large monitors */
      @media screen and (min-width: 1366px) and (max-width: 1600px) {{
        .main .stHeadingContainer h1 {{
          font-size: 40px;
          padding-top: 1.56rem;
          padding-bottom: 1.18rem;
        }}
        .main .stHeadingContainer h3 {{
          font-size: 22px;
        }}
        [data-testid="textInputRootElement"] input {{
          padding: 0.83rem;
        }}
        .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
          bottom: 54px;
        }}
        .main [data-testid="stFormSubmitButton"] button {{
          padding-bottom: 5px;
        }}
        .main [data-testid="block-container"] {{
          padding: 38px 22px;
        }}
      }}

      /* Very large monitors */
      @media screen and (min-width: 1600px) {{
        .main .stHeadingContainer h1 {{
          font-size: 44px;
          padding-top: 1.6rem;
          padding-bottom: 1.2rem;
        }}
        .main .stHeadingContainer h3 {{
          font-size: 24px;
        }}
        [data-testid="textInputRootElement"] input {{
          padding: 0.85rem;
        }}
        .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
          bottom: 64px;
        }}
        .main [data-testid="stFormSubmitButton"] button {{
          padding-bottom: 4px;
        }}
        .main [data-testid="block-container"] {{
          padding: 40px 24px;
        }}
      }}
    </style>
  """
  st.markdown(LANDING_STYLES, unsafe_allow_html=True)
