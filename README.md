# Core Solution Services

> This codebase is generated from https://github.com/GoogleCloudPlatform/solutions-template

## Prerequisite

| Tool | Required Version | Installation |
|---|---|---|
| Python                 | &gt;= 3.9     | |
| gcloud CLI             | Latest        | https://cloud.google.com/sdk/docs/install |
| Terraform              | &gt;= v1.3.7  | https://developer.hashicorp.com/terraform/downloads |
| Skaffold               | &gt;= v2.4.0  | https://skaffold.dev/docs/install/ |
| Kustomize              | &gt;= v5.0.0  | https://kubectl.docs.kubernetes.io/installation/kustomize/ |
| solutions-template CLI | &gt;= v1.13.0 | https://github.com/GoogleCloudPlatform/solutions-template |

## Setup

### Create a new Google Cloud project

We'd recommend starting from a brand new GCP project. Create a new GCP project at [https://console.cloud.google.com/projectcreate]

### Install Solutions Template package
```
pip install -U solutions-template
```

### Set up gcloud CLI
```
export PROJECT_ID=<my-project-id>
gcloud auth login
gcloud auth application-default login
gcloud config set project $PROJECT_ID
```

Initialize the Cloud infra:
```
st set project-id $PROJECT_ID
st infra init
```

Set up GKE cluster

```
st infra apply 2-gke
```

### (Optional) Add a HTTP Load balancer with DNS domain
```
st components update terraform_gke_ingress
```

Update the following questions in the promopt:
```
🎤 Cluster external endpoint IP address?
   x.x.x.x
🎤 Kubernetes service names in ingress? (comma-separated string)
   authentication,jobs-service,llm-service,user-management
🎤 DNS domains (comma-separated string)?
   my.domain.com
```

Apply terraform for GKE ingress:
```
st infra apply 3-gke-ingress
```
## Deploy

### Set up each microservice:
- LLM Service: [components/llm_service/README.md]

### Deploy all microservices (optionally with Ingress) to GKE cluster:
```
st deploy
```

### Verify deployed APIs

TBD
