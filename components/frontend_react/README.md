# GENIE React Frontend
This component is a REACT based frontend UI for GENIE.

## Install

You must deploy GENIE first before deploying this frontend app. See [the install guide for GENIE.](../../INSTALL.md)

### Prerequisites

The following prerequisites must be installed to deploy the React frontend app. Note that these prerequisites will be installed by the deploy script:

| Tool                | Required Version | Installation                                                                                                                                                                                        |
|---------------------|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `npm`               | `>= 10.2`        | [Mac](https://nodejs.org/en/download/) • [Windows](https://nodejs.org/en/download/) • [Linux](https://nodejs.org/en/download/package-manager/) |
| `firebase CLI`      | `>= v13.1.0`     | `utils/install_firebase.sh v13.1.0` |



## Build and Deploy the app using the deploy script

To deploy the app the first time, use the provided `deploy.sh` script. This script will install all necessary dependencies, setup and configure Firebase, configure the app itself, build the app, and deploy it.

### Usage

Run the script in the `components/frontend_react/` with the following command, replacing the placeholders with your actual values:

```bash
./deploy.sh <your-project-id> <your-firebase-app-name> <your-domain-name> <your-contact-email>
```

Example:

```bash
./deploy.sh my-genie-project my-firebase-app mydomain.com contact@mydomain.com
```

This command will:
- Install `jq`, `nvm`, Node.js, and the Firebase CLI.
- Configure Firebase with your project ID and app name.
- Populate the `.env.production` and `.env.development` files with the necessary environment variables.
- Build the app for production.
- Deploy the app to Firebase hosting.

## Build and deploy the app on the command line

After the initial install, to build and deploy the app again (say to deploy updates) follow these steps:

- Build the app

```bash
npm run build
```

- Deploy with firebase

```bash
firebase deploy --only hosting
```

### Add Google identity provider

Add Google as an identity provider.  This must be done manually via the console currently.  We recommend you do this in the [Firebase console](https://console.firebase.google.com/), because it automatically creates a web client for you.  In firebase, navigate to Build > Authentication > Sign-in Method.  

If you are an expert in OAuth authentication you can also configure the Google identity provider in the [GCP console](https://console.cloud.google.com/customer-identity/providers).  Refer to authentication component [README.md](https://github.com/GPS-Solutions/core-solution-services/blob/main/components/authentication/README.md) for more information.

### Authorizing User Domains during Sign-in
The frontend_react component provides an initial check for authorizing user domains during a user's sign-in process with Google. Thus, you'll need to change the `authProviders` and `authorizedDomains` attribute within `AppConfig` with your user's or client's organizational domain.

Under the `frontend_react/src/src/utils/AppConfig.ts` file:

```
export const AppConfig: IAppConfig = {
  siteName: "GenAI for Public Sector",
  locale: "en",
  logoPath: "/assets/images/rit-logo.png",
  simpleLogoPath: "/assets/images/rit-brain.png",
  imagesPath: "/assets/images",
  theme: "light",
  authProviders: ["google", "microsoft", "facebook", "password"],
  authorizedDomains: [/@google\.com$/i, /@gmail\.com$/i, /@\w+\.altostrat\.com$/i],
}
```

> Add or Change the `authProviders` and `authorizedDomains` to your respective input.

>**NOTE:** The `authorizedDomain` attributes are in reg expressions. (i.e "/@gmail\.com$/i")

> In addition to this frontend configuration, you'll need to ensure the [Google Cloud Identity](https://console.cloud.google.com/customer-identity/providers) has added the providers on Google Cloud's backend. Each provider (e.g Microsoft, Facebook) will have require an authentication client on the provider-side that Google Cloud refers to via `App ID` and `App Secret` to direct authentication. Ensure Authorized Redirect URIs are set on the authentication provider side. See provider's documentation for more info. 

### Authorizing Redirect URIs (OAuth 2.0 Authentication)
If you set up auth the Google Identity platform you will need to update the Web Client for authentication.
- Navigate to the Google Cloud Console -> APIs & Services -> [Credentials](https://console.cloud.google.com/apis/credentials)
- Click on your default Web Client (auto-created by Firebase).
- Under Authorized redirect URIs, add the following with your domain name:
  - `https://<your-domain-name>.web.app/__/auth/handler`

>This allows your backend to authorize your frontend web app in requesting an OAuth 2.0 authentication. Without this authorized redirect URIs, you will receive an unauthorized error.

# Development

## Run a local dev server
This command will start a local instance of the app for development.

```bash
npm run dev
```
