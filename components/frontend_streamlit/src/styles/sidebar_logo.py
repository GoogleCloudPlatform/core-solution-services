import streamlit as st

def display_side_logo():
  NAV_STYLES = """
    <style>
      [data-testid="stSidebarNav"]::before {
        content: "GENIE";
        font-weight: 500;
        font-family: Arial;
        color: #5f6368;
        padding-left: 60px;
      }
      [data-testid="stSidebarContent"] [data-testid="baseButton-header"]::after {
        content: "≡";
        color: #5f6368;
        font-size: 35px;
      }
      [data-testid="stSidebarContent"] [data-testid="baseButton-header"] svg {
        display: none;
      }
      [data-testid="stSidebarContent"] div:has([data-testid="baseButton-header"]) {
        width: 22px;
        right: 0;
        left: 12px;
      }

      /* Smartphones and small devices */
      @media screen and (max-width: 1024px) {
        [data-testid="stSidebarNav"]::before {
          font-size: 20px;
        }
        [data-testid="stSidebarNav"] {
          padding-top: 12px;
        }
        [data-testid="stSidebarContent"] [data-testid="baseButton-header"]::after {
          font-size: 28px;
        }
      }

      /* Laptops and small displays */
      @media screen and (min-width: 1024px) and (max-width: 1366px) {
        [data-testid="stSidebarNav"]::before {
          font-size: 24px;
        }
        [data-testid="stSidebarNav"] {
          padding-top: 14px;
        }
        [data-testid="stSidebarContent"] div:has([data-testid="baseButton-header"]) {
          top: 7px;
        }
      }

      /* Large monitors and very large monitors */
      @media screen and (min-width: 1366px) {
        [data-testid="stSidebarNav"]::before {
          font-size: 26px;
        }
        [data-testid="stSidebarNav"] {
          padding-top: 18px;
        }
        [data-testid="stSidebarContent"] div:has([data-testid="baseButton-header"]) {
          top: 13px;
        }
      }
    </style>
  """
  st.markdown(NAV_STYLES, unsafe_allow_html=True)