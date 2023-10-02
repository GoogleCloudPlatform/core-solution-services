# Development

Table of Content
<!-- vscode-markdown-toc -->
1. [Project Requirements](#ProjectRequirements)
2. [Code Submission Process](#CodeSubmissionProcess)
3. [Local Environment Setup](#LocalEnvironmentSetup)
4. [Develop and Test on a GKE cluster](#DevelopandTestonaGKEcluster)
5. [Advanced Skaffold commands](#AdvancedSkaffoldcommands)
6. [Debugging](#Debugging)
7. [Testing](#Testing)

<!-- vscode-markdown-toc-config
	numbering=true
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

This doc explains the development workflow, so you can get started contributing code to Core Solution Services

##  1. <a name='ProjectRequirements'></a>Project Requirements

Install the following based on the [README.md#Prerequisites](../README.md#Prerequisites)
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
  export YOUR_GITHUB_ID=<your-github-id>
  cd ~/workspace
  git clone https://github.com/$YOUR_GITHUB_ID/core-solution-services.git
  cd core-solution-services
  ```
* Verify if the local git copy has the right remote endpoint.
  ```
  git remote -v
  # This will display the detailed remote list like below.
  origin  https://github.com/$YOUR_GITHUB_ID/core-solution-services.git (fetch)
  origin  https://github.com/$YOUR_GITHUB_ID/core-solution-services.git (push)
  ```
  - If for some reason your local git copy does not have the correct remotes, run the following:
    ```
    git remote add origin https://github.com/$YOUR_GITHUB_ID/core-solution-services.git
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

###  2.3. <a name='2.3.ForRepoAdminsReviewingaPullRequest'></a> 2.3. (For Repo Admins) Reviewing a Pull Request
For code reviewers, go to the Pull Requests page of the origin repo on GitHub.
* Go to the specific pull request, review and comment on the request.
branch.
* Alternatively, you can use GitHub CLI `gh` to check out a PR and run the codes locally: https://cli.github.com/manual/gh_pr_checkout
* If all goes well with tests passed, click Merge pull request to merge the changes to `main`.

##  3. <a name='LocalEnvironmentSetup'></a>Local Environment Setup

###  3.1. <a name='VSCodeSetup'></a>VS Code Setup

Copy the following and paste to the `settings.json` of your VS Code:
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


> If VS Code asks you to install tools like `pylint`, etc. go ahead and do so.

###  3.2. <a name='SetupVirtualEnvforcomponentsmicroservice_folder'></a>Set up VirtualEnv for `components/<microservice_folder>`

Each component folder (non-common) in `./components` represents a standalone Docker container and has its own Python dependencies defined in `requirements.txt`.

These microservice components also depend on the `./components/common`, hence it requires additional setup for IDE's code-completion to register the common modules.

* Make sure you aren't in a VirtualEnv
  ```
  deactivate
  ```

* Set up VirtualEnv just for this microservice component
  ```
  cd components/<component_name>

  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip

  # install requirements from common
  pip install -r ../common/requirements.txt

  # install microservice requirements
  pip install -r requirements.txt
  ```
* (For VS Code only) Set up Python interpreter:
  * Open Command Palette (CMD + SHIFT + P)
  * Type `Python: Select Interpreter`
  * Choose your new interpreter
    * will look something like `./common/.venv/bin/python3`

* (For VS Code Only) Add the following to the `settings.json` in VS Code. The modules should load when you run from command line, and you should see code completion hints.
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

* You should now be able to load modules and test them locally:
  ```
  cd components/<component_name>/src
  python main.py
  ```

* Once you finish development for this component, run the following to exit the
VirtualEnv:
  ```
  deactivate
  ```

###  3.3. <a name='SetupVirtualEnvforcomponentscommon'></a>Set up VirtualEnv for `components/common`

Follow the steps below to create a new VirtualEnv for `components/common` and install required python packages defined in the `requirements.txt`.

* Create a VirtualEnv for a specific component
```
cd components/<component_name> # e.g. llm_service

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
* (For VSCode only) Set up Python interpreter:
  * Open Command Palette (CMD + SHIFT + P)
  * Type `Python: Select Interpreter`
  * Choose your new interpreter
    * will look something like `./common/.venv/bin/python3`

* You should now be able to load modules and test them locally:
  ```
  # In ./components/<component_name>
  cd src
  python
  ```
  In REPL (Copy and paste the code)
  ```python
  from common.models import User
  user = User()
  ```

* Once you finish development for this component, run the following to exit the VirtualEnv:
  ```
  deactivate
  ```

##  4. <a name='DevelopandTestonaGKEcluster'></a>Develop and Test on a GKE cluster

###  4.1. <a name='Doublecheckthecurrentgcloudconfig'></a>Double check the current `gcloud` config

* Please make sure the `gcloud` command set to the current project.
  ```
  export PROJECT_ID=<your-dev-project-id>
  gcloud config set project $PROJECT_ID
  ```

###  4.2. <a name='SetupWorkloadIdentityUser'></a>Set up Workload Identity User

* Run the following to set up the Kubernetes Service Account (ksa) in your namespace:
  ```
  export PROJECT_ID=<your-dev-project-id>
  export SKAFFOLD_NAMESPACE=$YOUR_GITHUB_ID
  export GSA_NAME="gke-sa"
  export KSA_NAME="gke-sa"
  bash ./tools/bind_ksa.sh
  ```

###  4.3. <a name='BuildanddeployallmicroservicesUsingSolutionsBuilderCLI'></a>Build and deploy all microservices (Using Solutions Builder CLI)

> Solutions Builder CLI runs `skaffold` commands behind the scene. It will print out the actual command before running it.

To build and deploy:
```
export SKAFFOLD_NAMESPACE=$YOUR_GITHUB_ID

# In the solution folder:
sb deploy

# Or, to build and deploy with livereload:
sb deploy --dev
```

Press Enter in the prompt:
```
This will build and deploy all services using the command below:
- gcloud container clusters get-credentials main-cluster --region us-central1 --project your-project-id
- skaffold run -p default-deploy  --default-repo="gcr.io/your-project-id"

This may take a few minutes. Continue? [Y/n]:
```

###  4.4. <a name='OptionalBuildanddeployallmicroservicesUsingskaffolddirectly'></a>[Optional] Build and deploy all microservices (Using skaffold directly)

####  4.4.1. <a name='Switchtothedefaultcluster'></a>Switch to the default cluster

* By default, skaffold builds with CloudBuild and runs in kubernetes cluster set in your local `kubeconfig`, using the namespace set above in `SKAFFOLD_NAMESPACE`. If it is set to your GKE cluster, it will deploy to the cluster.
  ```
  export CLUSTER_NAME=default_cluster
  gcloud container clusters get-credentials $CLUSTER_NAME --zone us-central1-a --project $PROJECT_ID
  ```

* Check your current context to verify which GKE cluster it points to:
  ```
  kubectl config current-context

  # Or you can use kubectx tool:
  kubectx
  ```

####  4.4.2. <a name='DeploytotheGKEcluster'></a>Deploy to the GKE cluster

* Run with skaffold:
  ```
  skaffold run -p gke --default-repo=gcr.io/$PROJECT_ID

  # Or run with hot reload and live logs:
  skaffold dev -p gke --default-repo=gcr.io/$PROJECT_ID
  ```

##  5. <a name='AdvancedSkaffoldcommands'></a>Advanced Skaffold commands

####  5.1. <a name='Buildandrunwithspecificmicroservices'></a>Build and run with specific microservice(s)
```
skaffold dev -m <service1>,<service2>
```

####  5.2. <a name='BuildandrunmicroserviceswithacustomSourceRepositorypath'></a>Build and run microservices with a custom Source Repository path
```
skaffold dev --default-repo=gcr.io/$PROJECT_ID
```

####  5.3. <a name='BuildandrunmicroserviceswithadifferentSkaffoldprofile'></a>Build and run microservices with a different Skaffold profile
```
# Using HPA (Horizontal Pod Autoscaler) profile
skaffold dev -p gke,gke-hpa
```

####  5.4. <a name='Skaffoldprofiles'></a>Skaffold profiles
By default, the Skaffold YAML contains the following pre-defined profiles ready to use.
- **gke** - This is the default profile for local development, which will be activated automatically with the `kubectl` context set to the default cluster of this GCP project.
  - The corresponding kustomize YAML is in the `./components/<component_name>/kustomize/base` folder.
- **gke-hpa** - This is the profile for building and deploying to the Prod environment, e.g. to a customer's Prod environment. Adds Horizontal Pod Autoscaler (HPA)
  - The corresponding kustomize YAML is in the `./components/<component_name>/kustomize/hpa` folder.


##  6. <a name='Debugging'></a>Debugging

###  6.1. <a name='Debugginglocally'></a>Debugging locally

####  6.1.1. <a name='Debuggingcomponentscommon'></a>Debugging `components/common`
By default, VS Code will use the Python interpreter you've selected with the Python extensions (CMD + SHIFT + P -> __Select Interpreter__) so clicking __Debug__ and running without a configuration should work, so long as you have shifted the interpreter over and activated the "Common" VirtualEnv.

Mileage will vary - you may need to create a "Debug Current File" Debug configuration in VS Code, particularly if you are in a multi-folder Workspace.

####  6.1.2. <a name='Debuggingcomponentscomponent_name'></a>Debugging `components/<component_name>`
This should also just work, so long as you have selected the right interpreter, are in the microservice folder, and have entered your VirtualEnv.

Mileage will vary - you may need to create a "Debug Current File" Debug configuration in VS Code, particularly if you are in a multi-folder Workspace.

###  6.2. <a name='DebuggingwithSkaffoldCloudCodeonGKEcluster'></a>5.2. Debugging with Skaffold + Cloud Code (on GKE cluster)
> NOTE: You don't need a VirtualEnv for this option.

First, install [Cloud Code](https://marketplace.visualstudio.com/items?itemName=GoogleCloudTools.cloudcode)

* From Command Palette (CMD + SHIFT + P): __Cloud Code: Debug on Kubernetes__
* Select the root `skaffold.yaml`
* Run __All dependencies__ or the module that you want
* Select a profile (dev for GKE)
* Select context - the GKE cluster you're using
* You will need to edit the `launch.json` file and add `/src` to the "sourceFileMap" field

When you're done, make sure to fully disconnect the debugger, so it removes the running services.

##  7. <a name='Testing'></a>Testing

###  7.1. <a name='Unittesting'></a>Unit testing

* Install Firebase CLI:
  ```
  curl -sL https://firebase.tools | bash
  ```
* Install Virtualenv and pip requirements
  ```
  # Start in the root folder
  export BASE_DIR=$(pwd)

  # Go to a specific microservice folder:
  cd components/<component_name>
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  pip install -r requirements-test.txt

  # If this component depends on the common folder:
  pip install -r ../common/requirements.txt
  ```
* Run unit tests locally:
  ```
  PYTEST_ADDOPTS="--cache-clear --cov . " PYTHONPATH=$BASE_DIR/components/<component_name>/src python -m pytest
  ```

###  7.2. <a name='Testfilenameconventionandformat'></a>Test filename convention and format

All unit test files follow the filename format:

- Python:
  ```
  <original_filename>_test.py
  ```

- Typescript/Javascript:
  ```
  <original_filename>.spec.ts
  <original_filename>.spec.js
  ```

###  7.3. <a name='Codestyleandlinter'></a>Code style and linter

Run linter locally:
```
python -m pylint $(git ls-files '*.py') --rcfile=$BASE_DIR/.pylintrc
```
