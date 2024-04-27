# GENIE React Frontend
This component is a REACT based frontend UI for GENIE.

# Install
You must deploy GENIE first before deploying this frontend app.  See [the install guide for GENIE.](../../INSTALL.md)

Start from the top level directory of this component:
```
cd components/frontend_react
```

## Check solution builder

Check the installation of the solution-builder tool:
```
sb version
```

If solution builder is not present, you need to activate a Python virtual environment with the solution-builder package installed.  You can do this using the following commands:

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
export GENIE_DOMAIN_NAME=<your-genie-domain-name>
export CONTACT_EMAIL=<your-contact-email>
```

Run these commands to update the config of your local repo.
```
sb set project-id ${PROJECT_ID}
sb vars set genie-domain-name ${GENIE_DOMAIN_NAME}
sb vars set firebase-api-key ${FIREBASE_API_KEY}
sb vars set contact-email ${CONTACT_EMAIL}
```

# Local Development
Execute all these commands from the `components/frontend_react/src` directory.

## Install dependencies

```bash
npm install
```

## Run a local dev server

```bash
npm run dev
```

## Build for production

```bash
npm run build
```

## Deploy with firebase
```bash
firebase deploy --only hosting
```

