# Large Language Module Service

## Setup

Create the empty-value secrets:
```
gcloud secrets create "openai-api-key"
gcloud secrets create "cohere-api-key"
```

Run the following to update API Keys to Cloud Secret.

```
export OPENAI_API_KEY=<Your API key>
echo $OPENAI_API_KEY | gcloud secrets versions add "openai-api-key" --data-file=-

export COHERE_API_KEY=<Your API key>
echo $COHERE_API_KEY | gcloud secrets versions add "cohere-api-key" --data-file=-
```
