#!/bin/bash
# Add error handling with set -e to exit on errors
set -e

# BASE_DIR, WEBAPP_DIR, and DEPLOYMENT_SCRIPT_DIR are
# defined and exported in the main script

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

# Check if npm is installed, and install it if not
echo "Checking for npm..."
if ! command -v npm &> /dev/null; then
  echo "npm not found. Installing npm..."
  OS_TYPE=$(uname)
  if [[ "$OS_TYPE" == "Linux" ]]; then
    sudo apt-get update && sudo apt-get install -y nodejs npm
  elif [[ "$OS_TYPE" == "Darwin" ]]; then
    brew install node # This includes npm
  else
    echo "Please install npm manually for your OS."
    exit 1
  fi
fi

# Install project dependencies if package.json exists
if [ -f "package.json" ]; then
  echo "Installing npm dependencies..."
  npm install
fi

echo "Installing nvm..."
# Use BASE_DIR that's already defined in main script
export BASE_DIR=${BASE_DIR:-$(pwd)}

pushd $HOME
# Add error handling for nvm installation
if ! curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash; then
  echo "Failed to install nvm. Exiting."
  popd
  exit 1
fi
popd

export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
# Check if nvm.sh exists before sourcing
if [ -s "$NVM_DIR/nvm.sh" ]; then
  \. "$NVM_DIR/nvm.sh" # This loads nvm
else
  echo "Error: nvm installation failed. $NVM_DIR/nvm.sh not found."
  exit 1
fi

echo "Installing Node.js..."
if ! nvm install 22; then
  echo "Failed to install Node.js version 22. Exiting."
  exit 1
fi

echo "Installing Firebase CLI..."
if ! "$BASE_DIR/utils/install_firebase.sh" v13.1.0; then
  echo "Failed to install Firebase CLI. Exiting."
  exit 1
fi

echo "Dependencies installation completed successfully."