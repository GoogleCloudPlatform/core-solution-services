# GENIE React Frontend
This component is a REACT based frontend UI for GENIE.

# Install

You must deploy GENIE first before deploying this frontend app.  See [the install guide for GENIE.](../../INSTALL.md)

## Prerequisites

The following prerequisites are necessary to deploy the React frontend app:


| Tool                | Required Version | Installation                                                                                                                                                                                        |
|---------------------|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `npm`               | `>= 10.2`        | [Mac](https://nodejs.org/en/download/) • [Windows](https://nodejs.org/en/download/) • [Linux](https://nodejs.org/en/download/package-manager/) |
| `firebase CLI`      | `>= v13.1.0`     | `utils/install_firebase.sh v13.1.0` |
| `solutions-builder` | `>= v1.17.19`    | https://pypi.org/project/solutions-builder/ |

## Check solution builder

Check the installation of the solution-builder tool:
```
sb version
```

If solution builder is not present, you need to activate a Python virtual environment with the solution-builder package installed.  You can do this using the following commands:

Start from the top level directory of this component:
```
cd components/frontend_react
```

Create a virtual environment and activate it.
```
python3 -m venv .venv
source .venv/bin/activate
```

Install the Solutions Builder package:
```
pip install -U solutions-builder
```

## Configuration for the app

### Set PROJECT_ID and authenticate with gcloud
```
export PROJECT_ID=<your-project-id>
gcloud config set project ${PROJECT_ID}
gcloud auth login
gcloud auth application-default login
```

### Set environment variables
- To get your firebase API key, go to the firebase console settings for your project: https://console.firebase.google.com/project/[your-project-id]/settings/general
- The "genie domain name" is the domain name of your deployed genie backend.
- The contact email is the email of an admin for your app.
```
export FIREBASE_API_KEY=<your-firebase-api-key>
export DOMAIN_NAME=<your-domain-name>
export CONTACT_EMAIL=<your-contact-email>
```

Run these commands from the top-level directory of the repository folder to update the config of your local repo.
```
cd core-solution-services

sb set project-id ${PROJECT_ID}
sb vars set domain-name ${DOMAIN_NAME}
sb vars set firebase-api-key ${FIREBASE_API_KEY}
sb vars set contact-email ${CONTACT_EMAIL}
```

# Build and deploy the app

## Add Google identity provider

Add Google as an identity provider.  You can do this in the [GCP console](https://console.cloud.google.com/customer-identity/providers?referrer=search&project=[your-project-id]) or in the [Firebase console](https://firebase.corp.google.com/project/your-project-id/authentication/providers). 


## Install dependencies
Execute all commands below from the `components/frontend_react/src` directory.

```bash
npm install
```

## Build for production

```bash
npm run build
```

## Deploy with firebase

- Edit `.firebaserc` to set your project id
- Create your app in firebase:
```bash
firebase apps:create web <your-app-name>
```

- Run the `firebase apps:sdkconfig WEB` command printed as the output of the `apps:create` command:
```bash
firebase apps:sdkconfig WEB <your-firebase-app-id>
```

### Edit deployment config file
- Using the output of the `firebase apps:sdkconfig` command edit the config.production.env file to set all the variable values present there.
- Copy the file to `.env.production`:
```bash
cp config.production.env .env.production
```

### Run firebase deploy
Deploy the app to firebase hosting with the following command:

```bash
firebase deploy --only hosting
```

# Development

## Run a local dev server

```bash
npm run dev
```

