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

# Install jq
echo "Installing jq..."
if ! command -v jq &> /dev/null; then
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update && sudo apt-get install -y jq
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew install jq
  else
    echo "Please install jq manually for your OS."
    exit 1
  fi
fi

# Install nvm (Node Version Manager)
echo "Installing nvm..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash

# Load nvm
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm

# Install Node.js
echo "Installing Node.js..."
nvm install 22

# Install Firebase CLI
echo "Installing Firebase CLI..."
./utils/install_firebase.sh v13.1.0

# Navigate to the webapp directory
cd components/frontend_react/webapp || exit

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
PROJECT_ID=$(jq -r '.projectId' sdkconfig.json)
APP_ID=$(jq -r '.appId' sdkconfig.json)
STORAGE_BUCKET=$(jq -r '.storageBucket' sdkconfig.json)
API_KEY=$(jq -r '.apiKey' sdkconfig.json)
AUTH_DOMAIN=$(jq -r '.authDomain' sdkconfig.json)
MESSAGING_SENDER_ID=$(jq -r '.messagingSenderId' sdkconfig.json)

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