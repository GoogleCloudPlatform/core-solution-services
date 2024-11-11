# Overview of basic install

The goal of a basic GENIE install is to use the latest GENIE code to deploy an instance of the GENIE software stack into a GCP project that you own.
At the end of this install, you will be able to access the GENIE React front end running in your GCP project that uses GENIE microservices also deployed in your GCP project to run a RAG demo.

There are many possible variations for how to deploy and develop with GENIE. However, the following are proscriptive steps that deploys GENIE using the simplest approach applicable to as many starting environments as possible, with a basic configuration. Once this installation is complete, you can dive deeper into add READMEs for how to deploy and work with additional features.

There are four logical steps to deploy GENIE:

1. _Set up_. Create a new GCP Project, set up Cloud Shell, get the GENIE code.
2. _Create the jump host_. We use Cloud Shell to deploy a jump host (virtual machine running in your GCP project) that will be used to do the actual GENIE deployment. We deploy from a jump host to ensure that all deployments start from the same virtual machine configuration.
3. _Deploy GENIE backend_. From the jump host, deploy the GENIE infrastructure (GKE, databases, etc) and microservices.
4. _Deploy GENIE front end_. From the jump host, deploy the GENIE front end application.

# 1. Set up

## Create a new GCP Project

In your GCP Organization, create a new GCP Project and note the `Project ID`.
You may need `Organization Policy Administrator` permissions for the project, since, depending on your Organization, some default policies may need to be changed.

## Open Cloud Shell

In a web browser, go to the [cloud console](https://console.cloud.google.com/) and select the project you just created.

At the top right, click the square icon with the prompt `>_` to Activate Cloud Shell. The Cloud Shell terminal opens at the bottom of the page and, along with some other text, you should see the following at the top.

```
Your Cloud Platform project in this session is set to `<your-project-id>`.
```

This confirms your Cloud Shell terminal is configured to connect to the project you just created.

## Authorize for using gcloud CLI

```
gcloud config configurations list
```

When you run this, you will be asked to Authorize Cloud Shell to use your credentials for the `gcloud` CLI commands. Click Authorize.
The output of this command will again show that your current project is `<your-project-id>`.

Note: Cloud Shell runs on a Google Compute Engine virtual machine and automatically authenticates using your cloud console login. Additionally, the service credentials associated with the virtual machine are automatically used by Application Default Credentials, so there is no need to run `gcloud auth login` or `gcloud auth application-default login`.

## Set up environment variables in Cloud Shell

In Cloud Shell, run

```
export PROJECT_ID=$(gcloud config get project)
export ORGANIZATION_ID=$(gcloud projects describe "$PROJECT_ID" --format="value(parent.id)")
```

And then confirm

```
echo $PROJECT_ID
echo $ORGANIZATION_ID
```

## Configure the Organization policies.

```
gcloud resource-manager org-policies delete constraints/compute.requireShieldedVm --organization=$ORGANIZATION_ID
gcloud resource-manager org-policies delete constraints/compute.requireOsLogin --organization=$ORGANIZATION_ID
gcloud resource-manager org-policies delete constraints/compute.vmExternalIpAccess --organization=$ORGANIZATION_ID
gcloud resource-manager org-policies delete constraints/iam.allowedPolicyMemberDomains --organization=$ORGANIZATION_ID
```

Note: if you do not have `Organization Policy Administrator`, you will receive a permissions error when you run these. To install GENIE, the policies above need to either be not enforced or deleted.

## Enable the following APIs within your project

- Cloud Resource Manager API
- Compute Engine API (compute.googleapis.com)

## Confirm the prerequsisite software is installed in Cloud Shell.

The following software and versions are required to deploy GENIE:

- `python >= 3.9`
- `terraform >= v1.3.7`

Acceptable versions of `python` and `terraform` should already be installed in Cloud Shell. To confirm, run the following in Cloud Shell.

```
python --version
terraform --version
```

## Note on Cloud Shell

The Cloud Shell VM is ephemeral. If you log out or your Cloud Shell stops due to inactivity, you will need to rerun these commands to reset the environment variables:

```
export PROJECT_ID=$(gcloud config get project)
export ORGANIZATION_ID=$(gcloud projects describe "$PROJECT_ID" --format="value(parent.id)")
```

While the Cloud Shell VM is ephemeral, your `$HOME` folder resides on a persistent disk so files in that directory persist between Cloud Shell sessions. By default, when you log into Cloud Shell you should be in your `$HOME` directory.

You can check by running

```
echo $HOME
```

and then

```
pwd
```

to see your current directory.

## Clone the repo

At this point, you are ready to clone the latest GENIE code to your Cloud Shell.

Run the command below to clone the repo into a local folder called `core-solution-services` in your current Cloud Shell directory (make sure it is within your `$HOME` directory)

```
git clone https://github.com/GoogleCloudPlatform/core-solution-services
cd core-solution-services
```

Until stated otherwise, the remaining steps should be done from the `core-solution-services` directory in Cloud Shell.

## Set up Python virtual environment

```
python -m venv .venv
```

```
source .venv/bin/activate
```

```
pip install -U "solutions-builder==1.18.1"
```

```
sb version
```

## Configure software

```
gcloud config set project ${PROJECT_ID}
```

```
gcloud auth configure-docker us-docker.pkg.dev
```

```
sb set project-id ${PROJECT_ID}
```

Enter 'Y' at the prompt.

You have now confirmed that your GCP organization, project, Cloud Shell environment variables and libraries are ready for the next step, to create the jump host.

# 2. Create the jump host

## Deploy the jump host

```
sb infra apply 0-jumphost
```

Enter 'Y' and 'yes' when prompted

Once the script completes in the Cloud Shell, the jump host VM has been deployed. Run the command below to save the zone of the jump host, we will use it while SSH-ing.

```
export JUMP_HOST_ZONE=$(gcloud compute instances list --filter="name=(jump-host)" --format="value(zone)")
```

## SSH to the jump host and confirm it is ready

You are now able to SSH to the jump host from Cloud Shell. Run the following:

```
gcloud compute ssh jump-host --zone=${JUMP_HOST_ZONE} --tunnel-through-iap --project=${PROJECT_ID}
```

You may be asked to create the `.ssh` directory. Enter `Y` to continue and press enter when asked for a passphrase.

On the jump host, it is likely that the the required software is still installing (usually takes 5-10 minutes after deployment).
You can check if all software is installed and the jump host is ready running:

```
ls -la /tmp/jumphost_ready
```

The output will be `No such file or directory` until the `jumphost_ready` file is created.
Once you no longer see the error when running the command, the file exists and the jump host is ready for the next step.

## Authenticate on the jump host

```
gcloud auth login
gcloud auth application-default login
gcloud auth configure-docker us-docker.pkg.dev
```

## Clone the repo on the jump host

```
git clone https://github.com/GoogleCloudPlatform/core-solution-services
cd core-solution-services
```

Unless specifically stated otherwise, the remaining steps should all be done from the `core-solution-services` directory of the jump host.

## Configure the jump host environment

```
export PROJECT_ID=$(gcloud config get project)
```

```
sb set project-id ${PROJECT_ID}
```

## Select domain name

To deploy the GENIE backend, you need a domain name that can be mapped (via DNS) to the IP address of the GENIE microservices you will be deploying in Steps 3 and 4.
The RIT team owns the `cloudpssolutions.com` domain and can create a subdomain for you of the form `<your-project-id>.cloudpssolutions.com`. These instructions assume that you
will create a domain name in this format.

There are instructions later (at the end of Step 3) for how to request that the RIT team create the DNS A record that maps your subdomain to the IP address of your backend GENIE microservices.

```
export DOMAIN_NAME=${PROJECT_ID}.cloudpssolutions.com
```

```
export API_BASE_URL=https://${DOMAIN_NAME}
```

```
sb vars set domain_name ${DOMAIN_NAME}
```

Finally, save all the environment variables we have set thus far in a script that runs every tiem you SSH to the jump host, so you will not have to reset them

```
sudo bash -c "cat << EOF >> /etc/profile.d/genie_env.sh
export DOMAIN_NAME=$DOMAIN_NAME
export API_BASE_URL=https://${DOMAIN_NAME}
export SKAFFOLD_DEFAULT_REPO=us-docker.pkg.dev/${PROJECT_ID}/default
EOF"
```

To check that the variables were updated in this file

```
cat /etc/profile.d/genie_env.sh
```

You have now fully deployed the jump host and are ready for the next step, to deploy the GENIE backend microservices.

# 3. Deploy the GENIE backend microservices

## Apply the bootstrap terraform

```
sb infra apply 1-genie-backend
```

Enter 'Y' and 'yes' when prompted

## Apply the foundations terraform

```
sb infra apply 2-foundation
```

Enter 'Y' and 'yes' when prompted

## Apply the GKE and ingress install

```
sb infra apply 3-gke
```

Enter 'Y' and 'yes' when prompted

```
sb infra apply 3-gke-ingress
```

Enter 'Y' and 'yes' when prompted

The output of this step should start with something similar to below. Save the IP address that is provided.

```
ingress_ip_address = [
  {
    "address" = "34.8.216.192"
    "address_type" = "EXTERNAL"
    "creation_timestamp" = "2024-11-11T15:12:34.332-08:00"
```

Update the jump host with additional environment variables

```
export REGION=$(gcloud container clusters list --filter=main-cluster --format="value(location)")
```

And update the saved environment variables on the jump host

```
sudo bash -c "echo 'export REGION=$REGION' >> /etc/profile.d/genie_env.sh"
```

## Apply the LLM service infarstructure

```
sb infra apply 4-llm
```

Enter 'Y' and 'yes' when prompted

## Connect to GKE cluster

Get credentials for the GKE cluster

```
gcloud container clusters get-credentials main-cluster --region ${REGION} --project ${PROJECT_ID}
```

Check that you can connect to the cluster and see the nodes running

```
kubectl get nodes
```

## Set up a vector database

RAG requires a vector database. This deployment uses a CLoudSQL PostgreSQL DB with the PGVector extension as the vector database.

The command below will create a secret called `postgres-user-passwd`.

```
gcloud secrets create "postgres-user-passwd"
```

In the command below, replace `<your-postgres-password>` with the password you would like to use, and SAVE THE DATABASE PASSWORD.

```
echo '<your-postgres-password>' | gcloud secrets versions add "postgres-user-passwd" --data-file=-
```

Create a CLoudSQL PostgreSQL instance

```
./utils/cloudsql_db.sh
```

The output of this script will look like the following

```
Cloud SQL Host IP address is 10.60.0.2
```

SAVE THE DATABASE IP ADDRESS.

```
export PG_HOST=<db-host-IP-address>
```

Add the PGVector extension

```
kubectl run psql-client --rm -i --tty --image ubuntu -- bash
```

Once inside the pod, run

```
apt update -y && apt install -y postgresql-client
```

In the next command, replace <your-postgres-password> with the DB password you saved.
``
export PGPASSWORD=<your-postgres-password>

```
In the next command, replace <pghost-ip-address> with the DB IP address you saved.
``
export PGHOST=<pghost-ip-address>
```

Then run

```
psql -U postgres -c "CREATE DATABASE pgvector"
psql -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector"
exit
```

The last command exits the temporary pod

Update the environment variables

```
sudo bash -c "echo 'export PG_HOST=${PG_HOST}' >> /etc/profile.d/genie_env.sh"
```

## Deploy backend microservices
