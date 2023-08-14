# Large Language Module Service

## Setup

### Before Deployment

Set API Keys to environment variables:
```
export OPENAI_API_KEY="<Your API key>"
export COHERE_API_KEY="<Your API key>"
```

Run the following to update API Keys to Cloud Secret.
```
gcloud secrets create "openai-api-key"
gcloud secrets create "cohere-api-key"
echo $OPENAI_API_KEY | gcloud secrets versions add "openai-api-key" --data-file=-
echo $COHERE_API_KEY | gcloud secrets versions add "cohere-api-key" --data-file=-
```

### After Deployment

Set up Cloud Storage with one sample PDF file for Query Engine to use later:
```
sb infra apply 3-llm
```
- This will create a `$PROJECT_ID-llm-docs` bucket and upload a `llm-sample-doc.pdf`.
- It will add required Firestore indexes.

Get the access token for a particular user:
```
BASE_URL=https://your.domain.com/
PYTHONPATH=components/common/src/ python components/authentication/src/utils/setup.py get_token --base-url=$BASE_URL
```
- This will print out the token in the terminal.

Run the following to build a Query engine:
```
ID_TOKEN=<the token printed above>
curl --location "https://css-test.cloudpssolutions.com/llm-service/api/v1/query/engine" \
--header "Content-Type: application/json" \
--header "Authorization: Bearer $ID_TOKEN" \
--data '{
    "doc_url": "gs://jonchen-css-0813-llm-docs/genai-sample-doc.pdf",
    "query_engine": "query-engine-test",
    "llm_type": "VertexAI-Chat",
    "is_public": true
}'
```

## Troubleshoot

### Deploy the microservice with live logs output in local terminal

To run a livereload service in the remote cluster and print logs in the local terminal:
```
sb deploy --component=llm_service --dev
```
- This will deploy the LLM service to the remote main cluster, and set up port forwarding with live reload from local source code.
- You can monitor all API requests and responses in the terminal output.

Once deployed, it will print logs from the microservice, e.g.
```
[llm-service] INFO:     Will watch for changes in these directories: ['/opt']
[llm-service] INFO:     Uvicorn running on http://0.0.0.0:80 (Press CTRL+C to quit)
[llm-service] INFO:     Started reloader process [1] using StatReload
[llm-service] INFO:     Started server process [8]
[llm-service] INFO:     Waiting for application startup.
[llm-service] INFO:     Application startup complete.
[llm-service] INFO:     35.191.8.94:32768 - "GET /ping HTTP/1.1" 200 OK
[llm-service] INFO:     35.191.8.64:32768 - "GET /ping HTTP/1.1" 200 OK
[llm-service] INFO:     35.191.8.66:44092 - "GET /ping HTTP/1.1" 200 OK
[llm-service] INFO:     10.1.1.1:55346 - "GET /ping HTTP/1.1" 200 OK
[llm-service] INFO:     10.1.1.1:55348 - "GET /ping HTTP/1.1" 200 OK
```

### Troubleshooting LLM Service - building a query engine

#### Received 403 error in LLM service

When sending the API call to https://$YOUR_DOMAIN/llm-service/api/v1/query/engine but received a 403 error. It could be one of the following reasons:

- The Kubenetes Role and Role Binding are not set correctly.
  - Check out the `components/llm_service/kustomize/base` folder, you will see role.yaml and role_binding.yaml. Make sure they exist.
  - Check the `kustomization.yaml` file and make sure the role.yaml and role_binding.yaml are in `resources` list. Orders don't matter.
  - Check out `role_binding.yaml` and ensure the Service Account name is exact `gke-sa`. This is defined in the `/terraform/stages/2-gke/main.tf`

#### Batch job created but no pod created.

If a batch job is created succesfully,

