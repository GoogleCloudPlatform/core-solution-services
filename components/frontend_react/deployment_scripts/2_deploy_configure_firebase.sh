#!/bin/bash
set -e

PROJECT_ID="$1"
FIREBASE_APP_NAME="$2"

is_valid_json() {
  if jq empty sdkconfig.json > /dev/null 2>&1; then
    echo "The sdkconfig is valid json."
    return 0 # Indicates success
  else
    echo "The sdkconfig is NOT valid json."
    return 1 # Indicates failure
  fi
}

fetch_sdk_config() {
  retries=5
  delay=5
  for i in $(seq 1 $retries); do
    echo "Attempting to fetch Firebase SDK config (attempt $i)..."
    firebase apps:sdkconfig WEB "$app_id" --project "$PROJECT_ID" | awk '
      BEGIN {print "{"}
      /^\s*"projectId":/ || /^\s*"appId":/ || /^\s*"storageBucket":/ || /^\s*"apiKey":/ || /^\s*"authDomain":/ || /^\s*"messagingSenderId":/ {
        line = $0;
        # Remove trailing comma if present
        gsub(/,\s*$/, "", line);
        # Store the line
        lines[count++] = line;
      }
      END {
        # Print all lines with appropriate commas
        for (i = 0; i < count; i++) {
          print lines[i] (i < count-1 ? "," : "");
        }
        print "}";
      }' > sdkconfig.json
    if [ -s sdkconfig.json ] && is_valid_json; then
      if [ $? -eq 0 ]; then
        echo "Firebase SDK config fetched successfully."
        return 0
      else
        echo "Firebase SDK config fetched, but json is invalid"
        rm sdkconfig.json
        if [ $i -eq $retries ]; then
          echo "ERROR: Failed to fetch and validate Firebase SDK config after $retries attempts."
          return 1
        fi
        echo "Failed to fetch valid SDK config. Retrying in $delay seconds..."
        sleep $delay
        delay=$((delay * 2))
      fi
    else
      if [ $i -eq $retries ]; then
        echo "ERROR: Failed to fetch Firebase SDK config after $retries attempts."
        return 1
      fi
      echo "Failed to fetch SDK config. Retrying in $delay seconds..."
      sleep $delay
      delay=$((delay * 2))
    fi
  done
}

# Check if Firebase is already enabled for this project
echo "Checking if Firebase is already enabled for project $PROJECT_ID..."
if firebase projects:list | grep -q "$PROJECT_ID"; then
  echo "Firebase is already enabled for project $PROJECT_ID"
else
  echo "Adding Firebase to GCP project..."
  firebase projects:addfirebase "$PROJECT_ID"
  
  echo "Waiting for Firebase provisioning..."
  sleep 10
fi

# Check if Firebase app matching the app name already exists
existing_app=$(firebase apps:list --project=$PROJECT_ID | grep "$FIREBASE_APP_NAME" | awk '{print $4}' | tr -d '│ ')

if [ -z "$existing_app" ]; then
  echo "Updating .firebaserc with project ID..."
  cat <<EOL > .firebaserc
  {
    "projects": {
      "default": "$PROJECT_ID"
    }
  }
EOL

  echo "Creating Firebase app..."
  app_create_output=$(firebase apps:create web "$FIREBASE_APP_NAME" --project=$PROJECT_ID)

  app_id=$(echo "$app_create_output" | grep "App ID:" | awk '{print $4}')

  if [ -z "$app_id" ]; then
      echo "Error: Failed to extract app ID."
      exit 1
  fi

  echo "App ID: $app_id"

  fetch_sdk_config
  if [ $? -ne 0 ]; then
    exit 1
  fi

else
  echo "Firebase app '$FIREBASE_APP_NAME' already exists. Skipping creation."
  app_id=$(firebase apps:list | grep "$FIREBASE_APP_NAME" | awk '{print $4}' | tr -d '│ ')

  if [ -z "$app_id" ]; then
    echo "Error: failed to retrieve app id from firebase apps:list"
    exit 1
  fi

  echo "App ID: $app_id"

  # Fetch SDK config
  fetch_sdk_config
  if [ $? -ne 0 ]; then
    exit 1
  fi
fi

echo "Script completed successfully."