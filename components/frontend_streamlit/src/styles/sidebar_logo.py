# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Adds hamburger menu button and GENIE title to sidebar
"""

import streamlit as st

def display_side_logo():
  side_logo_styles = """
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
  st.markdown(side_logo_styles, unsafe_allow_html=True)
