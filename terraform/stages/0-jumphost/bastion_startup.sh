#!/bin/bash
# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Startup script for the bastion host
# Installs terraform, gcloud and other dependencies

cd /tmp

# Update system packages
sudo apt-get update -y && sudo apt-get autoremove -y
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -yq
sudo apt-get install apt-transport-https python3.9 python3-pip python3-testresources pipenv redis-tools unzip -y
sudo apt-get install python3.9-venv net-tools -y

# Install docker
sudo addgroup --system docker
sudo snap install docker && sudo snap start docker

# Install node and java (for running firebase emulator)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install nodejs openjdk-17-jre -y

# Install Kustomize
export KUSTOMIZE_VERSION=5.1.0
wget https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv"$KUSTOMIZE_VERSION"/kustomize_v"$KUSTOMIZE_VERSION"_linux_amd64.tar.gz
tar -xzf ./kustomize_v"$KUSTOMIZE_VERSION"_linux_amd64.tar.gz
sudo cp kustomize /usr/local/bin/

# Install Skaffold
export SKAFFOLD_VERSION=2.6.0
export SKAFFOLD_PLATFORM=linux
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/v"$SKAFFOLD_VERSION"/skaffold-"$SKAFFOLD_PLATFORM"-amd64
sudo install skaffold /usr/local/bin/

# Re-install gcloud
sudo snap remove google-cloud-cli
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
  sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
sudo apt-get update -y && sudo apt-get install google-cloud-cli google-cloud-sdk-gke-gcloud-auth-plugin -y
gcloud components list

# Install terraform, helm, kubectl and other tools
sudo snap install terraform --classic
sudo snap install helm --classic
sudo snap install kubectl --classic

python3 -m pip install --upgrade pip
python3 -m pip install --upgrade pyopenssl
python3 -m pip install google-cloud-firestore google-cloud-bigquery firebase-admin
python3 -m pip install solutions-builder==1.18.1 --ignore-installed PyYAML

# Install dependencies for running user-tool
python3 -m pip install fireo==2.1.0 regex fastapi google-cloud-secret-manager

# add aliases profile script
cat << EOF | sudo tee /etc/profile.d/00-aliases.sh
alias k='kubectl '
alias kd='kubectl delete pod '
alias kl='kubectl logs '
alias klt='kubectl logs -f '
alias kp='kubectl get pods'
alias gs='git status'
alias gb='git branch'
alias gr='git remote -r'
alias gd='git diff'
alias hg='history | grep '
alias dockerauth='gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://us-docker.pkg.dev'
EOF

# add environment vars profile script
cat << EOF | sudo tee /etc/profile.d/genie_env.sh
export AUTH_AUTO_CREATE_USERS=true
export AUTH_EMAIL_DOMAINS_WHITELIST=google.com
export CORS_ALLOW_ORIGINS="*"
export PROJECT_ID=$(gcloud config get project)
export NAMESPACE=default
export DOMAIN_NAME="your-domain-name"     # sb-var:domain_name
export REGION="us-central1"               # sb-var:gcp_region
EOF

# Mark installation as complete
touch jumphost_ready
