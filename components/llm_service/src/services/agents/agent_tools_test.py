"""This is a collection of tests for the tools available to AI agents"""
import pytest
from services.agents.agent_tools import vertex_code_interpreter_tool

# marking as long for potential future test streamlining
@pytest.mark.long
def test_code_interpreter():
  """Tests that code interpreter generates a response in the expected format"""
  #This is a longer running test due to a call to GCP service
  response = vertex_code_interpreter_tool(
    ("give me a pie chart of continents by land area"))
  assert "generated_code" in response
  assert "execution_error" in response
  assert "output_files" in response
  assert len(response["output_files"]) > 0
  assert "name" in response["output_files"][0]
  assert "contents" in response["output_files"][0]

