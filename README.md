# Core Solution Services

> This codebase is generated from https://github.com/GoogleCloudPlatform/solutions-builder

Core Solution Services (CSS) is a group of foundational microservices, data models and other features, implemented in Python and running on Kubernetes. It supports common functionality needed by solutions built for different industries, like authentication, user management, data storage, and job management, and includes CI/CD using Github Actions and e2e testing.  CSS may be used as a stand-alone platform, or as a foundational layer to accelerate the building of specific applications.  It also includes a generic capability for GenAI use cases.  To date the microservices in CSS have been deployed in production for a variety of customers in the Public Sector division of Google Cloud.

## Use Cases

We have built an initial use case to support GenAI for Enterprise (GENIE).  GENIE is used as the foundation platform for other GenAI solutions in Google Cloud Public Sector.

### GenAI for Enterprise (GENIE)

We are building core services used for GenAI and Enterprise Search use cases, with built-in flexibility to leverage a number of LLMs like VertexAI (Gemini, Palm2), ChatGPT 3.5/4, Cohere, and more to come.

Highlighted features:

- Enable any enterprise to leverage a chatbot to answer questions using Retrieval Augmented Generation (RAG), based on configured content such as a collection of documents, websites, or databases.
- Support for Vertex model APIs and Vertex Model Garden.
- Easy plug in and use of LLM models available in the market, leveraging [Langchain](https://www.langchain.com/) as a model interface layer.
- Configurable agents based on Langchain.
- A built-in frontend app (using [Streamlit](https://streamlit.io/)) to showcase end-to-end user journeys.
- Cross-platform frontend application powered by [FlutterFlow](https://flutterflow.io/) that delivers end-to-end user flows and seamless digital experience on Android, iOS, web, and desktop platforms.

## Releases

Consult the [CHANGELOG](./CHANGELOG.md) for release information.  The current stable release of Core Solution Services is `v0.2.0`

## Quickstart (for GENIE)

To test the GenAI capabilities in Core Solution Services, we suggest you use Jupyter notebooks. There are several notebooks included in the platform (though be aware these are currently development aids and not polished).

1. Clone the repo locally

2. Create and activate a python 3.9 virtual environment in the LLM Service component.

In the top level directory of the repo:

```
cd components/llm_service
python3 -m venv .venv
source .venv/bin/activate
```

3. Install python requirements

```
pip install -r ../common/src/requirements.txt
pip install -r requirements.txt
pip install jupyter
```

4. Start a notebook server in the notebooks folder

```
cd notebooks
jupyter notebook
```

5. Open one of the notebooks and start experimenting with the libraries and APIs.


## Installing

Please follow the [INSTALL](./INSTALL.md) guide to install the platform. Note we strongly suggest you use a new GCP project to do this.  We also recommend you have the ability to update certain policies for your GCP Organization.

## Development

Please refer to the [DEVELOPMENT](./docs/DEVELOPMENT.md) guide to develop on the platform.
