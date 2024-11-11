# Releases

## v0.4.0

New features:

### GENIE ("GenAI for Enterprise" platform on GCP)
- Multimodal RAG for images using multi-modal embeddings for search
- Chat file upload in both backend and React app.  Upload files or specify URLs to pass to model.
- RBAC for model access.  See README for LLM Service for docs on how to manage access to models for users.
- Added user role management in React frontend, used for RBAC for models and query engines
- Added documentation on authentication in the platform in docs/AUTH.md
- Updated to recent releases of FastAPI (0.112.2) and associated libraries
- Use L4 GPUs with Truss models
- Chunk size and chunking class are now query engine build params
- Add chunk size to React Query Admin engine build form
- Switched to using llama_index.core.node_parser.SentenceSplitter for chunking by default
- Updated default query generation model to Gemini Flash 1.5 - was set to Palm2
- Added Microsoft login in React frontend
- Add webscraping component written in Go for performance. Used for web data query engines with depth > 0.
- Add timestamps to logging
- New deploy script for React frontend

### Fixes
- Fixed download of PDFs from scraped sites
- Fixed deletion of query engines in React frontend; made hard delete the default


## v0.3.2

New features:

### GENIE ("GenAI for Enterprise" platform on GCP)
- Remove tools_service from default ingress and install instructions
- Updated install guide to emphasize that React UX is recommended over Flutterflow and Streamlit
- Add instructions for deploying Gemma 2B LLM service to GENIE

### Fixes
- Corrected README for React frontend to instruct to build app after setting config


## v0.3.1

New features:

### GENIE ("GenAI for Enterprise" platform on GCP)
- Deploy using artifact registry
- Add Query Engine Admin in React Frontend to create new Query Engines, view build jobs
- Support basic query filters for GENIE (non-Vertex Search) Query Engines
- Support basic RBAC on documents in GENIE query engines
- Add script to install postgres with Cloud SQL

### Fixes
- Update to build and deploy process to fix Container registry deprecation which was causing deploys to fail in new projects.
- Fix embedding generation bug causing documents to fail to be indexed

## v0.3.0

New features:

### GENIE ("GenAI for Enterprise" platform on GCP)

- Add VertexSearch query engine type, using Vertex Search to index data and perform RAG retrieval
- Add Integrated Search query engine type, allowing RAG retrieval across query engines
- Add new React-based frontend app (see [README](./components/frontend_react/README.md) to install and deploy)
- RAG: Significant improvements to chunking; now checking context window length for generation
- Integrate with LlamaIndex for chunking and data connectors
- Update langchain libraries (April 2024)
- Add SharePoint/OneDrive data connector, support SharePoint data sources
- Improved agent dispatch using langchain LLMRouterChain
- Background job-based queries, agent dispatch and agent runs
- Add support for Huggingface embeddings
- Support multimodal embeddings
- Support multimodel llm generation with Gemini
- Include instructions to upgrade/resize llm-service node pool

### Core Solution Services
- Create separate common_ml image to improve build/deploy times for LLM Service
- Pin version of firestore emulator used in unit tests and deploy. Requires firestore emulator to be started manually for unit tests.
- Create an environment variable profile on the jumphost during install
- Add documentation for setting up the CI/CD pipeline in Github

### Fixes
- Vertex embeddings now check token length limit, and use latest guidance on API max chunks and rate limits
- Allow DbAgent to be called directly via agent run endpoint
- Do not require OpenAI api key for default install

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
