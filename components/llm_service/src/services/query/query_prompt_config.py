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
Query prompt templates
"""

from langchain.prompts import PromptTemplate

#SC240930: May need to fix for multimodal - how does new chat route do it?
#SC240930: No, leave as-is.  Prompt will stay text only.  Will built up list of image_urls later, to pass into llM_chat along with the question prompt.
prompt_template = """
You are a helpful and truthful AI Assistant.
Use the following pieces of context and the chat history to answer the question at the end.
Do not answer anything other than the final question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context}

Chat History:
{chat_history}

Question: {question}
Helpful Answer:"""

#SC240930: May need to fix for multimodal - how does new chat route do it?
#SC240930: INPUT: prompt is always a string
#SC240930: INPUT: chat_history is always a string
#SC240930: INPUT: text_context is always a string
#SC240930: NEW INPUT: Need to provide a list of chunk_urls, for those QueryReferences that are images
#SC240930: No, leave as-is.  Prompt will stay text only.  Will built up list of image_urls later, to pass into llM_chat along with the question prompt.

#SC240930: OUTPUT: What is QUESTION_PROMPT? It's an instance of class PromptTemplate, which inherits
#SC240930: from StringPromptTemplate, which inherits from BasePromptTemplate, which is part of
#SC240930: langchain_core.prompts
QUESTION_PROMPT = PromptTemplate(
    template=prompt_template, input_variables=[
        "context", "chat_history", "question"
    ]
)

#SC240930: May need to fix for multimodal - how does new chat route do it?
#SC240930: Don't bother.  Multimodal moat around Gemini.
llama2_prompt_template = """
[INST]<<SYS>>You are a helpful and truthful AI search assistant for NASA.
Only respond to the final Human input at the end.
Use the following pieces of context to answer the question at the end.
If the answer is not in the context provided,
just say that you don't know, don't try to make up an answer.<</SYS>>

{context}

{chat_history}

Human input: {question}[/INST]"""

#SC240930: May need to fix for multimodal - how does new chat route do it?
#SC240930: Don't bother.  Multimodal moat around Gemini.
LLAMA2_QUESTION_PROMPT = PromptTemplate(
    template=llama2_prompt_template, input_variables=[
        "context", "chat_history", "question"
    ]
)

summary_template = """
Summarize the following text in three sentences or less:
{original_text}
"""

SUMMARY_PROMPT = PromptTemplate(
    template=summary_template, input_variables=["original_text"]
)
