import streamlit as st

def history_styles():
  HISTORY_STYLE = """<style>
  /* General styles for sidebar content */
  [data-testid=stSidebarUserContent] {
    /* Button styles */
    .stButton button {
      background-color: #c4eed0;
      color: #1F1F1F;
      font-weight: bold;
      text-align: left;
      border: 0;
      border-radius: 11px;
      display: block !important;
      transition: background-color 0.1s ease-in;

      /* Dark mode specific styles */
      @media screen and (prefers-color-scheme: dark) {
        background-color: #195;
      }

      /* Hover state for buttons */
      &:hover {
        background-color: #b9e2c5;
      }
    }

    h3 {
      padding-top: .59rem;
      font-size: .97rem;
      font-weight: 500;
    }

    /* Styles for horizontal block buttons */
    [data-testid=stHorizontalBlock] .stButton button {
      background-color: #4285f4;
      color: white;
      float: right;

      &:hover {
        background-color: #2369de;
      }
    }

    /* Styles for text in vertical block buttons */
    [data-testid=stVerticalBlockBorderWrapper] .stButton p {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      font-family: Arial;
      font-size: .875rem;
    }

    /* Styles for select components */
    [data-baseweb=select] > div:nth-child(1), [data-testid=stSelectbox] svg {
      cursor: pointer;
      border-color: #90989f;
      border-radius: 0.7rem;
      color: #5f6368; /* Assuming you want to apply this color to the select svg as well */
    }
  }

  /* Styles for the sidebar navigation separator */
  [data-testid=stSidebarNavSeparator] {
    margin-left: 20px;
    margin-right: 20px;
  }

  /* Styles for dropdown list items */
  [data-testid=stVirtualDropdown] li {
    background-color: #FFFFFF;
  }

  [data-testid="stSidebarNavItems"] {
    padding-top: 1rem;
  }
  </style>"""
  st.markdown(HISTORY_STYLE, unsafe_allow_html=True)
  