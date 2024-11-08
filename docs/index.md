# Documentation Index

Welcome to the documentation index for the project. Below you'll find links to various documentation files and README files for different components of the project.

## Main Documentation

- [CI/CD Setup](./CICD.md): Instructions for setting up CI/CD on GitHub, including workflow files and environment configuration.
- [Authentication](./AUTH.md): Details on the authentication scheme used in the CSS platform, including identity providers and token validation.
- [Configuration](./CONFIG.md): Information on configuring the LLMService Model, including provider, vendor, and model configurations.
- [Development](./DEVELOPMENT.md): Guidelines for setting up the development environment, code submission process, and testing.
- [Experimental LLM Truss](../experimental/llm_truss/README.md): Instructions for deploying LLMs into GKE, including Llama2-7b.
- [Experimental VLLM Gemma](../experimental/vllm_gemma/README.md): Guide for deploying Gemma 2B on a Kubernetes cluster with L4 GPUs.

## Component Documentation

### LLM Service

- [Query Engines](../components/llm_service/docs/QUERY_ENGINES.md): Overview of query engines, their types, and how to create and query them.
- [LLM Service README](../components/llm_service/README.md): Setup instructions for the LLM Service, including model vendors, optional models, and vector database configuration.

### Authentication Service

- [Authentication Service README](../components/authentication/README.md): Setup guide for enabling the Identity Platform and managing users.

### Tools Service

- [Tools Service README](../components/tools_service/README.md): Information on the tools and third-party integrations available in the Tools Service.

### Frontend React

- [Frontend React README](../components/frontend_react/README.md): Installation and deployment instructions for the GENIE React frontend, including identity provider configuration.

### Jobs Service

- [Jobs Service README](../components/jobs_service/README.md): Installation instructions for the Jobs Service.

## Additional Resources

- [GENIE React Frontend](../components/frontend_react/README.md): This component is a REACT-based frontend UI for GENIE. It includes installation instructions and prerequisites.
- [Deploying Gemma 2B](../experimental/vllm_gemma/README.md): Reference guide for deploying Gemma 2B using Kubernetes with GPU support.

Feel free to explore each document for more detailed information on setting up and using the various components of the project. 