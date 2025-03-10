#!/bin/bash

# Extract values from sdkconfig.json
echo "Extracting values from sdkconfig.json..."
JSON_CONTENT=$(cat sdkconfig.json)
PROJECT_ID=$(echo "$JSON_CONTENT" | jq -r '.projectId')
APP_ID=$(echo "$JSON_CONTENT" | jq -r '.appId')
STORAGE_BUCKET=$(echo "$JSON_CONTENT" | jq -r '.storageBucket')
API_KEY=$(echo "$JSON_CONTENT" | jq -r '.apiKey')
AUTH_DOMAIN=$(echo "$JSON_CONTENT" | jq -r '.authDomain')
MESSAGING_SENDER_ID=$(echo "$JSON_CONTENT" | jq -r '.messagingSenderId')

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