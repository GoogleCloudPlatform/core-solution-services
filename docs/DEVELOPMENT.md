# (DRAFT) Development

<!-- vscode-markdown-toc -->
1. [Project Requirements](#ProjectRequirements)
2. [Code Submission Process](#CodeSubmissionProcess)
3. [Local IDE Development (VS Code)](#LocalIDEDevelopmentVSCode)
4. [Local Development (minikube)](#LocalDevelopmentminikube)
5. [Development with Kubernetes (GKE)](#DevelopmentwithKubernetesGKE)
6. [Advanced Skaffold features (minikube or GKE)](#AdvancedSkaffoldfeaturesminikubeorGKE)
7. [Deploying Common CSS Services (Authentication)](#DeployingCommonCSSServicesAuthentication)
8. [Debugging](#Debugging)
9. [Unit tests - microservices](#Unittests-microservices)

<!-- vscode-markdown-toc-config
	numbering=true
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

This doc explains the development workflow, so you can get started contributing code to Core Solution Services

##  1. <a name='ProjectRequirements'></a>Project Requirements

Install the following based on [the versions for this project](./README.md#Prerequisites)
* `skaffold`
* `kustomize`
* `kubectx`
* `kubens`

##  2. <a name='CodeSubmissionProcess'></a>Code Submission Process

###  2.1. <a name='Forthefirst-timesetup:'></a>For the first-time setup:
* Create a fork of a Git repository (using the button on the right corner of the page)
* Choose your own GitHub profile to create this fork under your name.
* Clone the repo to your local computer.
  ```
  export GITHUB_ID=<your-github-id>
  cd ~/workspace
  git clone https://github.com/$GITHUB_ID/core-solution-services.git
  cd core-solution-services
  ```
* Verify if the local git copy has the right remote endpoint.
  ```
  git remote -v
  # This will display the detailed remote list like below.
  origin  https://github.com/$GITHUB_ID/core-solution-services.git (fetch)
  origin  https://github.com/$GITHUB_ID/core-solution-services.git (push)
  ```
  - If for some reason your local git copy does not have the correct remotes, run the following:
    ```
    git remote add origin https://github.com/$GITHUB_ID/core-solution-services.git
    # Or, to reset the URL if origin remote exists
    git remote set-url origin https://github.com/<your-github-id>/core-solution-services.git
    ```
* Add the upstream repo to the remote list as **upstream**.
  ```
  git remote add upstream https://github.com/GoogleCloudPlatform/core-solution-services.git
  ```
  - In default case, `upstream` will be the repo that you make the fork from.

###  2.2. <a name='Whenmakingcodechanges'></a>When making code changes
* Sync your fork with the latest commits in upstream/master branch. (more info)
  ```
  # In your local fork repo folder.
  git checkout -f main
  git pull upstream main
  ```
* Create a new local branch to start a new task (e.g. working on a feature or a bug fix):
  ```
  # This will create a new branch.
  git checkout -b feature_xyz
  ```
* After making changes, commit the local change to this custom branch and push to your fork repo on GitHub. Alternatively, you can use editors like VSCode to commit the changes easily.
  ```
  git commit -a -m 'Your description'
  git push
  # Or, if it doesn’t push to the origin remote by default.
  git push --set-upstream origin $YOUR_BRANCH_NAME
  ```
  - This will submit the changes to your fork repo on GitHub.
* Go to your GitHub fork repo web page, click the *Compare & Pull Request* in the notification. In the Pull Request form, make sure that:
  - The upstream repo name is correct.
  - The destination branch is set to `main`.
  - The source branch is your custom branch. (e.g. `feature_xyz` in the example above)
  - You may also pick specific reviewers for this pull request.
* Once the pull request is created, it will appear on the Pull Request list of the upstream origin repository, which will automatically run basic tests and checks via the CI/CD.
* If any tests failed, fix the codes in your local branch, re-commit and push the changes to the same custom branch.
  ```
  # after fixing the code…
  git commit -a -m 'another fix'
  git push
  ```
  - This will update the pull request and re-run all necessary tests automatically.
  - If all tests passed, you will need to wait for the reviewers’ approval.
* Once the request has been approved, the reviewer or Repo Admin will merge the pull request back to the upstream `main` branch.

###  2.3. <a name='ForRepoAdminsReviewingaPullRequest'></a>(For Repo Admins) Reviewing a Pull Request
For code reviewers, go to the Pull Requests page of the origin repo on GitHub.
* Go to the specific pull request, review and comment on the request.
branch.
* Alternatively, you can use GitHub CLI `gh` to check out a PR and run the codes locally: https://cli.github.com/manual/gh_pr_checkout
* If all goes well with tests passed, click Merge pull request to merge the changes to `main`.

##  3. <a name='LocalIDEDevelopmentVSCode'></a>Local IDE Development (VS Code)

Here are settings and tips to set up your local IDE for development and testing of the code. These instructions are for VS Code.

As a shortcut, here is a sample `settings.json` for VS Code you will want to start with
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintPath": "pylint",
  "editor.formatOnSave": true,
  "python.formatting.provider": "yapf",
  "python.formatting.yapfArgs": [
    "--style={based_on_style: pep8, indent_width: 2}"
  ],
  "python.linting.pylintEnabled": true,
  "terminal.integrated.env.osx": {
    "PYTHONPATH": "${workspaceFolder}/common/src/"
  },
  "python.analysis.extraPaths": [
    "${workspaceFolder}/common/src/"
  ],
  "python.autoComplete.extraPaths": [
    "${workspaceFolder}/common/src/"
  ]
}
```
You may need to reload VS Code for these to take effect:
* CMD + SHIFT + P
* __Developer: Reload Window__

###  3.1. <a name='Commoncontainersetup'></a>`Common` container setup
The `common` container houses any common libraries, modules, data objects (ORM) etc. that might be needed by other microservices. It can serve as the base container for builds in other microservices as shown in this [Dockerfile](./components/authentication/Dockerfile)

Additional setup is required in a Python development environment so libraries added here are included in your IDE's code completion, etc.

###  3.2. <a name='DevelopingjustCommoncontainerVSCode'></a>Developing just `Common` container (VSCode)
* Set up VENV just for common
```
cd common

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
* Open Command Palette (CMD + SHIFT + P)
* Type `Python: Select Interpreter`
* Choose your new interpreter
  * will look something like `./common/.venv/bin/python3`

You should now be able to load modules and test them locally:
```
cd src
python
```
* In REPL:
```python
from common.models import User
user = User()
```
* Exit the VENV
```
deactivate
```

###  3.3. <a name='Microservicecontainersetup'></a>Microservice container setup
Any microservice containers that use common will follow the same setup, but will also require additional setup for your IDE's code-completion to register the common modules:
* Set up `venv` just for microservice

Make sure you aren't in a VENV
```
deactivate
```
```
cd components/llm_service

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# install requirements from common
pip install -r ../common/requirements.txt

# install microservice requirements
pip install -r requirements.txt
```
* Open Command Palette (CMD + SHIFT + P)
* Type "Python: Select Interpreter"
* Choose your new interpreter
  * will look something like `./components/llm_service/.venv/bin/python3`

If you added the following to your VS Code `settings.json` file like mentioned before, the modules should load when you run from command line, and you should see code completion hints.
```json
{
  "terminal.integrated.env.osx": {
    "PYTHONPATH": "${workspaceFolder}/common/src/"
  },
  "python.analysis.extraPaths": [
    "${workspaceFolder}/common/src/"
  ]
}
```
You should now be able to load modules and test them locally:
```
cd components/llm_service/src

# run web server
python main.py
```
* Exit the VENV
```
deactivate
```

###  3.4. <a name='OtherIDESetup'></a>Other IDE Setup

* If VS Code asks you to install tools like `pylint`, etc. go ahead and do so.

##  4. <a name='LocalDevelopmentminikube'></a>Local Development (`minikube`)

Minikube can be used to provide an easy local Kubernetes environment for fast prototyping and debugging
* Install Minikube:
```
# For MacOS:
brew install minikube

# For Windows:
choco install -y minikube
```
* Simple local run

Make sure the Docker daemon is running locally. To start minikube:
```
# This will reset the kubectl context to the local minikube.
minikube start

# Build and run locally with hot reload:
skaffold dev
```
* `minikube` runs with ENV variables that are captured in `kustomize`, for example [here](./components/llm_service/kustomize/base/properties.env)
```
# if PROJECT_ID variable is used in your containers
export PROJECT_ID=<your-project>

skaffold dev
```

###  4.1. <a name='ADVANCED:RunonminikubewithyourGCPcredentials'></a>ADVANCED: Run on minikube with your GCP credentials
This will mount your GCP credentials to every pod created in minikube. See [this guide](https://minikube.sigs.k8s.io/docs/handbook/addons/gcp-auth/) for more info.

The addon normally uses the [Google Application Default Credentials](https://google.aip.dev/auth/4110) as configured with `gcloud auth application-default login`. If you already have a json credentials file you want to specify, such as to use a service account, set the GOOGLE_APPLICATION_CREDENTIALS environment variable to point to that file.
* User credentials
```
gcloud auth application-default login
minikube addons enable gcp-auth
```
* File based credentials
```
# Download a service accouunt credential file
export GOOGLE_APPLICATION_CREDENTIALS=<creds-path>.json
minikube addons enable gcp-auth
```

##  5. <a name='DevelopmentwithKubernetesGKE'></a>Development with Kubernetes (GKE)

###  5.1. <a name='InitialsetupforGKEdevelopment'></a> Initial setup for GKE development
After cloning the repo, please set up for local development.

* Export GCP project id and the namespace based on your GitHub handle (i.e. user ID)
  ```
  export PROJECT_ID=core-solution-services-dev
  export REGION=us-central1
  export SKAFFOLD_NAMESPACE=$GITHUB_ID
  echo $PROJECT_ID $SKAFFOLD_NAMESPACE
  ```
* Run the following to create skaffold namespace, and use the default cluster name as `default_cluster`:
  ```
  ./setup/setup_local.sh
  ```
* Run the following to set up the Kubernetes Service Account (ksa) in your namespace:
  ```
  export NAMESPACE=$SKAFFOLD_NAMESPACE
  bash ./setup/setup_ksa.sh
  ```

###  5.2. <a name='BuildandrunallmicroservicesinthedefaultGKEclusterwithlivereload'></a>Build and run all microservices in the default GKE cluster with live reload
> **_NOTE:_**  By default, skaffold builds with CloudBuild and runs in kubernetes cluster set in your local `kubeconfig`, using the namespace set above in `SKAFFOLD_NAMESPACE`. If it is set to your GKE cluster, it will deploy to the cluster. If it's set to `minikube`, it will deploy there.
```
# check your current kubeconfig
kubectx

skaffold dev
```
- Please note that any change in the code locally will rerun the build process.

###  5.3. <a name='DeploytoaspecificGKEcluster'></a>Deploy to a specific GKE cluster
> **IMPORTANT**: Please change gcloud project and kubectl context before running skaffold.
```
export PROJECT_ID=core-solution-services-dev

# Switch to a specific project.
gcloud config set project $PROJECT_ID

# Assuming the default cluster name is "default_cluster".
gcloud container clusters get-credentials default_cluster --zone us-central1-a --project $PROJECT_ID
```
Run with skaffold:
```
skaffold run -p custom --default-repo=gcr.io/$PROJECT_ID

# Or run with hot reload and live logs:
skaffold dev -p custom --default-repo=gcr.io/$PROJECT_ID
```

##  6. <a name='AdvancedSkaffoldfeaturesminikubeorGKE'></a>Advanced Skaffold features (minikube or GKE)

###  6.1. <a name='Buildandrunwithspecificmicroservices'></a>Build and run with specific microservice(s)
```
skaffold dev -m <service1>,<service2>
```

###  6.2. <a name='BuildandrunmicroserviceswithacustomSourceRepositorypath'></a>Build and run microservices with a custom Source Repository path
```
skaffold dev --default-repo=gcr.io/$PROJECT_ID
```

###  6.3. <a name='BuildandrunmicroserviceswithadifferentSkaffoldprofile'></a>Build and run microservices with a different Skaffold profile
```
# Using hpa profile
skaffold dev -p hpa
```

###  6.4. <a name='Skaffoldprofiles'></a>Skaffold profiles
By default, the Skaffold YAML contains the following pre-defined profiles ready to use.
- **base** - This is the default profile for local development, which will be activated automatically with the `kubectl` context set to the default cluster of this GCP project.
- **hpa** - This is the profile for building and deploying to the Prod environment, e.g. to a customer's Prod environment. Adds Horizontal Pod Autoscaler (HPA)

###  6.5. <a name='SwitchingfromlocalminikubetoGKEdevelopment'></a>Switching from local (`minikube`) to GKE development
Use the `kubectx` tool to change KubeConfig contexts, which are used by skaffold to target the appropriate cluster.
* Switching to minikube
```
# if minikube is already started
kubectx minikube

# if minikube is not started
# running this will also change the KubeConfig context
minikube start

skaffold dev
```
* Switching to GKE
```
# see available KubeContexts
kubectx

# choose your cluster
kubectx <YOUR_CLUSTER_NAMAE>

skaffold dev
```

##  7. <a name='DeployingCommonCSSServicesAuthentication'></a>Deploying Common CSS Services (Authentication)

If you are deploying common Core Solution Services from another repo into your dev setup, perform the following steps. Target the same cluster and namespace from a separate tab, since you will need to run this `skaffold` command in parallel with the local `skaffold` command.

Clone the repo:
```
git glone https://github.com/$GITHUB_ID/core-solution-services.git
cd core-solution-services
```
Run a skaffold dev command to build / deploy the microservice:
```
GCP_PROJECT=<YOUR_PROJECT>
export FIREBASE_API_KEY=<FIREBASE_API_KEY>

GCP_PROJECT=$GCP_PROJECT skaffold dev -m authentication,redis -p custom --default-repo=gcr.io/$GCP_PROJECT
```

##  8. <a name='Debugging'></a>Debugging

###  8.1. <a name='LocalDebugging-Common'></a>Local Debugging - Common
By default, VS Code will use the Python interpreter you've selected with the Python extensions (CMD + SHIFT + P -> __Select Interpreter__) so clicking __Debug__ and running without a configuration should work, so long as you have shifted the interpreter over and activated the "Common" VENV.

Mileage will vary - you may need to create a "Debug Current File" Debug configuration in VS Code, particularly if you are in a multi-folder Workspace.

###  8.2. <a name='LocalDebugging-Microservice'></a>Local Debugging - Microservice
This should also just work, so long as you have selected the right interpreter, are in the microservice folder, and have entered your VENV.

Mileage will vary - you may need to create a "Debug Current File" Debug configuration in VS Code, particularly if you are in a multi-folder Workspace.

###  8.3. <a name='MinikubeMicroserviceDebuggingwSkaffoldCloudCodeVSCode'></a>Minikube Microservice Debugging w/ Skaffold + Cloud Code (VS Code)
You don't need a VENV for this option.

First, install [Cloud Code](https://marketplace.visualstudio.com/items?itemName=GoogleCloudTools.cloudcode)

```bash
minikube start
# if minikube is started: kubectx minikube
```

* From Command Palette (CMD + SHIFT + P): __Cloud Code: Debug on Kubernetes__
* Select the root `skaffold.yaml`
* Run __All dependencies__ or the module that you want
* Select a profile (Default for minikube)
* Select context (minikube)

If minikube isn't starting, you may need to disable "Enable Minikube Gcp Auth Plugin" in the Cloud Code Settings.

###  8.4. <a name='GKEMicroserviceDebuggingwSkaffoldCloudCodeVSCode'></a>GKE Microservice Debugging w/ Skaffold + Cloud Code (VS Code)
You don't need a VENV for this option.

First, install [Cloud Code](https://marketplace.visualstudio.com/items?itemName=GoogleCloudTools.cloudcode)

* From Command Palette (CMD + SHIFT + P): __Cloud Code: Debug on Kubernetes__
* Select the root `skaffold.yaml`
* Run __All dependencies__ or the module that you want
* Select a profile (dev for GKE)
* Select context - the GKE cluster you're using
* You will need to edit the `launch.json` file and add `/src` to the "sourceFileMap" field

When you're done, make sure to fully disconnect the debugger, so it removes the running services.

##  9. <a name='Unittests-microservices'></a>Unit tests - microservices

Install Firebase CLI:
```
curl -sL https://firebase.tools | bash
```
Install Virtualenv and pip requirements
```
# Start in the root folder
export BASE_DIR=$(pwd)

# Go to a specific microservice folder:
cd components/llm_service
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-test.txt
```
Run unit tests locally:
```
PYTEST_ADDOPTS="--cache-clear --cov . " PYTHONPATH=$BASE_DIR/common/src python -m pytest
```

####  9.1. <a name='Runlinterlocally:'></a>Run linter locally:
```
python -m pylint $(git ls-files '*.py') --rcfile=$BASE_DIR/.pylintrc
```

####  9.2. <a name='Unittestfileformat:'></a>Unit test file format:
All unit test files follow the filename format:

- Python:
  ```
  <original_filename>_test.py