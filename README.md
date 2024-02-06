# Core Solution Services

> This codebase is generated from https://github.com/GoogleCloudPlatform/solutions-builder

Core Solution Services (CSS) is a group of foundational microservices, data models and other features,
implemented in Python and running on Kubernetes. It supports common functionality needed by solutions
built for different industries, like authentication, user management, data storage, and job management,
and includes CI/CD and e2e testing.  CSS may be used as a stand-alone platform, or as a foundational layer
to accelerate the building of specific applications.  It also includes a generic capability for GenAI
use cases.  To date the microservices in CSS have been deployed in production for a variety of customers
in the Public Sector division of Google Cloud.

## Use Cases

We have built an initial use case to support GenAI for Enterprise, and there will be more use
cases to come soon.

### GenAI for Enterprise (GENIE)

We are building core services used for GenAI and Enterprise Search use cases, with built-in
flexibility to leverage a number of LLMs like VertexAI, ChatGPT 3.5/4, Cohere, and more to come.

Highlighted features:

- Enable any enterprise to leverage a chatbot to answer any questions based on their selected
  content such as a list of documents, databases, etc.
- Easy to plug in and use any LLM models available in the market, leveraging Langchain.
- A built-in frontend app (using [Streamlit](https://streamlit.io/)) to showcase end-to-end user journeys.
- Cross-platform frontend application powered by [FlutterFlow](https://flutterflow.io/) that delivers end-to-end user flows and seamless digital experience on Android, iOS, web, and desktop platforms.

## Releases

Consult the CHANGELOG for release information.  The current stable release of CSS is v0.0.2.

## Quickstart (for GENIE)

To access the GenAI capabilities in Core Solution Services, we suggest you use Jupyter notebooks.  There are several notebooks included in the platform (though be aware these are currently development aids and not polished).

1. Clone the repo locally

1. Create and activate a python 3.9 virtual environment in the LLM Service component.

In the top level directory of the repo:

```
cd components/llm_service
python3 -m venv .venv
source .venv/bin/activate
```

1. Install python requirements

```
pip install -r ../common/src/requirements.txt
pip install -r requirements.txt
pip install jupyter
```

1. Start a notebook server in the notebooks folder

```
cd notebooks
jupyter notebook
```

1. Open one of the notebooks and start experimenting with the libraries and APIs.


## Installing

Please follow the [INSTALL](./INSTALL.md) guide to install the platform. Note we stringly suggest you use a new GCP project to do this.  We also recommend you have the ability to update GCP Org policies.

## Development

Please refer to the [DEVELOPMENT](./INSTALL.md) guide to develop on the platform.

