# Releases

## v0.3.0

New features:

### GENIE ("GenAI for Enterprise" platform on GCP)

- Add VertexSearch query engine type, using Vertex Search to index data and perform RAG retrieval
- Add Integrated Search query engine type, allowing RAG retrieval across query engines
- RAG: Significant improvements to chunking; now checking context window length
- Integrate with LlamaIndex for chunking, data connectors
- Update to latest langchain libraries (April 2024)
- Add SharePoint/OneDrive data connector, support SharePoint data sources
- Improved agent dispatch using langchain LLMRouterChain
- Background job-based queries and agent dispatch
- Add support for Huggingface embeddings

### Core Solution Services
- Create separate common_ml image to improve build/deploy times for LLM Service
- Pin version of firestore emulator used in unit tests and deploy. Requires firestore emulator to be started manually for unit tests.

### Known Issues
- e2e testing not currently enabled
- Some known install issues (see [INSTALL](./INSTALL.md) guide)

## v0.2.0

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

### Known Issues
- e2e testing not currently enabled
- Some known install issues (see [INSTALL](./INSTALL.md) guide)
- Flutterflow UX not deploying successfully
