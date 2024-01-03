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
Center content for landing page
"""

import streamlit as st
from components.task_picker import task_picker_display

def landing_suggestions():
  info, plan, chat, query = st.columns(4)

  with info:
    with st.expander("Specify Task"):
      task_picker_display()

  with plan:
    with st.expander("Plan"):
      st.text("Generates and execute a plan to your specification")

  with chat:
    with st.expander("Chat"):
      st.text("Get answers with a standard prompt")

  with query:
    with st.expander("Query"):
      st.text("Utilize a data source to get answers")
