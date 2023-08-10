# Authentication Service

## Setup

Retrieve the default API key for Identity Platform. This API key is generated from the Terraform stage `2-foundation` automatically.

```
KEY_NAME=$(gcloud alpha services api-keys list --filter="displayName='API Key for Identity Platform'" --format="value(name)")
```

Set the environment variable `FIREBASE_API_KEY`, this will be passed into the Authentication microservice pod when deploying.
```
export FIREBASE_API_KEY=$(gcloud alpha services api-keys get-key-string ${KEY_NAME} --format="value(keyString)")
echo $FIREBASE_API_KEY
```
