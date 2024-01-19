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

""" Schema examples and test objects for unit tests """
# pylint: disable = line-too-long

LLM_GENERATE_EXAMPLE = {
  "llm_type": "",
  "prompt": "",
}

LLM_MULTI_GENERATE_EXAMPLE = {
  "llm_type": "",
  "prompt": ""
}

LLM_EMBEDDINGS_EXAMPLE = {
  "embedding_type": "",
  "text": "",
}

QUERY_EXAMPLE = {
  "prompt": "test prompt",
  "llm_type": "VertexAI-Chat",
  "sentence_references": False
}

USER_QUERY_EXAMPLE = {
  "id": "asd98798as7dhjgkjsdfh",
  "user_id": "fake-user-id",
  "title": "Test query",
#  "llm_type": "VertexAI-Chat",
  "query_engine_id": "asd98798as7dhjgkjsdfh",
  "history": [
    {"HumanQuestion": "test input 1"},
    {
      "AIResponse": "test response 1",
      "AIReferences": [
        {
          "query_engine_id": "asd98798as7dhjgkjsdfh",
          "query_engine": "query-engine-test",
          "document_id": "efghxxzzyy1234",
          "chunk_id": "abcdxxzzyy1234"
        }
      ]
    },
    {"HumanQuestion": "test input 2"},
    {
      "AIResponse": "test response 2",
      "AIReferences": [
        {
          "query_engine_id": "asd98798as7dhjgkjsdfh",
          "query_engine": "query-engine-test",
          "document_id": "efghxxzzyy5678",
          "chunk_id": "abcdxxzzyy5678"
        }
      ]
    }
  ]
}

QUERY_ENGINE_EXAMPLE = {
  "id": "asd98798as7dhjgkjsdfh",
  "name": "query-engine-test",
  "description": "sample description",
  "embedding_type": "VertexAI-Chat",
  "vector_store": "langchain_pgvector",
  "created_by": "fake-user-id",
  "is_public": True,
  "index_id": "projects/83285581741/locations/us-central1/indexes/682347240495461171",
  "index_name": "query_engine_test_MEindex",
  "endpoint": "projects/83285581741/locations/us-central1/indexEndpoints/420294037177840435"
}

QUERY_RESULT_EXAMPLE = {
  "id": "asd98798as7dhjgkjsdfh",
  "query_engine_id": "asd98798as7dhjgkjsdfh",
  "query_engine": "query-engine-test",
  "response": "test response",
  "query_refs": ["abcd1234", "defg5678"],
  "archived_at_timestamp": None,
  "archived_by": None,
  "created_by": "fake-user-id",
  "created_time": "2023-07-04 19:22:50.799741+00:00"
}

QUERY_DOCUMENT_EXAMPLE_1 = {
  "id": "asd98798as7dhjgkjsdfh1",
  "query_engine_id": "asd98798as7dhjgkjsdfh",
  "query_engine": "query-engine-test",
  "doc_url": "abcd.com/pdf1",
  "index_start": 0,
  "index_end": 123
}

QUERY_DOCUMENT_EXAMPLE_2 = {
  "id": "asd98798as7dhjgkjsdfh2",
  "query_engine_id": "asd98798as7dhjgkjsdfh",
  "query_engine": "query-engine-test",
  "doc_url": "abcd.com/pdf2",
  "index_start": 0,
  "index_end": 11
}

QUERY_DOCUMENT_EXAMPLE_3 = {
  "id": "asd98798as7dhjgkjsdfh3",
  "query_engine_id": "asd98798as7dhjgkjs",
  "query_engine": "query-engine-test",
  "doc_url": "abcd.com/pdf3",
  "index_start": 0,
  "index_end": 1234
}

QUERY_DOCUMENT_CHUNK_EXAMPLE_1 = {
  "id": "asd98798as7dhjhkkjhk1",
  "query_engine_id": "asd98798as7dhjgkjsdfh",
  "query_document_id": "asd98798as7dhjgkjsdfh1",
  "index": 0,
  "text": "<p>query_document_chunk_example_1</p>",
  "clean_text": "query_document_chunk_example_1",
  "sentences": ["query_document_chunk_example_1"]
}

QUERY_DOCUMENT_CHUNK_EXAMPLE_2 = {
  "id": "asd98798as7dhjhkkjhk12",
  "query_engine_id": "asd98798as7dhjgkjsdfh",
  "query_document_id": "asd98798as7dhjgkjsdfh1",
  "index": 1,
  "text": "<p>query_document_chunk_example_2</p>",
  "clean_text": "query_document_chunk_example_2",
  "sentences": ["query_document_chunk_example_2"]
}

QUERY_DOCUMENT_CHUNK_EXAMPLE_3 = {
  "id": "asd98798as7dhjhkkjhk13",
  "query_engine_id": "asd98798as7dhjgkjs",
  "query_document_id": "asd98798as7dhjgkjsdfh1",
  "index": 2,
  "text": "<p>query_document_chunk_example_3</p>",
  "clean_text": "query_document_chunk_example_3",
  "sentences": ["query_document_chunk_example_3"]
}

CHAT_EXAMPLE = {
  "id": "asd98798as7dhjgkjsdfh",
  "user_id": "fake-user-id",
  "title": "Test chat",
  "llm_type": "VertexAI-Chat",
  "history": [
    {"HumanInput": "test input 1"},
    {"AIOutput": "test response 1"},
    {"HumanInput": "test input 2"},
    {"AIOutput": "test response 2"}
  ],
  "created_time": "2023-05-05 09:22:49.843674+00:00",
  "last_modified_time": "2023-05-05 09:22:49.843674+00:00"
}

USER_EXAMPLE = {
    "id": "fake-user-id",
    "first_name": "Test",
    "last_name": "Tester",
    "user_id": "fake-user-id",
#    "auth_id": "fake-user-id",
    "email": "user@gmail.com",
#    "role": "Admin",
    "user_type": "user",
    "status": "active"
}

USER_PLAN_EXAMPLE = {
  "id": "fake-plan-id",
  "name": "example plan",
  "user_id": "fake-user-id",
  "task_prompt": "fake task prompt",
  "task_response": "fake task response",
  "agent_name": "Task",
  "plan_steps": ["fake-planstep-id-1", "fake-planstep-id-2"]
}

USER_PLAN_STEPS_EXAMPLE_1 = {
  "id": "fake-planstep-id-1",
  "user_id": "fake-user-id",
  "plan_id": "fake-plan-id",
  "description": "Use [fake tool] to [perform step description 1]",
  "agent_name": "Task"
}

USER_PLAN_STEPS_EXAMPLE_2 = {
  "id": "fake-planstep-id-2",
  "user_id": "fake-user-id",
  "plan_id": "fake-plan-id",
  "description": "Use [fake tool] to [perform step description 2]",
  "agent_name": "Task"
}

AGENT_RUN_EXAMPLE = {
  "prompt": "hello"
}

AGENT_RUN_RESPONSE_EXAMPLE = {
  "output": "hello",
  "chat": CHAT_EXAMPLE
}

AGENT_PLAN_EXAMPLE = {
  "prompt": "hello"
}

AGENT_PLAN_RESPONSE_EXAMPLE = {
  "output": "hello",
  "chat": CHAT_EXAMPLE,
  "plan": {
    "id": "fake-plan-id",
    "name": "example plan",
    "user_id": "fake-user-id",
    "agent_name": "Task",
    "plan_steps": [
      {
        "id": "fake-planstep-id-1",
        "description": "Use [fake tool] to [perform step description 1]",
      },
      {
        "id": "fake-planstep-id-2",
        "description": "Use [fake tool] to [perform step description 2]",
      }
    ]
  }
}

USER_PLAN_RESPONSE_EXAMPLE = USER_PLAN_EXAMPLE
