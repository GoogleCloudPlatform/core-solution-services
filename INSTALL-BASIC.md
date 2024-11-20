# Overview of basic install

The goal of a **basic** GENIE install is to use the latest GENIE code to deploy an instance of the GENIE software stack into a GCP project that you own.

At the end of this install, you will be able to use the GENIE React front end to call the GENIE microservices,
both of which are deployed in your GCP project, and run a RAG demo.

There are many possible variations for how to deploy and develop with GENIE.
The following are prescriptive steps to deploy a basic GENIE configuration, using the simplest approach applicable to as many starting environments as possible.
Once this installation is complete, you can dive deeper into other GENIE READMEs to deploy and work with additional features.

There are four logical steps to deploy GENIE:

1. **Set up**. Create a new GCP Project, set up Cloud Shell, clone the GENIE code.
2. **Create a jump host**. We use Cloud Shell to deploy a jump host (virtual machine running in your GCP project) that will be used to do the actual GENIE deployment. We deploy from a jump host to ensure that all deployments start from the same virtual machine configuration.
3. **Deploy GENIE backend**. From the jump host, deploy the GENIE infrastructure (GKE, databases, etc) and microservices.
4. **Deploy GENIE front end**. From the jump host, deploy the GENIE front end application.

# 1. Set up

## Create a new GCP Project

In your GCP Organization, create a new GCP Project and note the `Project ID`.
To deploy GENIE, certain organization policies must be either not enforced or deleted.
Depending on your organization's specific default policies, you
may need `Organization Policy Administrator` permission to change some policies to allow for the GENIE install in the steps below.

## Open Cloud Shell

In a web browser, go to the [cloud console](https://console.cloud.google.com/) and select the project you just created.

At the top right, click the square icon with the prompt `>_` to Activate Cloud Shell. The Cloud Shell terminal opens at the bottom of the page and, along with some other text, you should see the following at the top.

```
Your Cloud Platform project in this session is set to `<your-project-id>`.
```

This confirms your Cloud Shell terminal is configured to connect to the project you just created.

## Authorize for using gcloud CLI

```
gcloud config list
```

When you run this, you will be asked to Authorize Cloud Shell to use your credentials for the `gcloud` CLI commands. Click Authorize.
The output of this command will again show that your current project is `<your-project-id>`.

Note: Cloud Shell runs on a Google Compute Engine virtual machine and automatically authenticates using your cloud console login. Additionally, the service credentials associated with the virtual machine are automatically used by Application Default Credentials, so there is no need to run `gcloud auth login` or `gcloud auth application-default login`.

## Set up environment variables in Cloud Shell

In Cloud Shell, run

```
export PROJECT_ID=$(gcloud config get project)
```

```
export ORGANIZATION_ID=$(gcloud projects describe "$PROJECT_ID" --format="value(parent.id)")
```

And then confirm

```
echo $PROJECT_ID
```

```
echo $ORGANIZATION_ID
```

The command above may not pull the `ORGANIZATION_ID` in all contexts. If the value of ORGANIZATION_ID is still blank,
check for it in the [cloud console](https://console.cloud.google.com/), and then set it using this command.

```
export ORGANIZATION_ID=<your-organization-id>
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

```
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable compute.googleapis.com
```

## Confirm the prerequisite software is installed in Cloud Shell.

The following software and versions are required to deploy GENIE:

- `python >= 3.9`
- `terraform >= v1.3.7`

Acceptable versions of `python` and `terraform` should already be installed in Cloud Shell. To confirm, run the following in Cloud Shell.

```
python --version
```

```
terraform --version
```

## Clone the repo

At this point, you are ready to clone the latest GENIE code to your Cloud Shell.

Run the command below to clone the repo into a local folder called `core-solution-services` in your current Cloud Shell directory (make sure it is within your `$HOME` directory)

```
git clone https://github.com/GoogleCloudPlatform/core-solution-services
```

Then, change to the repo directory.

```
cd core-solution-services
```

Until stated otherwise, the remaining steps should be done from the `core-solution-services` directory in Cloud Shell.

## Set up Python virtual environment

Run the following commands to install `solutions-builder`, which is required for GENIE deployment.

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

Follow these instructions if you need to [reconnect to Cloud Shell](#reconnect-to-cloud-shell), such as after a session timeout.

# 2. Create the jump host

## Deploy the jump host

```
sb infra apply 0-jumphost
```

Enter 'Y' and 'yes' when prompted

Once the script completes in the Cloud Shell, the jump host VM has been deployed. Run the command below to save the zone of the jump host.
We will use it while SSH-ing.

```
export JUMP_HOST_ZONE=$(gcloud compute instances list --filter="name=(jump-host)" --format="value(zone)")
```

## SSH to the jump host and confirm it is ready

You are now able to SSH to the jump host from Cloud Shell. Run the following:

```
gcloud compute ssh jump-host --zone=${JUMP_HOST_ZONE} --tunnel-through-iap --project=${PROJECT_ID}
```

You may be asked to create the `.ssh` directory. Enter `Y` to continue and press `Enter` when asked for a passphrase.

On the jump host, it is likely that the the required software is still installing (usually takes 5-10 minutes after deployment).
You can check if all software is installed and the jump host is ready by running:

```
ls -la /tmp/jumphost_ready
```

The output will be `No such file or directory` until the `jumphost_ready` file is created.

Once you no longer see the error when running the command, the file exists and the jump host is ready for the next step.

## Authenticate on the jump host

```
gcloud auth login --update-adc
```

```
gcloud auth configure-docker us-docker.pkg.dev
```

## Clone the repo on the jump host

```
git clone https://github.com/GoogleCloudPlatform/core-solution-services
```

```
cd core-solution-services
```

Until specifically stated otherwise, the remaining steps should all be done from the `core-solution-services` directory of the jump host.

## Configure the jump host environment

```
export PROJECT_ID=$(gcloud config get project)
```

```
sb set project-id ${PROJECT_ID}
```

## Select domain name

To deploy the GENIE backend, you need a domain or subdomain that can be mapped (via DNS) to the IP address of the GENIE microservices you will be deploying in Steps 3 and 4.

If you are using your own domain name and will set up the DNS A record yourself, then provide it here as the `DOMAIN_NAME` value below.

```
export DOMAIN_NAME=<your-domain-name>
```

Alternatively, the RIT team owns the `cloudpssolutions.com` domain. For GPS internal users we can create a subdomain of the form `<your-project-id>.cloudpssolutions.com`.
If you plan to deploy GENIE using this approach, run the command below instead.

```
export DOMAIN_NAME=${PROJECT_ID}.cloudpssolutions.com
```

**Save the `DOMAIN NAME`** you have specified.

Later, the instructions in Step 3 will go over how to get the DNS A record created.

Continue setting the environment variables.

```
export API_BASE_URL=https://${DOMAIN_NAME}
```

```
sb vars set domain_name ${DOMAIN_NAME}
```

Finally, save all the environment variables we have set thus far in a script that runs every time you SSH to the jump host,
so you will not have to reset them.

```
sudo bash -c "cat << EOF >> /etc/profile.d/genie_env.sh
export DOMAIN_NAME=$DOMAIN_NAME
export API_BASE_URL=https://${DOMAIN_NAME}
export SKAFFOLD_DEFAULT_REPO=us-docker.pkg.dev/${PROJECT_ID}/default
EOF"
```

You can check that the variables have been saved to this file by running this command:

```
cat /etc/profile.d/genie_env.sh
```

You have now fully deployed the jump host and are ready for the next step --> Deploying the GENIE backend microservices.

# 3. Deploy the GENIE backend

## Apply the bootstrap terraform

```
sb infra apply 1-bootstrap
```

Enter 'Y' and 'yes' when prompted

## Apply the foundations terraform

```
sb infra apply 2-foundation
```

Enter 'Y' and 'yes' when prompted

Note: there is a known timing issue with this step which can result in a Firebase error. Check the [troubleshooting guide](#firebase-database-already-exists) for information about this error, and the fix.

## Apply the GKE and ingress install

```
sb infra apply 3-gke
```

Enter 'Y' and 'yes' when prompted

```
sb infra apply 3-gke-ingress
```

Enter 'Y' and 'yes' when prompted

The output of this step should start with something similar to below.

```
ingress_ip_address = [
  {
    "address" = "<your-ip-address>"
    "address_type" = "EXTERNAL"
    "creation_timestamp" = "2024-11-11T15:12:34.332-08:00"
```

**Save the ingress IP address** that is provided.

Update the jump host with additional environment variables

```
export REGION=$(gcloud container clusters list --filter=main-cluster --format="value(location)")
```

And update the file that saves the environment variables

```
sudo bash -c "echo 'export REGION=$REGION' >> /etc/profile.d/genie_env.sh"
```

## Offline: Create a DNS A record

The GENIE installation requires setting up a DNS A record that maps your domain or subdomain to your ingress IP address.

If you are using your own domain, create the DNS A record now.

If you plan to use a subdomain of `cloudpssolutions.com`, ping the `GENIE Solution Dev` chat space with your `DOMAIN_NAME` and
ingress IP address, and ask that an A record be created.

Once you start The DNS process, you can immediately resume the rest of the GENIE backend deployment here (Step 3).
The DNS A record will need to be operational to verify the deployment at the end of Step 3.

## Apply the LLM service infarstructure

```
sb infra apply 4-llm
```

Enter 'Y' and 'yes' when prompted

## Connect to GKE cluster

Get credentials for the GENIE GKE cluster that was deployed.

```
gcloud container clusters get-credentials main-cluster --region ${REGION} --project ${PROJECT_ID}
```

Check that you can connect to the cluster and see the nodes that are running.

```
kubectl get nodes
```

## Set up a vector database

RAG requires a vector database. This deployment uses a CloudSQL for PostgreSQL DB with the PGVector extension as the vector database.

The command below will create a secret called `postgres-user-passwd`.

```
gcloud secrets create "postgres-user-passwd"
```

In the command below, replace `<your-postgres-password>` with the password you would like to use.

```
echo '<your-postgres-password>' | gcloud secrets versions add "postgres-user-passwd" --data-file=-
```

**Save the database password** you just created.

Create a CloudSQL for PostgreSQL DB instance

```
./utils/cloudsql_db.sh
```

The output of this script will look like the following (IP address will be different)

```
Cloud SQL Host IP address is 192.168.0.10.
```

**Save the database IP address**.

In the command below, replace `<db-host-IP-address>` with the database IP address.

```
export PG_HOST=<db-host-IP-address>
```

## Add the PGVector extension

To add the PGVector extension to the PostreSQL database you created, we need to run commands from a temporary pod. Run the command below
to connect to a temporary pod.

```
kubectl run psql-client --rm -i --tty --image ubuntu -- bash
```

Once inside the pod, run

```
apt update -y && apt install -y postgresql-client
```

In the next command, replace `<your-postgres-password>` with the DB password you saved previously.

```
export PGPASSWORD=<your-postgres-password>
```

In the next command, replace `<pghost-ip-address>` with the DB IP address you saved.

```
export PGHOST=<pghost-ip-address>
```

Then run

```
psql -U postgres -c "CREATE DATABASE pgvector"
psql -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector"
exit
```

The `exit` command exits the temporary pod.

Back on the jump host now, update the environment variables again

```
sudo bash -c "echo 'export PG_HOST=${PG_HOST}' >> /etc/profile.d/genie_env.sh"
```

## Deploy backend microservices

At this point, all the required environment variables should already be set on the jump host. To confirm, you can run the
following and check the output.

```
echo $PROJECT_ID
echo $NAMESPACE
echo $PG_HOST
echo $DOMAIN_NAME
echo $API_BASE_URL
echo $SKAFFOLD_DEFAULT_REPO
```

From the `core-solution-services` directory in the jump host, run the command below to deploy the backend microservices

```
skaffold run -p default-deploy -n $NAMESPACE
```

This step will take 15-20 minutes.

Note: At times we see errors when running this step. Check the [troubleshooting guide](#failed-to-download-openapi) for more information and next steps.

Once the step completes, check that the pods for the GENIE microservices are running.

```
kubectl get pods
```

You should see output similar to the following

```
NAME                                    READY   STATUS    RESTARTS   AGE
authentication-69bfb78d69-4j64d         1/1     Running   0          91m
frontend-flutterflow-5559bbcc85-rwvjg   1/1     Running   0          80m
frontend-streamlit-f7d7f7b5d-cjmjr      1/1     Running   0          80m
jobs-service-7ccc46f786-w5lr5           1/1     Running   0          85m
llm-service-799f986dcd-t852z            1/1     Running   0          89m
redis-master-0                          1/1     Running   0          84m
redis-replicas-0                        1/1     Running   0          84m
redis-replicas-1                        1/1     Running   0          84m
redis-replicas-2                        1/1     Running   0          83m
rules-engine-56dcd7bbb-sdpt5            1/1     Running   0          82m
tools-service-7ffc95556b-77656          1/1     Running   0          82m
user-management-6479c84668-p2c2l        1/1     Running   0          90m
```

## Deploy the microservices ingress

For the next step, change to the `ingress` folder

```
cd ingress
```

And then run

```
skaffold run -p default-deploy -n $NAMESPACE --default-repo="${SKAFFOLD_DEFAULT_REPO}"
```

This step should complete almost immediately. This kicks off the process of creating the managed certificate for
the microservices ingress IP. Creating the managed certificate could take from 15 minutes - 24 hours (though
unlikely).

Until the managed certificate is ACTIVE, the GENIE installation is not complete. You can check the status of the
managed certificate by running

```
kubectl get managedcertificate
```

Once the status is ACTIVE, you have completed the GENIE backend installation.

## Verify installation

To check if the GENIE backend has successfully been deployed, in a web browser load the microservices API pages -
make sure to replace `<your-project-id>` in the URLs below.

```
https://<your-project-id>.cloudpssolutions.com/authentication/api/v1/docs
https://<your-project-id>.cloudpssolutions.com/llm-service/api/v1/docs
```

When both of these pages load, the GENIE backend is deployed.

# 4. Deploy the GENIE front end

The front end is a React app that we will deploy to Firebase Hosting. We will use Google as the authentication provider to allow anyone with a google.com email address to log in.

## Add Google as a Firebase identity provider

In a web browser, go to the [Firebase console](https://firebase.corp.google.com/). Using the project selection options (this will depend on whether your Organization has previously used Firebase), select the project ID of the Google Cloud project you created to deploy GENIE. Note that you do not need to enable Google Analytics.

Your Google Cloud project will now also be a Firebase project of the same name.

Once the Firebase project is created, in the menu bar at the left select `Build` and then `Authentication`. If
necesary, click the `Get Started` button.

On the Authentication page, click the `Sign-in method` tab at the top.

Under Additional providers, select `Google`.

In the top right, click the `Enable` slider to enable the Google provider.

Select a support email for the project.

Once that is done, click Save.

## Install firebase on jump host

Using Cloud Shell, SSH to the jump host. Change to the `core-solution-services` directory

Run this to install the Firebase CLI.

```
utils/install_firebase.sh v13.1.0
```

When the install is complete, log in using the firebase CLI

```
firebase login --no-localhost
```

Make sure the quota project is set

```
gcloud auth application-default set-quota-project $PROJECT_ID
```

## Build the React front end

To build the front end, change to the `webapp` directory

```
cd components/frontend_react/webapp
```

Install the npm dependcies

```
npm install
```

## Configure Firebase app

In this directory, open the `.firebaserc` file.

Change `your-project-id` to be the project ID you created for the GENIE deploy. Save that file.

Run this command, substituting the project ID you created for the GENIE deploy for `<your-project-id>`

```
firebase apps:create web <your-project-id>-app
```

When that is complete, copy the last line of the input which should be in the form:

```
firebase apps:sdkconfig WEB 1:936005173737:web:292e7e9fa799dd1e070b78
```

Paste it and run it at the prompt.

The output is the configuration information for your app, and should look similar to this:

```
firebase.initializeApp({
  "projectId": "fed-ce-genie-workshop",
  "appId": "1:936005173737:web:292e7e9fa799dd1e070b78",
  "storageBucket": "fed-ce-genie-workshop.firebasestorage.app",
  "locationId": "us-central",
  "apiKey": "AIzaSyA6O3bPJGVjq4nngOBewJisQAcHVfY_QHM",
  "authDomain": "fed-ce-genie-workshop.firebaseapp.com",
  "messagingSenderId": "936005173737"
});
```

Open the `config.production.env` file, and update the default values in that file with the new values provided in the firebase app config.
Note that all fields in `config.production.env` are prefixed with `VITE_`.

For the fields not provided by Firebase app config

- for `VITE_PUBLIC_CONTACT_US_EMAIL`, use your email address.
- for `VITE_PUBLIC_API_ENDPOINT`, use `https://<your-project-id>.cloudpssolutions.com/llm-service/api/v1`
- for `VITE_PUBLIC_API_JOBS_ENDPOINT`, use `https://<your-project-id>.cloudpssolutions.com/llm-service/api/v1`

Save the updated `config.production.env` file.

From the `webapp` directory, run these comands

```
cp config.production.env .env.production
cp config.production.env .env.development
```

## Deploy the Firebase app

Build the app for production

```
npm run build
```

Deploy the app to Firebase

```
firebase deploy --only hosting
```

## Add the Redirect URI

In the Google Cloud console -> APIs & Services -> [Credentials](https://console.cloud.google.com/apis/credentials) section,
in the OAuth 2.0 Client IDs section, select the default Web Client that has been created for you.

Under Authorized redirect URIs, click `Add URI`. Add the following URI, substituting the project ID you created for the GENIE deploy for `<your-project-id>`

```
https://<your-project-id>.web.app
```

Click Save.

## Test the front end

In a new incognito browser window, go to

```
https://<your-project-id>.web.app
```

The Sign in page should load. Click Sign-in with your google.com email address.
Once sign in is complete,the GENIE main page should load.

Enter

```
Hello world
```

And Gemini should respond.

# Troubleshooting [Step 1](#1-set-up) | [Step 2](#2-create-the-jump-host) | [Step 3](#3-deploy-the-genie-backend) | [Step 4](#4-deploy-the-genie-front-end)

## Reconnect to Cloud Shell

If Cloud Shell stops due to inactivity or you need to log out, the VM is ephemeral and you will need to reset the environment variables the next time you open Cloud Shell in order to SSH to the jump host. You can reset them by running the commands below:

```

export PROJECT_ID=$(gcloud config get project)
export ORGANIZATION_ID=$(gcloud projects describe "$PROJECT_ID" --format="value(parent.id)")
export JUMP_HOST_ZONE=$(gcloud compute instances list --filter="name=(jump-host)" --format="value(zone)")

```

While the Cloud Shell VM is ephemeral, your `$HOME` directory resides on a persistent disk, so files in `$HOME` will persist between Cloud Shell sessions.
By default, when you log into Cloud Shell you should be in your `$HOME` directory

You can check what your `$HOME` directory is by running

```

echo $HOME

```

And check your current directory by running:

```

pwd

```

Once the environment variables are re-set in Cloud Shell, you can SSH to the jump host again using

```

gcloud compute ssh jump-host --zone=${JUMP_HOST_ZONE} --tunnel-through-iap --project=${PROJECT_ID}

```

## Firebase database already exists

There is a known error when running:

```

sb infra apply 2-foundation

```

That looks like this:

> Error: Error creating Database: googleapi: Error 409: Database already exists. Please use another database_id
>
> with google_firestore_database.database,
> on firestore_setup.tf line 42, in resource "google_firestore_database" "database":
> 42: resource "google_firestore_database" "database" {

The fix for this is below. Make sure to run all lines.

```

cd terraform/stages/2-foundation/
terraform import google_firestore_database.database "(default)"
cd -

```

Once you have run the fix, rerun the original step.

```

sb infra apply 2-foundation

```

## Failed to download openapi

When running this step

```

skaffold run -p default-deploy -n $NAMESPACE

```

This error has been seen, which we think is another timing issue.

```

error: error validating "STDIN": error validating data: failed to download openapi: Get "https://34.55.197.78/openapi/v2?timeout=32s": dial tcp 34.55.197.78:443: i/o timeout; if you choose to ignore these errors, turn validation off with --validate=false

```

To fix, log out of the jump host by typing `exit`.
[SSH back into the jump host](#reconnect-to-cloud-shell), and reauthenticate on the jump host.

Re-run the command

```

skaffold run -p default-deploy -n $NAMESPACE

```

Generally, the deploy will now complete.
