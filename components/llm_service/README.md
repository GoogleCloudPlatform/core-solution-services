# Large Language Module Service

## Setup

### Setting up LLM model vendors (optional)
We support OpenAI and Cohere as API LLM vendors currently.  Additional vendors that are supported by langchain would be easy to add.

To add support for OpenAI or Cohere:

* Set API Keys to environment variables:

OpenAI
```
export OPENAI_API_KEY="<Your API key>"
```

Cohere

```
export COHERE_API_KEY="<Your API key>"
```

* Run the following to update API Keys to Cloud Secret:

OpenAI
```
gcloud secrets create "openai-api-key"
echo $OPENAI_API_KEY | gcloud secrets versions add "openai-api-key" --data-file=-
```

Cohere
```
gcloud secrets create "cohere-api-key"
echo $COHERE_API_KEY | gcloud secrets versions add "cohere-api-key" --data-file=-
```

* Update `models.json` to enable the vendor:

```
...

  "vendors": {
    "OpenAI": {
      "enabled": true,
      "api_key": "openai-api-key",
      "env_flag": "ENABLE_OPENAI_LLM"
    },
    "Cohere": {
      "enabled": true,
      "api_key": "cohere-api-key",
      "env_flag": "ENABLE_COHERE_LLM"
    }
  },

...

```

## Adding Optional LLM Models

### Llama2 Truss Deployment
Optionally deploy Llama2 using Truss following these [instructions](../../experimental/llm_truss/llama2-7b-sample/README.md).

To use deployed llama2 Endpoint (IP:PORT), set the following environment variable before deploying llm-service:


```shell
export ENABLE_TRUSS_LLAMA2=True
export TRUSS_LLAMA2_ENDPOINT = "truss-llama2-7b-service"
```

### Llama2 Vertex AI Deployment
You can deploy Llama2 using [Model Garden](https://cloud.google.com/model-garden?hl=en) in Vertex AI.
To use the online prediction endpoint, set the following environment variable before the deployment:

```shell
export REGION=<region-where-endpoint-is-deployed>
export MODEL_GARDEN_LLAMA2_CHAT_ENDPOINT_ID = "end-point-service-id"
```

## Set up PGVector Vector Database (using one of CloudSQL or AlloyDB)

Create a secret for postgreSQL password:

```shell
gcloud secrets create "postgres-user-passwd"
```

Store the password in the secret.  Note: use single quotes to enclose the password if the password contains special characters like '$'.
```shell
echo '<your-postgres-password>' | gcloud secrets versions add "postgres-user-passwd" --data-file=-
```

### PostgreSQL (Cloud SQL) as a vector database

Create a postgreSQL instance:
```
export INSTANCE_ID=${PROJECT_ID}-db

gcloud services enable sqladmin.googleapis.com

gcloud sql instances create ${INSTANCE_ID} \
  --database-version=POSTGRES_15 \
  --region=us-central1 \
  --tier=db-perf-optimized-N-2 \
  --edition=ENTERPRISE_PLUS \
  --enable-data-cache \
  --storage-size=250 \
  --network default-vpc \
  --enable-google-private-path \
  --availability-type=REGIONAL \
  --no-assign-ip

gcloud sql users set-password postgres \
  --instance=vectordb \
  --password=$(gcloud secrets versions access latest --secret="postgres-user-passwd")

export PG_HOST=$(gcloud sql instances list --format="value(PRIVATE_ADDRESS)")
```

### AlloyDB as a vector database

Run this script to create an AlloyDB instance:
```shell
./utils/alloy_db.sh
```

Set the IP address for database host from the output of the above script:
```shell
export PG_HOST=<alloydb-ip-address>
```

### Add PGVector extension

Create an ephemeral pod (auto-deleted) for running psql client:

```shell
kubectl run psql-client --rm -i --tty --image ubuntu -- bash
```

Once inside the temporary sql pod:

```commandline
apt update -y && apt install -y postgresql-client

export PGPASSWORD=<your-postgres-password>
export PGHOST=<pghost-ip-address>
psql -U postgres -c "CREATE DATABASE pgvector"
psql -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector"
exit
```

### Update environment vars profile with PG_HOST
Write to env vars profile:
```shell
sudo bash -c "echo 'export PG_HOST=${PG_HOST}' >> /etc/profile.d/genie_env.sh"
```


## After Deployment (optional)
This section includes optional steps to perform depending on your installation.

### Create a BOT account to authenticate to other services

This bot account is needed if you are using agents that use the Tools Service.  The LLM Service uses this account to authenticate to the Tools Service, to perform actions like sending emails or creating Sheets.

Create `llm-backend-robot-username` account for LLM service authentication:
```
# Setting BASE_URL Without trailing slash.
BASE_URL=https://your.domain.com
PYTHONPATH=components/common/src/ python components/authentication/scripts/user_tool.py create_bot_account --base-url=$BASE_URL
```

### Create a Query Engine
You can use the method below to create a query engine from the command line, to test your installation, or to ensure that at least one query engine is present.  Query Engines can also be created using the "Query Engines" page in streamlit.

Get the access token for a particular user:
```
# Setting BASE_URL Without trailing slash.
BASE_URL=https://your.domain.com
PYTHONPATH=components/common/src/ python components/authentication/scripts/user_tool.py get_token --base-url=$BASE_URL
```
- This will print out the token in the terminal.

Run the following to build a Query engine:
```
ID_TOKEN=<the token printed above>
QUERY_ENGINE_NAME="qe1"
curl --location "$BASE_URL/llm-service/api/v1/query/engine" \
--header "Content-Type: application/json" \
--header "Authorization: Bearer $ID_TOKEN" \
--data "{
    \"doc_url\": \"gs://$PROJECT_ID-llm-docs\",
    \"query_engine\": \"$QUERY_ENGINE_NAME\"
}"
```

This will create a Vertex AI Matching Engine Index. You can check out the progress on https://console.cloud.google.com/vertex-ai/matching-engine/indexes?referrer=search&project=$PROJECT_ID.
> Note: It may take 15+ minutes to create a Matching Engine Index.
> The Kubernetes Job may show time out while creating the Matching Engine and Endpoint in its logs, but the creation process will still be executed in the background.
> You will see the Endpoint created soon later.

Once finished, you shall see the following artifacts:
- A record in `query_engines` collection in Firestore, representing the new Query engine.
- A corresponding document metadata in `query_documents` collection in Firestore.
- A record in `query_document_chunk` collection in Firestore.
- A Vertex AI Matching Engine.

### Deploy with CORS origin allows

Set the CORS origin environment variable:
```
CORS_ALLOW_ORIGINS=http://localhost,http://localhost:8080,http://localhost:5173,https://your-domain.com
```

Deploy microservice to GKE cluster as usual.
```
sb deploy -n default -m llm_service
```

### Deploy with custom agent_config.json stored in a GCS bucket path.

Create a GCS bucket if it doesn't exist.
```
gcloud storage buckets create gs://${PROJECT_ID}-config
```

Upload the `agent_config.json` to a GCS bucket path:
```
gcloud storage cp /path/to/agent_config.json gs://${PROJECT_ID}-config
```
- You can refer to the `components/llm_service/src/config/agent_config.json` as the template to start with.

Verify if the file has uploaded correctly to the bucket.
```
gsutil list gs://${PROJECT_ID}-config/agent_config.json
```

Set up the environment variable `AGENT_CONFIG_PATH` accordingly:
- When deploying locally, set AGENT_CONFIG_PATH to the GCS path.
  ```
  export AGENT_CONFIG_PATH=gs://${PROJECT_ID}-config/agent_config.json
  ```
- When deploying with CI/CD like Github action, set the AGENT_CONFIG_PATH in the CI/CD's env vars.

> If AGENT_CONFIG_PATH is not set, it will fall back to use the default agent_config.json in
> `components/llm_service/src/config/agent_config.json`.

## Onedrive integration

To access Onedrive as a datasource, the following setup must be performed:

```shell
gcloud secrets create "onedrive-client-secret"
gcloud secrets create "onedrive-principle-name"

echo '<your-onedrive-client-secret>' | gcloud secrets versions add "onedrive-client-secret" --data-file=-

echo '<your-onedrive-principle-name>' | gcloud secrets versions add "onedrive-principle-name" --data-file=-
```

Prior to deploy you must set these env vars:
```
export ONEDRIVE_CLIENT_ID="<your-onedrive-client-id>"
export ONEDRIVE_TENANT_ID="<your-onedrive-tenant-id>"
```

Write these to the env vars profile so they are always set when you deploy from the jump host:
```shell
sudo bash -c "echo 'export ONEDRIVE_CLIENT_ID=${ONEDRIVE_CLIENT_ID}' >> /etc/profile.d/genie_env.sh"
sudo bash -c "echo 'export ONEDRIVE_TENANT_ID=${ONEDRIVE_TENANT_ID}' >> /etc/profile.d/genie_env.sh"
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

#### Monitor the batch job in Kubernetes Workloads

Once sending the API call to https://$YOUR_DOMAIN/llm-service/api/v1/query/engine, it will create a Kubernetes Job and a corresponding Firestore record in `batch_jobs` collections.
- Check the batch_job object in https://console.cloud.google.com/firestore/databases/-default-/data/panel/batch_jobs
- Check the Kubernetes Job in the Kubernetes Workload: https://console.cloud.google.com/kubernetes/workload/overview

In the Kubernetes Workload view, you'll see workloads with "Job" type.
- If the job is created and running succesfully, the status shall be "OK" or "Running".
- If you are seeing the status as "Error" or something else like "BackoffLimitExceeded", this means the Job failed.

Run the following to describe the job in the terminal:
```
kubectl describe job atestjob-1eab-4f55-9075-895ed6e86c24
```
- You'd see something like:
  ```
  Events:
  Type     Reason                Age   From            Message
  ----     ------                ----  ----            -------
  Normal   SuccessfulCreate      47m   job-controller  Created pod: atestjob-1eab-4f55-9075-895ed6e86c24-dtdlh
  Warning  BackoffLimitExceeded  47m   job-controller  Job has reached the specified backoff limit
  ```

Run the following to triage the logs from the failed pod:
```
kubectl logs atestjob-1eab-4f55-9075-895ed6e86c24-dtdlh
```

For example, it would print logs with error messages like below:
```
Traceback (most recent call last):
  File "/opt/run_batch_job.py", line 62, in <module>
    app.run(main)
  File "/usr/local/lib/python3.9/site-packages/absl/app.py", line 308, in run
    _run_main(main, args)
  File "/usr/local/lib/python3.9/site-packages/absl/app.py", line 254, in _run_main
    sys.exit(main(argv))
  File "/opt/run_batch_job.py", line 57, in main
    raise e
  File "/opt/run_batch_job.py", line 43, in main
    _ = batch_build_query_engine(request_body, job)
  File "/opt/services/query_service.py", line 189, in batch_build_query_engine
    query_engine_build(doc_url, query_engine, user_id, llm_type)
  File "/opt/services/query_service.py", line 255, in query_engine_build
    raise InternalServerError(e) from e
common.utils.http_exceptions.InternalServerError: 403 GET https://storage.googleapis.com/storage/v1/b/query-engine-test-me-data/o?maxResults=257&projection=noAcl&prettyPrint=false: gke-sa@test-project.iam.gserviceaccount.com does not have storage.objects.list access to the Google Cloud Storage bucket. Permission 'storage.objects.list' denied on resource (or it may not exist).
```
- In this example, it appeared to be the IAM permissions problem for the `gke-sa` service account.


#### Received 403 error in LLM service

When sending the API call to https://$YOUR_DOMAIN/llm-service/api/v1/query/engine but received a 403 error. It could be one of the following reasons:

- The Kubernetes Role and Role Binding are not set correctly.
  - Check out the `components/llm_service/kustomize/base` folder, you will see role.yaml and role_binding.yaml. Make sure they exist.
  - Check the `kustomization.yaml` file and make sure the role.yaml and role_binding.yaml are in `resources` list. Orders don't matter.
  - Check out `role_binding.yaml` and ensure the Service Account name is exact `gke-sa`. This is defined in the `/terraform/stages/2-gke/main.tf`

#### Batch job created but failed.

If a batch job is created successfully, but there's an error about creating a pod, run the following to triage kubernetes resources:

```
$ kubectl get jobs
NAME                                   COMPLETIONS   DURATION   AGE
d49bb762-4c0e-4972-abf9-5d284bd74597   0/1           3m57s      3m57s
```

```
$ kubectl describe job d49bb762-4c0e-4972-abf9-5d284bd74597

Pod Template:
  Labels:           batch.kubernetes.io/controller-uid=4107c701-3461-489a-8bc3-f52cb48a39e5
                    batch.kubernetes.io/job-name=d49bb762-4c0e-4972-abf9-5d284bd74597
                    controller-uid=4107c701-3461-489a-8bc3-f52cb48a39e5
                    job-name=d49bb762-4c0e-4972-abf9-5d284bd74597
  Service Account:  gke-sa
  Containers:
   jobcontainer:
    Image:      gcr.io/$PROJECT_ID/llm-service:1fd3ca9-dirty
    Port:       <none>
    Host Port:  <none>
    Command:
      python
      run_batch_job.py
    Args:
      --container_name
      d49bb762-4c0e-4972-abf9-5d284bd74597
    Limits:
      cpu:     3
      memory:  7000Mi
    Requests:
      cpu:     2
      memory:  5000Mi
    Environment:
      DATABASE_PREFIX:
      PROJECT_ID:         $PROJECT_ID
      ENABLE_OPENAI_LLM:  True
      ENABLE_COHERE_LLM:  True
      GCP_PROJECT:        $PROJECT_ID
    Mounts:               <none>
  Volumes:                <none>
Events:
  Type     Reason                Age    From            Message
  ----     ------                ----   ----            -------
  Normal   SuccessfulCreate      4m17s  job-controller  Created pod: d49bb762-4c0e-4972-abf9-5d284bd74597-l87wf
  Warning  BackoffLimitExceeded  4m8s   job-controller  Job has reached the specified backoff limit
```

Then describe the pod from the above output (listed in the Events at the end as `Created pod`) and see what's going on.
```
$ kubectl describe pod d49bb762-4c0e-4972-abf9-5d284bd74597-l87wf

...
Containers:
  jobcontainer:
    Container ID:  containerd://60eb1dde2b50c80515b0a0b6ff717beb970add98f9e3529f2bc34cb868159772
    Image:         gcr.io/$PROJECT_ID/llm-service:1fd3ca9-dirty
    Image ID:      gcr.io/$PROJECT_ID/llm-service@sha256:4b243b37d0457f2464161015b23dad48fe50937b3d509f627ac22668035319a5
    Port:          <none>
    Host Port:     <none>
    Command:
      python
      run_batch_job.py
    Args:
      --container_name
      d49bb762-4c0e-4972-abf9-5d284bd74597
    State:          Terminated
      Reason:       Error
      Exit Code:    1
      Started:      Mon, 14 Aug 2023 14:15:24 -0400
      Finished:     Mon, 14 Aug 2023 14:15:24 -0400
```

Now the pod seems get some error, run the following to check out logs (Or see logs in Stackdriver.)
```
kubectl logs d49bb762-4c0e-4972-abf9-5d284bd74597-l87wf
```
