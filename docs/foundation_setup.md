# Core Solution Services - GKE Foundation Setup

## Prerequisite

| Tool                | Required Version | Installation                                                                                                                                                                                        |
|---------------------|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `python`            | `>= 3.9`         | [Mac](https://www.python.org/ftp/python/3.9.13/python-3.9.13-macos11.pkg) • [Windows](https://www.python.org/downloads/release/python-3918/) • [Linux](https://docs.python.org/3.9/using/unix.html) |
| `gcloud` CLI        | `Latest`         | https://cloud.google.com/sdk/docs/install                                                                                                                                                           |
| `terraform`         | `>= v1.3.7`      | https://developer.hashicorp.com/terraform/downloads                                                                                                                                                 |
| `solutions-builder` | `>= v1.17.0`     | https://pypi.org/project/solutions-builder/                                                                                                                                                         |
| `skaffold`          | `>= v2.4.0`      | https://skaffold.dev/docs/install/                                                                                                                                                                  |
| `kustomize`         | `>= v5.0.0`      | https://kubectl.docs.kubernetes.io/installation/kustomize/                                                                                                                                          |

## Setup

### Create a new Google Cloud project

We'd recommend starting from a brand new GCP project. Create a new GCP project at [https://console.cloud.google.com/projectcreate]

### Install Solutions Builder package
```
pip install -U solutions-builder
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
sb set project-id $PROJECT_ID
sb infra apply 1-bootstrap
```

Enable Cloud Identity Platform (For Authentication)
- https://console.cloud.google.com/marketplace/details/google-cloud-platform/customer-identity


Set up Cloud foundation and GKE cluster
```
sb infra apply 2-foundation
sb infra apply 3-gke
```

### Add a HTTP Load balancer with DNS domain
```
sb components add terraform_gke_ingress
```

Update the following questions in the prompt:
- Cluster external endpoint IP address?
  - (The IP address will be automatically retrieved)
- Kubernetes service names in ingress? (comma-separated string)
  - **authentication,user-management**
- DNS domains (comma-separated string)?
  - (Your DNS domain)
  > Note: You can leave a dummy DNS domain if you don't have any custom domains. If so, you'd use IP address to connect to API endpoints later on.

Apply terraform for GKE ingress and LLM service:
```
sb infra apply 3-gke-ingress
```
- This will create a GCE load balancer with ingress.
- This will create a `$PROJECT_ID-llm-docs` bucket and upload the sample doc `llm-sample-doc.pdf` to it.
- It will add required Firestore indexes.

(Optional) Add an A record to your DNS:
![Alt text](../.github/assets/dns_a_record.png)
- Set the IP address to the external IP address in the ingress.

## Deploy

### Before Deploy

Follow README files of each microservice to setup:
- Authentication [components/authentication/README.md](../components/authentication/README.md)

### Deploy all microservices and ingress to GKE cluster:
```
sb deploy
```

### After deployment

- Follow [components/authentication/README.md#create-users](../components/authentication/README.md#create-users) to create the first user.
  - You will need the output ID Token for the next step.

### Verify deployment

Once deployed, check out the API docs with the following links:
- https://$YOUR_DNS_DOMAIN/authentication/api/v1/docs
- https://$YOUR_DNS_DOMAIN/user-management/api/v1/docs

> Alternative you can link with IP address e.g. http://x.x.x.x/authentication/api/v1/docs to verify API endpoints.
