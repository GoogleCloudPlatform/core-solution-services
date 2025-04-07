## Prerequisites

| Tool                | Required Version | Installation                                                                                                                                                                                        |
|---------------------|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `python`            | `>= 3.9`         | [Mac](https://www.python.org/ftp/python/3.9.18/python-3.9.18-macos11.pkg) • [Windows](https://www.python.org/downloads/release/python-3918/) • [Linux](https://docs.python.org/3.9/using/unix.html) |
| `gcloud` CLI        | `Latest`         | https://cloud.google.com/sdk/docs/install                                                                                                                                                           |
| `terraform`         | `>= v1.3.7`      | https://developer.hashicorp.com/terraform/downloads                                                                                                                                                 |
| `solutions-builder` | `== v1.18.1`    | https://pypi.org/project/solutions-builder/                                                                                                                                                         |
| `skaffold`          | `>= v2.4.0`      | https://skaffold.dev/docs/install/                                                                                                                                                                  |
| `kustomize`         | `>= v5.0.0`      | https://kubectl.docs.kubernetes.io/installation/kustomize/                                                                                                                                          |

### Installing on Windows

We recommend you use [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) with [Ubuntu](https://canonical-ubuntu-wsl.readthedocs-hosted.com/en/latest/guides/install-ubuntu-wsl2/) for the initial steps, up to the point where you have a jump host.  After that you should complete the install from the jump host.

### Troubleshooting Awareness

Please be aware of our [troubleshooting resources](https://github.com/GoogleCloudPlatform/core-solution-services/tree/main#troubleshooting) as they detail solutions to common issues found during the deployment process.

## Setup

### Set up the GCP Project

We recommend starting from a brand new GCP project. Create a new GCP project at https://console.cloud.google.com/projectcreate

### Install gcloud
[Install](https://cloud.google.com/sdk/docs/install) the gcloud command line tool, if it is not already present in your dev environment.


### Enable Cloud Identity Platform

Follow the steps below to enable Cloud Identity Platform and add Email/Password provider: (For Authentication)
- [components/authentication/README.md#enable-identity-platform](./components/authentication/README.md#enable-identity-platform)

### Check Org policies (Optional)

Make sure that policies are not enforced (`enforce: false` or `NOT_FOUND`). You must be an organization policy administrator to set a constraint.
- https://console.cloud.google.com/iam-admin/orgpolicies/compute-requireShieldedVm?project=$PROJECT_ID
- https://console.cloud.google.com/iam-admin/orgpolicies/requireOsLogin?project=$PROJECT_ID
```
export ORGANIZATION_ID="$(gcloud projects get-ancestors $PROJECT_ID | grep organization | cut -f1 -d' ')"
gcloud resource-manager org-policies delete constraints/compute.requireShieldedVm --organization=$ORGANIZATION_ID
gcloud resource-manager org-policies delete constraints/compute.requireOsLogin --organization=$ORGANIZATION_ID
gcloud resource-manager org-policies delete constraints/compute.vmExternalIpAccess --organization=$ORGANIZATION_ID
gcloud resource-manager org-policies delete constraints/iam.allowedPolicyMemberDomains --organization=$ORGANIZATION_ID
```

### Clone repo

You should start with a clean copy of the repository. Clone this repo to your local machine to start. Optionally, you can use [Cloud Shell](https://cloud.google.com/shell). Run the rest of the commands inside the repo folder.

```
git clone https://github.com/GoogleCloudPlatform/core-solution-services
cd core-solution-services
```

Checkout the release tag for the desired release.

```
git checkout v0.4.0
```

### Verify your Python version and create a virtual env
Make sure you have Python version 3.9 or greater.
```
python3 --version
```
Create a virtual environment and activate it.
```
python3 -m venv .venv
source .venv/bin/activate
```

### Install Solutions Builder package
Make sure to not install the default sb 2.x.x version, as its not backwards compatible.
```
pip install -U "solutions-builder==1.18.1"

# Verify Solution Builder CLI tool with version == v1.18.1
sb version
```

### Set up `gcloud` CLI
```
export PROJECT_ID=<your-project-id>
gcloud config set project ${PROJECT_ID}
gcloud auth login
gcloud auth application-default login
gcloud auth configure-docker us-docker.pkg.dev
```

### Update Project ID
Run this command to update the project id in config files of your local repo.
```
sb set project-id ${PROJECT_ID}
```

### Set up a Jump Host

> If you choose to run this setup in your local machine, you can skip this section. However, we recommend using a jump host to ensure a consistent install environment.

> During the install process we create an environment variable profile in /etc/profile.d/genie_env.sh. This file captures the environment variables used for configuration of the microservices, and since it is sourced any time a user logs in, ensures all variables will be set correctly during a deploy.  If you are not using a jump host we still recommend that you create this file.

Run the following to create a Compute Engine VM as the jump host.
```
sb infra apply 0-jumphost
```
- Please note it may take 5-10 minutes to install dependencies in the VM.

Log into the jump host:
```
export JUMP_HOST_ZONE=$(gcloud compute instances list --filter="name=(jump-host)" --format="value(zone)")
echo Jump host zone is ${JUMP_HOST_ZONE}
gcloud compute ssh jump-host --zone=${JUMP_HOST_ZONE} --tunnel-through-iap --project=${PROJECT_ID}
```

Check the status of the jump host setup:
```
ls -la /tmp/jumphost_ready
```
- If the file `jumphost_ready` exists, it means the jumphost is ready to deploy the rest of the resources.  If not, please wait for a few minutes.

Authenticate to GCP in the jumphost:
```
gcloud auth login
gcloud auth application-default login
gcloud auth configure-docker us-docker.pkg.dev
```

#### Configure repository in Jumphost
Check out the code:
```
git clone https://github.com/GoogleCloudPlatform/core-solution-services
```

Checkout the release tag for the desired release.

```
cd core-solution-services
git checkout v0.4.0
```

Configure the repository:
```
# Set PROJECT_ID
export PROJECT_ID=$(gcloud config get project)
echo PROJECT_ID=${PROJECT_ID}

# Update project_id values in the source repo
sb set project-id ${PROJECT_ID}
```

Run the rest of the deployment steps from within this jumphost.


### Create the Cloud infra

* Perform this additional repo config step, to update domain name (for HTTPS load balancer and ingress):
```
export DOMAIN_NAME=<your-domain-name> # e.g. css.example.com
export API_BASE_URL=https://${DOMAIN_NAME}
sb vars set domain_name ${DOMAIN_NAME}
```

* On the jump host, run this command to ensure that these env vars are always set upon login:
```
sudo bash -c "cat << EOF >> /etc/profile.d/genie_env.sh
export DOMAIN_NAME=$DOMAIN_NAME
export API_BASE_URL=https://${DOMAIN_NAME}
export SKAFFOLD_DEFAULT_REPO=us-docker.pkg.dev/${PROJECT_ID}/default
EOF"
```

* Apply bootstrap terraform:
```
sb infra apply 1-bootstrap
```

* Apply foundations terraform.  Note in the following step there is a known issue with firebase setup: `Error 409: Database already exists.`  If this error occurs, consult the Troubleshooting section to apply the fix, then re-run the 2-foundation step.

```
sb infra apply 2-foundation
```

* Proceed with the GKE and ingress install:

```
sb infra apply 3-gke
sb infra apply 3-gke-ingress
```

* On the jump host, run this to update the env vars profile:
```
export REGION=$(gcloud container clusters list --filter=main-cluster --format="value(location)")
sudo bash -c "echo 'export REGION=$REGION' >> /etc/profile.d/genie_env.sh"
```

* (Optional) Add an A record to your DNS:
![Alt text](.github/assets/dns_a_record.png)

  - Set the IP address in the A record to the external IP address in the ingress.

* Apply infra/terraform for LLM service:
  - This will create a `$PROJECT_ID-llm-docs` bucket and upload the sample doc `llm-sample-doc.pdf` to it.
  - It will add required Firestore indexes.

```
sb infra apply 4-llm
```


### Before Deploy

1. Set up `kubectl` to connect to the provisioned GKE cluster
```
export REGION=$(gcloud container clusters list --filter=main-cluster --format="value(location)")
gcloud container clusters get-credentials main-cluster --region ${REGION} --project ${PROJECT_ID}
kubectl get nodes
```

2. Follow README files for the microservices below to complete set up:
- LLM Service: [components/llm_service/README.md](./components/llm_service/README.md#setup) (Only Setup section)
  - We recommend deploying AlloyDB and PG Vector as a vector store.  See the section on AlloyDB in the LLM Service [README](components/llm_service/README.md)
- Tools Service:  If you are using the Tool Service (for GenAI agents that use Tools) follow the instructions in the [README](components/tools_service/README.md)

3. Build webscraper container
Perform a one-time build of the webscraper utility container.  Run this command at the top level repo directory.
```
skaffold build -m webscraper
```

## Deploy Backend Microservices


> Note that when you deploy the ingress below you may need to wait some time (in some cases, hours) before the https cert is active.

You must set these environment variables prior to deployment.  The jump host includes a script to automatically set these variables on login: `/etc/profile.d/genie_env.sh`.
```
export PROJECT_ID=$(gcloud config get project)
export NAMESPACE=default
export PG_HOST=<the IP of your deployed Alloydb instance>
export DOMAIN_NAME=<your domain>
export API_BASE_URL=https://${DOMAIN_NAME}
export APP_BASE_PATH="/streamlit"
export SKAFFOLD_DEFAULT_REPO=us-docker.pkg.dev/${PROJECT_ID}/default
```

### Option 1: Deploy GENIE microservices to the GKE cluster

If you are installing GENIE you can deploy a subset of the microservices used by a default install of GENIE.

```
skaffold config set default-repo "${SKAFFOLD_DEFAULT_REPO}"
skaffold run -p default-deploy -m authentication,redis,llm_service,jobs_service,frontend_streamlit -n $NAMESPACE
```
- This will run `skaffold` commands to deploy those microservices to the GKE cluster.

Check the status of the pods:

```
kubectl get pods
```

#### Deploy ingress to GKE cluster:

> Note again that the ingress may take some time to be available.  You can check the ingress status in the GCP console by [navigating to the cluster](https://console.cloud.google.com/kubernetes/discovery) and selecting "Gateways, Service and Ingress"

```bash
cd ingress
skaffold run -p genie-deploy -n $NAMESPACE --default-repo="${SKAFFOLD_DEFAULT_REPO}"
```


### Option 2: Deploy all microservices to GKE cluster
If you wish to deploy all microservices in Core Solution Services use the following command:

```bash
NAMESPACE=default
skaffold run -p default-deploy -n $NAMESPACE
```
- This will run `skaffold` commands to deploy all microservices to the GKE cluster.

Check the status of the pods:

```
kubectl get pods
```

#### Deploy ingress to GKE cluster:

> See above comments on time needed for ingress deploy

```bash
cd ingress
skaffold run -p default-deploy -n $NAMESPACE --default-repo="${SKAFFOLD_DEFAULT_REPO}"
```

### After deployment

- Follow the "add users" section in the [authentication service README](./components/authentication/README.md) to add a user, so you can login to the UX.

### Verify deployment

#### Validating the Redis deployment

Redis is an optional component which is used for caching authentication tokens. It
enhances Genie performance in multi user and concurrent user environments. If this is a 
single user or development installation, redis installation is not required and this step
can be safely ignored.
 
If redis pods are not running and an error similar to `Error: uninstall: Release not loaded: redis: release: not found`
and Redis is required, please reference the [redis troubleshooting section](#redis-installation-workaround) for a redis installation workaround.

#### Validating API Endpoints

Once deployed, check out the API docs with the following links:

- Backend API documentations:
  - https://$YOUR_DNS_DOMAIN/authentication/api/v1/docs
  - https://$YOUR_DNS_DOMAIN/user-management/api/v1/docs
  - https://$YOUR_DNS_DOMAIN/jobs-service/api/v1/docs
  - https://$YOUR_DNS_DOMAIN/llm-service/api/v1/docs

Alternatively, you can test with the IP address to verify API endpoints
```
BASE_IP_ADDRESS=$(gcloud compute addresses list --global --format="value(address)")
```
- Open up `http://$BASE_IP_ADDRESS/authentication/api/v1/docs` in a web browser.


## Frontend applications

### React app
> [React](https://react.dev/) is a popular frontend development framework.

The codebase includes a React app that supports Chat and Query (RAG) for end users, along with Google Identity login.  See the [components/frontend_react/README.md](components/frontend_react/README.md) for instructions on building and deploying the React app.

### Streamlit UX

> [Streamlit](https://streamlit.io) is an open-source Python library that makes it easy to create custom web apps. It's a popular choice for data scientists and machine learning engineers who want to quickly create interactive dashboards and visualizations

As of the 0.3.0 release the React app is the preferred UX for GENIE and we recommend you deploy and use that app.

When running `skaffold run` like above, it automatically deploys the Streamlit-based frontend app altogether with all services deployment.  The streamlit UX is for development purposes only.  

- Once deployed, you can verify the Streamlit frontend app at `https://$YOUR_DNS_DOMAIN/streamlit` in a web browser.

### (Optional) Deploy or run frontend apps manually

See [components/frontend_streamlit/README.md](components/frontend_streamlit/README.md) for options to run or deploy the Streamlit app.

## Node-pool configuration (Optional)

This section contains instructions on how to create a node pool specifc to the LLM Service.  You may need to do this if you are experiencing crashes due to the LLM Service container running out of memory (this can happen when using the DB Agent for example), or if you want to increase performance on query engine builds.

For a production deployment, we recommend configuring a separate node pool for the LLM Service.

### List current node-pools
```shell
gcloud container node-pools list --cluster=main-cluster --region ${REGION} --project ${PROJECT_ID}
```

### Update kustomize config
Append this entry to the end of `components/llm_service/kustomize/base/deployment.yaml`:
```
      nodeSelector:
        cloud.google.com/gke-nodepool: llm-pool
```
Take care with the indentation - the nodeSelector directive should be under the `template:` `spec:` and at the same level as `containers:` and `serviceAccountName:`.

### Create node-pool for LLM Service (if missing or upgrading)
Ref: https://cloud.google.com/kubernetes-engine/docs/how-to/node-pools
```shell
gcloud container node-pools create llm-pool \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --node-locations=${REGION}-a \
  --cluster=main-cluster \
  --service-account gke-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --machine-type=n1-standard-8 \
  --disk-type pd-balanced \
  --disk-size 1000 \
  --num-nodes=1
```
### Update LLM node pool
```shell
gcloud container node-pools update llm-pool \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --cluster=main-cluster \
  --machine-type n1-standard-8 \
  --disk-type pd-balanced \
  --disk-size 1000
```
### Resize LLM node pool
```shell
gcloud container clusters resize main-cluster \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --node-pool llm-pool \
  --num-nodes 2
```

## Troubleshooting

Please refer to [TROUBLESHOOTING.md](https://github.com/GoogleCloudPlatform/solutions-builder/blob/main/docs/TROUBLESHOOTING.md) for any Terraform errors

### Firestore database already exists
```shell
│ Error: Error creating Database: googleapi: Error 409: Database already exists. Please use another database_id
│
│   with google_firestore_database.database,
│   on firestore_setup.tf line 42, in resource "google_firestore_database" "database":
│   42: resource "google_firestore_database" "database" {
```
Fix
```shell
cd terraform/stages/2-foundation/
terraform import google_firestore_database.database "(default)"
cd -
```

### Redis Installation Workaround

In certain OS and Skaffold version combinations there is a known issue which prevents Skaffold from fetching the redis helm
chart from the newer OCI endpoints. The workaround is to download the redis binary directly and point helm to the local chart
by modifying the relevant skaffold reference.

```bash
cd components/redis
helm pull oci://registry-1.docker.io/bitnamicharts/redis
tar -xzvf redis-20.5.0.tgz (or your related version)
vi skaffold.yaml
```
Update skaffold.yaml so it points to the local redis path:
```
      releases:
      - name: redis
        chartPath: redis
```
Cd back to the core-solution-services directory and deploy the redis microservice: 
```bash
cd ../..
skaffold run -p default-deploy -m redis -n $NAMESPACE
```
Validate your redis deployment
```bash
kubectl get pods
```
You should see a redis-master-0 and replica pods running.

### Apple M1 laptop related errors
- I use an Apple M1 Mac and got errors like below when I ran `terraform init`:
  ```
  │ Error: Incompatible provider version
  │
  │ Provider registry.terraform.io/hashicorp/template v2.2.0 does not have a package available for your current platform,
  │ darwin_arm64.
  │
  │ Provider releases are separate from Terraform CLI releases, so not all providers are available for all platforms. Other
  │ versions of this provider may have different platforms supported.
  ```
  - A: Run the following to add support of M1 chip ([reference](https://kreuzwerker.de/en/post/use-m1-terraform-provider-helper-to-compile-terraform-providers-for-mac-m1))
    ```
     brew install kreuzwerker/taps/m1-terraform-provider-helper
     m1-terraform-provider-helper activate
     m1-terraform-provider-helper install hashicorp/template -v v2.2.0
    ```

### Running user-tool gives an error
```shell
user@jump-host:/home/user/core-solution-services$ PYTHONPATH=components/common/src/ python components/authentication/scripts/user_tool.py create_user --base-url=$BASE_URL
API base URL: http://x.x.x.x
User email (user@example.com):
/home/user/.local/lib/python3.9/site-packages/google/cloud/firestore_v1/base_collection.py:290: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
Fix
```shell
pip install -r components/common/requirements.txt
pip install -r components/authentication/requirements.txt
```

### Docker not working for current user
```shell
docker: Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Post "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/containers/create": dial unix /var/run/docker.sock: connect: permission denied.
```
Fix
```shell
sudo usermod -aG docker ${USER}
```
Log out and log back in again to re-evaluate group memberships


### sb deploy --dev fails for Mac OS
```shell
sh: envsubst: command not found
build [llm-service] failed: exit status 127
```
Fix
```shell
brew install gettext
brew link --force gettext 
```

### 502 Bad Gateway Error when using LLM Service
If you have an existing Genie installation where the response takes a while and returns an 502 error, it could be because the backend LLM service is using the default timeout of 30 sec. The solution is to redeploy the LLM service manually because `skaffold run` does not automatically apply the backendconfig changes.

Fix
```shell
cd components/llm_service/kustomize/base
kubectl delete service llm-service
kubectl apply -f backend_config.yaml
kubectl apply -f service.yaml
cd -
```
