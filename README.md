# cloud-core-services

> This codebase is generated from https://github.com/GoogleCloudPlatform/solutions-template

## Prerequisite

| Tool | Required Version | Installation |
|---|---|---|
| Python     | &gt;= 3.9     | |
| gcloud CLI | Latest        | https://cloud.google.com/sdk/docs/install |
| Terraform  | &gt;= v1.3.7  | https://developer.hashicorp.com/terraform/downloads |
| Skaffold   | &gt;= v2.4.0  | https://skaffold.dev/docs/install/ |
| Kustomize   | &gt;= v5.0.0 | https://kubectl.docs.kubernetes.io/installation/kustomize/ |


## Setting up Google Cloud project

There are two options to set up your Google Cloud project.
- [Setting up Google Cloud Project](docs/INSTALLATION.md#SettingupGoogleCloudProject)
- [Setting up Google Cloud Project (Manual Steps)](#SettingupGoogleCloudProjectManualSteps)

Please refer to [INSTALLATION.md](docs/INSTALLATION.md) for more details.

## Deployment

### Install Solutions Template package
```
pip install -U solutions-template
```

### First time setup

```
gcloud auth login
gcloud auth application-default login
gcloud config set project $PROJECT_ID
st infra init
```

### Set up GKE cluster

```
st infra apply 2-gke
```

### Deploy microservices to GKE cluster

```
st deploy
```

## Development

Please refer to [DEVELOPMENT.md](docs/DEVELOPMENT.md) for more details on development and code submission.

## Troubleshoot

Please refer to [TROUBLESHOOT.md](docs/DEVELOPMENT.md) for more details on development and code submission.

