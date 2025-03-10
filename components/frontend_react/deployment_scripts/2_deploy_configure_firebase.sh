#!/bin/bash
set -e

PROJECT_ID=$1
FIREBASE_APP_NAME=$2

# Check if Firebase app already exists
existing_app=$(firebase apps:list | grep "$FIREBASE_APP_NAME" | awk '{print $1}')

if [ -z "$existing_app" ]; then
  # Configure Firebase
  echo "Updating .firebaserc with project ID..."
  cat <<EOL > .firebaserc
  {
    "projects": {
      "default": "$PROJECT_ID"
    }
  }
  EOL

  # Create your app in Firebase
  echo "Creating Firebase app..."
  firebase apps:create web "$FIREBASE_APP_NAME"

  # Retry fetching SDK config with exponential backoff
  retries=5
  delay=5
  for i in $(seq 1 $retries); do
    echo "Attempting to fetch Firebase SDK config (attempt $i)..."
    firebase apps:sdkconfig WEB "$FIREBASE_APP_NAME" > sdkconfig.json
    if [ -f sdkconfig.json ]; then
      echo "Firebase SDK config fetched successfully."
      break
    else
      if [ $i -eq $retries ]; then
        echo "ERROR: Failed to fetch Firebase SDK config after $retries attempts."
        exit 1
      fi
      echo "Failed to fetch SDK config. Retrying in $delay seconds..."
      sleep $delay
      delay=$((delay * 2)) # Exponential backoff
    fi
  done
else
  echo "Firebase app '$FIREBASE_APP_NAME' already exists. Skipping creation."
  # If the app exists, we should still try to get the sdkconfig
  # Retry fetching SDK config with exponential backoff
  retries=5
  delay=5
  for i in $(seq 1 $retries); do
    echo "Attempting to fetch Firebase SDK config (attempt $i)..."
    firebase apps:sdkconfig WEB "$FIREBASE_APP_NAME" > sdkconfig.json
    if [ -f sdkconfig.json ]; then
      echo "Firebase SDK config fetched successfully."
      break
    else
      if [ $i -eq $retries ]; then
        echo "ERROR: Failed to fetch Firebase SDK config after $retries attempts."
        exit 1
      fi
      echo "Failed to fetch SDK config. Retrying in $delay seconds..."
      sleep $delay
      delay=$((delay * 2)) # Exponential backoff
    fi
  done
fi

