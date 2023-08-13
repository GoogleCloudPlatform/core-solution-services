# Large Language Module Service

## Setup

Set API Keys to environment variables:
```
export OPENAI_API_KEY="<Your API key>"
export COHERE_API_KEY="<Your API key>"
```

Run the following to update API Keys to Cloud Secret.
```
gcloud secrets create "openai-api-key"
gcloud secrets create "cohere-api-key"
echo $OPENAI_API_KEY | gcloud secrets versions add "openai-api-key" --data-file=-
echo $COHERE_API_KEY | gcloud secrets versions add "cohere-api-key" --data-file=-
```
