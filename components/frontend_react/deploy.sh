#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <project-id> <firebase-app-name> <domain-name> <contact-email>"
  exit 1
fi

PROJECT_ID=$1
FIREBASE_APP_NAME=$2
DOMAIN_NAME=$3
CONTACT_EMAIL=$4

# Determine the base directory of the repository
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Navigate to the webapp directory
WEBAPP_DIR="$BASE_DIR/components/frontend_react/webapp"
echo "Changing directory to $WEBAPP_DIR..."
cd "$WEBAPP_DIR" || { echo "Failed to change directory to $WEBAPP_DIR. Please run this script from the components/frontend_react directory."; exit 1; }

# Install jq
echo "Installing jq..."
if ! command -v jq &> /dev/null; then
  OS_TYPE=$(uname)
  if [[ "$OS_TYPE" == "Linux" ]]; then
    sudo apt-get update && sudo apt-get install -y jq
  elif [[ "$OS_TYPE" == "Darwin" ]]; then
    brew install jq
  else
    echo "Please install jq manually for your OS."
    exit 1
  fi
fi

# Install nvm (Node Version Manager)
echo "Installing nvm..."
pushd $HOME
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
popd

# Load nvm
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm

# Install Node.js
echo "Installing Node.js..."
nvm install 22

# Install Firebase CLI
echo "Installing Firebase CLI..."
"$BASE_DIR/utils/install_firebase.sh" v13.1.0

# Install dependencies
echo "Installing dependencies..."
npm install

# Configure Firebase
echo "Configuring Firebase..."
# Update .firebaserc with the provided project ID
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

# Get the Firebase SDK config
echo "Fetching Firebase SDK config..."
firebase apps:sdkconfig WEB "$FIREBASE_APP_NAME" > sdkconfig.json

# Extract values from sdkconfig.json
echo "Extracting values from sdkconfig.json..."
JSON_CONTENT=$(sed -n '/firebase.initializeApp({/,/});/p' sdkconfig.json | sed '1d;$d' | tr -d '\n' | sed 's/^/{/;s/$/}/')
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

# Build the app for production
echo "Building the app..."
npm run build

# Deploy the app with Firebase
echo "Deploying the app to Firebase..."
firebase deploy --only hosting

echo "Installation and deployment complete."