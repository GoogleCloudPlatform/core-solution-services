import streamlit as st

def suggestions_component():
  SUGGESTIONS_STYLES = """
    <style>
      .main [data-testid="stExpander"] details {
        border-color: #FFFFFF;
        border-radius: 0.7rem;
        background-color: #FFFFFF;
        color: rgb(0 0 0 / 64%);
      }
      .main [data-testid="stExpander"] summary:hover {
        color: #3b3a3a;
      }
      .main [data-testid="stExpander"] summary svg {
        display: none;
      }
      .main [data-testid="stExpander"] summary p {
        font-weight: 600;
        font-size: 16px;
      }
    </style>
  """
  st.markdown(SUGGESTIONS_STYLES, unsafe_allow_html=True)
  