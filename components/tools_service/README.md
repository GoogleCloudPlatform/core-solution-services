# Tools Service

The microservice with a collection of tools and 3rd party integration.

## Tools

### Gmail Service

#### Setup

Before deployment, add the following to the Secrets Manager:
- *tools-gmail-client-secret*: Follow [this official guide](https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application) to create a new OAuth client ID, and generate a new credential JSON file.
- *tools-gmail-oauth-token*: Generate a new OAuth token for the specific user as the sender.


Run the following to add the following to the Secrets Manager:
```
# Create and set secret "tools-gmail-client-secret"
gcloud secrets create "tools-gmail-client-secret"
cat <path/to/client_secrets.json> | gcloud secrets versions add "tools-gmail-client-secre" --data-file=-

# Create and set secret "tools-gmail-oauth-token"
gcloud secrets create "tools-gmail-oauth-token"
cat <path/to/token.json> | gcloud secrets versions add "tools-gmail-client-secre" --data-file=-
```
