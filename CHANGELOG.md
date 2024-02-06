## Releases

v0.2.0

Features:

### GENIE ("GenAI for Enterprise" platform on GCP)

- Chat, text generation and embeddings using Vertex models (Feb 2024) and Langchain supported LLMs
- Basic RAG pipeline using AlloyDB / PGVector (recommended) or Vertex Matching Engine as vector store. Supports web-based datasources and GCS as a data source.
- Agents using Langchain
- Agent tool examples: send email using gmail, create spreadsheets, consult a rules engine
- DB Agents to retrieve data from SQL databases
- Basic UX in Streamlit and Flutterflow (see READMEs in those components for details)
- Support for Llama2 via Truss (experimental)

### Core Solution Services
- Authentication
- User Management
- Rules Engine
- Job Service
