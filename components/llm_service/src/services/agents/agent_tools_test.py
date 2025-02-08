"""This is a collection of tests for the tools available to AI agents"""
import pytest
from unittest import mock

# pylint: disable =   redefined-outer-name

from services.agents.agent_tools import (
  agent_tool_registry,
  agent_tool,
  rules_engine_get_ruleset_fields,
  rules_engine_execute_ruleset,
  ruleset_input_tool,
  ruleset_execute_tool,
  gmail_tool,
  docs_tool,
  google_sheets_tool,
  run_chat_tools
)

# Test data
MOCK_RULESET_FIELDS = {
  "income": "number",
  "age": "number",
  "state": "string"
}

MOCK_RULESET_RESULT = {
  "eligible": True,
  "reason": "Meets all criteria"
}

MOCK_SHEET_RESPONSE = {
  "status": "Success",
  "sheet_url": "https://sheets.google.com/test",
  "sheet_id": "123456"
}

@pytest.fixture
def mock_get_method():
  with mock.patch("services.agents.agent_tools.get_method") as mock_get:
    mock_get.return_value.json.return_value = {"fields": MOCK_RULESET_FIELDS}
    yield mock_get

@pytest.fixture
def mock_post_method():
  with mock.patch("services.agents.agent_tools.post_method") as mock_post:
    mock_post.return_value.json.return_value = {"fields": MOCK_RULESET_RESULT}
    yield mock_post

def test_agent_tool_decorator():
  """Test that the agent_tool decorator properly registers tools"""

  @agent_tool()
  def test_tool_with_description():
    """This is a test tool"""
    return "test result"

  @agent_tool()
  def test_tool_with_docstring():
    """This is a test tool with a docstring"""
    return "test result"

  assert "test_tool_with_description" in agent_tool_registry
  assert "test_tool_with_docstring" in agent_tool_registry
  assert callable(agent_tool_registry["test_tool_with_description"])
  assert callable(agent_tool_registry["test_tool_with_docstring"])

def test_rules_engine_get_ruleset_fields(mock_get_method):
  """Test getting ruleset fields from rules engine"""
  result = rules_engine_get_ruleset_fields("test_ruleset")
  assert result == MOCK_RULESET_FIELDS
  mock_get_method.assert_called_once()

def test_rules_engine_execute_ruleset(mock_post_method):
  """Test executing a ruleset"""
  test_inputs = {"income": 50000}
  result = rules_engine_execute_ruleset("test_ruleset", test_inputs)
  assert result == MOCK_RULESET_RESULT
  mock_post_method.assert_called_once()

def test_ruleset_input_tool(mock_get_method):
  """Test the ruleset input tool"""
  result = ruleset_input_tool("test_ruleset")
  assert result == MOCK_RULESET_FIELDS
  mock_get_method.assert_called_once()

def test_ruleset_execute_tool(mock_post_method):
  """Test the ruleset execute tool"""
  args = {
    "ruleset_name": "test_ruleset",
    "rule_inputs": {"income": 50000}
  }
  result = ruleset_execute_tool(args)
  assert result == MOCK_RULESET_RESULT
  mock_post_method.assert_called_once()

def test_gmail_tool(mock_post_method):
  """Test the Gmail tool"""
  mock_post_method.return_value.json.return_value = {
    "result": "Email sent", 
    "recipient": "test@example.com"
  }

  input_dict = {
    "recipients": ["test@example.com"],
    "subject": "Test Subject",
    "message": "Test Message"
  }

  result = gmail_tool(input_dict)

  assert "gmail_tool" in result
  assert "test@example.com" in result
  mock_post_method.assert_called_once()

def test_docs_tool(mock_post_method):
  """Test the Docs tool"""
  mock_response = {
    "subject": "Missing Income Verification",
    "message": "Please send your pay stub"
  }
  mock_post_method.return_value.json.return_value = mock_response

  input_dict = {
    "recipients": ["test@example.com"],
    "content": "Test content"
  }

  result = docs_tool(input_dict)

  assert result["subject"] == mock_response["subject"]
  assert result["message"] == mock_response["message"]
  mock_post_method.assert_called_once()

def test_google_sheets_tool(mock_post_method):
  """Test the Google Sheets tool"""
  mock_post_method.return_value.json.return_value = MOCK_SHEET_RESPONSE

  input_dict = {
    "name": "Test Sheet",
    "columns": ["Col1", "Col2"],
    "rows": [["data1", "data2"]],
    "user_email": "test@example.com"
  }

  result = google_sheets_tool(input_dict)

  assert result["sheet_url"] == MOCK_SHEET_RESPONSE["sheet_url"]
  assert result["sheet_id"] == MOCK_SHEET_RESPONSE["sheet_id"]
  mock_post_method.assert_called_once()

@mock.patch("services.agents.agent_tools.vertex_code_interpreter_tool")
def test_run_chat_tools_success(mock_vertex_tool):
  """Test run_chat_tools with successful execution"""
  mock_response = {
    "execution_error": None,
    "generated_code": "print('Hello')",
    "execution_result": "Hello",
    "output_files": [{"name": "test.png", "contents": "base64content"}]
  }
  mock_vertex_tool.return_value = mock_response

  response, files = run_chat_tools("Test prompt")

  assert "Code generated" in response
  assert "Hello" in response
  assert files == mock_response["output_files"]
  mock_vertex_tool.assert_called_once_with("Test prompt")

@mock.patch("services.agents.agent_tools.vertex_code_interpreter_tool")
def test_run_chat_tools_error(mock_vertex_tool):
  """Test run_chat_tools with execution error"""
  mock_response = {
    "execution_error": "Test error occurred",
    "generated_code": "",
    "execution_result": "",
    "output_files": None
  }
  mock_vertex_tool.return_value = mock_response

  response, files = run_chat_tools("Test prompt")

  assert response == "Test error occurred"
  assert files is None
  mock_vertex_tool.assert_called_once_with("Test prompt")

