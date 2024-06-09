# Set up CI/CD on Github

The .githib directory in the repo contains template workflow files to create a CI/CD pipeline for the platform.  This enables linting, unit and e2e tests to run on PRs, and continuous deployment to a dev environment upon successful execution of the tests.

## Configure github environment

There are several variables that are used by the Github workflows.  These must be configured in an "environment" associated with the repo.  See [the Github docs](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) for more information on deployment environments.

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
```

## Github deployment credentials
The following line in the Github deployment workflow refers to an environment secret needed to enable Github actions to deploy to your project:

```
          credentials_json: ${{ secrets.GCP_CREDENTIALS }}
```

You should create this secret in the github environment populated with a service account key.  Generate a sevice account key from the `deployment@<project_id>.iam.gserviceaccount.com` service account that is created by the platform install process.
