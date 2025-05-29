#!/bin/bash
set -e

# PROJECT_ID is passed from the main script

# Make sure PROJECT_ID is available
if [ -z "$PROJECT_ID" ]; then
  if [ -f "sdkconfig.json" ]; then
    PROJECT_ID=$(cat sdkconfig.json | jq -r '.projectId')
  fi
  
  if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID not set and could not be found in sdkconfig.json"
    exit 1
  fi
fi

# Build the app for production
echo "Building the app..."
if ! npm run build; then
  echo "Error: Build failed"
  exit 1
fi

# Deploy the app with Firebase
echo "Deploying the app to Firebase..."
if ! firebase deploy --only hosting --project $PROJECT_ID; then
  echo "Error: Firebase deployment failed"
  exit 1
fi

echo "Deployment completed successfully."
