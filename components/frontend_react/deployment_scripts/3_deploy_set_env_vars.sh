#!/bin/bash
set -e

# DOMAIN_NAME and CONTACT_EMAIL are set in the main script

# Ensure required variables are accessible
if [ -z "$DOMAIN_NAME" ]; then
  echo "Error: DOMAIN_NAME environment variable is not set."
  exit 1
fi

if [ -z "$CONTACT_EMAIL" ]; then
  echo "Warning: CONTACT_EMAIL environment variable is not set. Using default value."
  CONTACT_EMAIL="contact@example.com"
fi

# Extract values from sdkconfig.json
echo "Extracting values from sdkconfig.json..."
if [ ! -f "sdkconfig.json" ]; then
  echo "Error: sdkconfig.json file not found. Run the Firebase configuration script first."
  exit 1
fi

JSON_CONTENT=$(cat sdkconfig.json)
PROJECT_ID=$(echo "$JSON_CONTENT" | jq -r '.projectId')
APP_ID=$(echo "$JSON_CONTENT" | jq -r '.appId')
STORAGE_BUCKET=$(echo "$JSON_CONTENT" | jq -r '.storageBucket')
API_KEY=$(echo "$JSON_CONTENT" | jq -r '.apiKey')
AUTH_DOMAIN=$(echo "$JSON_CONTENT" | jq -r '.authDomain')
MESSAGING_SENDER_ID=$(echo "$JSON_CONTENT" | jq -r '.messagingSenderId')

# Validate extracted values
for VAR in PROJECT_ID APP_ID STORAGE_BUCKET API_KEY AUTH_DOMAIN MESSAGING_SENDER_ID; do
  if [ -z "${!VAR}" ]; then
    echo "Error: Failed to extract $VAR from sdkconfig.json"
    exit 1
  fi
done

# Populate .env.production and .env.development
echo "Populating environment files..."
cat <<EOL > .env.production
VITE_FIREBASE_PUBLIC_API_KEY=$API_KEY
VITE_FIREBASE_AUTH_DOMAIN=$AUTH_DOMAIN
VITE_FIREBASE_PROJECT_ID=$PROJECT_ID
VITE_FIREBASE_STORAGE_BUCKET=$STORAGE_BUCKET
VITE_FIREBASE_MESSAGING_SENDER_ID=$MESSAGING_SENDER_ID
VITE_FIREBASE_APP_ID=$APP_ID
VITE_PUBLIC_CONTACT_US_EMAIL=$CONTACT_EMAIL
VITE_PUBLIC_API_ENDPOINT=https://$DOMAIN_NAME/llm-service/api/v1
VITE_PUBLIC_API_JOBS_ENDPOINT=https://$DOMAIN_NAME/jobs-service/api/v1
EOL

cp .env.production .env.development

echo "Environment configuration completed successfully."