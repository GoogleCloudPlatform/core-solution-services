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

""" Agent utilities """
import re
import io
from contextlib import redirect_stdout
from common.utils.logging_handler import Logger

Logger = Logger.get_logger(__file__)
ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_punctuation_from_end(text):
  # Regular expression pattern to match punctuation at the end of the string
  pattern = r"[^\w]+$"

  # Replace the matched punctuation with an empty string
  return re.sub(pattern, "", text)

def clean_agent_logs(text):
  text = ansi_escape.sub("", text)
  text = re.sub(r'\[1;3m', "\n", text)
  text = re.sub(r'\[[\d;]+m', "", text)
  return text

def agent_executor_run_with_logs(agent_executor, agent_inputs):
  # collect print-output to the string.

  with io.StringIO() as buf, redirect_stdout(buf):
    result = agent_executor.run(agent_inputs)
    agent_logs = buf.getvalue()
    Logger.info(f"Agent process result: \n\n{result}")
    Logger.info(f"Agent process log: \n\n{agent_logs}")
    return result, clean_agent_logs(agent_logs)
