# cloud-core-services

> This codebase is generated from https://github.com/GoogleCloudPlatform/solutions-template

## Setting up Google Cloud project

There are two options to set up your Google Cloud project.
- [Setting up Google Cloud Project](docs/INSTALLATION.md#SettingupGoogleCloudProject)
- [Setting up Google Cloud Project (Manual Steps)](#SettingupGoogleCloudProjectManualSteps)

Please refer to [INSTALLATION.md](docs/INSTALLATION.md) for more details.

## Deployment

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

