# GENIE React Frontend
This component is a REACT based frontend UI for GENIE.

# Install

You must deploy GENIE first before deploying this frontend app.  See [the install guide for GENIE.](../../INSTALL.md)

## Prerequisites

The following prerequisites must be installed to deploy the React frontend app:


| Tool                | Required Version | Installation                                                                                                                                                                                        |
|---------------------|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `npm`               | `>= 10.2`        | [Mac](https://nodejs.org/en/download/) • [Windows](https://nodejs.org/en/download/) • [Linux](https://nodejs.org/en/download/package-manager/) |
| `firebase CLI`      | `>= v13.1.0`     | `utils/install_firebase.sh v13.1.0` |

## Jump host installation
If you are installing from the jump host, install npm and the firebase CLI using the links above.

# Build and deploy the app

## Add Google identity provider

Add Google as an identity provider.  You can do this in the [GCP console](https://console.cloud.google.com/customer-identity/providers) or in the [Firebase console](https://console.firebase.google.com/).  In firebase, navigate to Build > Authentication > Sign-in Method.

## Install dependencies
Execute all commands below from the `components/frontend_react/src` directory.  You only need to install dependencies once, unless you update the app.

```bash
npm install
```

## Configure firebase

- Edit `.firebaserc` to set your project id
- Create your app in firebase:
```bash
firebase apps:create web <your-app-name>
```

- Run the `firebase apps:sdkconfig WEB` command printed as the output of the `apps:create` command:
```bash
firebase apps:sdkconfig WEB <your-firebase-app-id>
```

### Edit deployment config files
- Using the output of the `firebase apps:sdkconfig` command edit the config.production.env file to set all the variable values present there.
- Copy the file to `.env.production` and `.env.development`:
```bash
cp config.production.env .env.production
cp config.production.env .env.development
```

## Build for production
You should build the app on first deploy, and every time you make updates to the app.

```bash
npm run build
```


## Deploy with firebase
Deploy the app to firebase hosting with the following command:

```bash
firebase deploy --only hosting
```

# Development

## Run a local dev server
This command will start a local instance of the app for development.

```bash
npm run dev
```

