# Authentication Service

## Setup

- Go to GCP console and [enable the Identity Platform](https://console.cloud.google.com/customer-identity).
  ![Enable IDP](../../.github/assets/idp_enable.png)

- Add a Email/Password provider [in Identity Platform page](https://console.cloud.google.com/customer-identity/providers):
  ![Add IDP provider](../../.github/assets/idp_add_provider.png)

- Run the command below to set the environment variable `FIREBASE_API_KEY`, this will be passed into the Authentication microservice pod when deploying.
  ```
  # Retrieve the default API key generated from the Terraform stage `2-foundation` automatically.

  KEY_NAME=$(gcloud alpha services api-keys list --filter="displayName='API Key for Identity Platform'" --format="value(name)")
  export FIREBASE_API_KEY=$(gcloud alpha services api-keys get-key-string ${KEY_NAME} --format="value(keyString)")
  echo $FIREBASE_API_KEY
  ```
