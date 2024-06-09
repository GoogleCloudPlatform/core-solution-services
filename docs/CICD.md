# Set up CI/CD on Github

The .githib directory in the repo contains template workflow files to create a CI/CD pipeline for the platform.  This enables linting, unit and e2e tests to run on PRs, and continuous deployment to a dev environment upon successful execution of the tests.

## Rename "master" to "main"
Our Gihub actions refer to the "main" branch.  We recommend you [rename your "master" branch to "main"](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/changing-the-default-branch).

## Workflow files

### Deployment workflows
There are two deployment workflow files included in the repo, one for "develop" and one for "demo":

```
.github/workflows/deployment_gke_develop.yaml
.github/workflows/deployment_gke_demo.yaml
```

In a typical development process developers will deploy and test in a development environment, and periodically (say at the end of every sprint) a manual deployment will be made to a stable "demo" environment.  So typically CI/CD will only be enabled for the development environment.

In the workflow file `.github/workflows/deployment_gke_develop.yaml` you have the following configuration:

```
on:
  push:
    branches:
      - main
    paths:
      - ".github/workflows/deployment_gke_develop.yaml"
      - "components/**"
      - "ingress/**"
      - "utils/**"
```

This tells Github Actions to run this workflow on every push to the repo on the "main" branch.  So when PRs are merged to main the workflow will run and reploy to your development environment.

### Unit test and linting workflows
There are workflow files included for each service that run linting and unit tests on that service:  

```
.github/workflows/unit_test_linter_llm_service.yaml
.github/workflows/unit_test_linter_jobs_service.yaml
.github/workflows/unit_test_linter_rules_service.yaml
.github/workflows/unit_test_linter_tools_service.yaml
.github/workflows/unit_test_linter_user_management.yaml
.github/workflows/unit_test_linter_authentication.yaml
```

These are set up by default to run on pull requests to the main branch, according to this config in the workflow files:

```
on:
  pull_request:
    branches:
      - main
    paths:
      - "components/common/**"
      - "components/common_ml/**"
      - "components/llm_service/**"
      - ".github/workflows/unit_test_linter_llm_service.yaml"
      - ".pylintrc"
      - "!components/llm_service/**.md"
```

A common workflow for developers is to generate a draft PR for a new feature branch from their fork, to enable linting and unit tests to run when they push commits to that branch in their fork.

### e2e workflow
> Note the e2e workflows are currently not enabled.

This workflow file will execute e2e tests.  End-to-end tests are designed to perform integration tests based on user journeys.  This feature will be enabled in future releases of the platform.

## Configure github environment

There are several variables that are used by the Github workflows.  These must be configured in an "environment" associated with the repo.  See [the Github docs](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) for more information on deployment environments.

The Gihub environment name used by the workflow is referred to in the following line of the workflow files:

```
    environment: develop
```

You can create different deployment environments (say for a test environment, or a staging environment) by making a copy of the "develop" workflow file.

The `deploment_gke_develop.yaml` file in the workflows directory refers to the following variables.  These need to be configured in the Github environment. Each of these also corresponds to an environment variable used by Core Solution Services.  This set of environment variables is stored in the `/etc/profile.d/genie_env.sh` file on the jump host for manual deployment, and also needs to be replicated in the Github environment to enable automated deployment via CI/CD.

```
  PROJECT_ID: ${{ vars.PROJECT_ID }}
  SKAFFOLD_NAMESPACE: ${{ vars.GKE_NAMESPACE }}
  DOMAIN_NAME: ${{ vars.DOMAIN_NAME }}
  CORS_ALLOW_ORIGINS: ${{ vars.CORS_ALLOW_ORIGINS }}
  AGENT_CONFIG_PATH: ${{ vars.AGENT_CONFIG_PATH }}
  ONEDRIVE_CLIENT_ID: ${{ vars.ONEDRIVE_CLIENT_ID }}
  ONEDRIVE_TENANT_ID: ${{ vars.ONEDRIVE_TENANT_ID }}
  PG_HOST: ${{ vars.PG_HOST }}
  AUTH_AUTO_CREATE_USERS: ${{ vars.AUTH_AUTO_CREATE_USERS }}
  AUTH_EMAIL_DOMAINS_WHITELIST: ${{ vars.AUTH_EMAIL_DOMAINS_WHITELIST }}
```

## Github deployment credentials
The following line in the Github deployment workflow refers to an environment secret needed to enable Github actions to deploy to your project:

```
          credentials_json: ${{ secrets.GCP_CREDENTIALS }}
```

You should create this secret in the github environment populated with a service account key.  Generate a sevice account key from the `deployment@<project_id>.iam.gserviceaccount.com` service account that is created by the platform install process.
