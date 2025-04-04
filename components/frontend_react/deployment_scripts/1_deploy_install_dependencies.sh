#!/bin/bash

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

echo "Installing nvm..."
pushd $HOME
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
popd

export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm

echo "Installing Node.js..."
nvm install 22

echo "Installing Firebase CLI..."
"$BASE_DIR/utils/install_firebase.sh" v13.1.0