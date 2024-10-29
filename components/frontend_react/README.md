# GENIE React Frontend
This component is a REACT based frontend UI for GENIE.

## Install

You must deploy GENIE first before deploying this frontend app.  See [the install guide for GENIE.](../../INSTALL.md)

### Prerequisites

The following prerequisites must be installed to deploy the React frontend app:


| Tool                | Required Version | Installation                                                                                                                                                                                        |
|---------------------|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `npm`               | `>= 10.2`        | [Mac](https://nodejs.org/en/download/) • [Windows](https://nodejs.org/en/download/) • [Linux](https://nodejs.org/en/download/package-manager/) |
| `firebase CLI`      | `>= v13.1.0`     | `utils/install_firebase.sh v13.1.0` |

### Jump host installation
If you are installing from the jump host, install npm and the firebase CLI using the links above.

## Build and deploy the app

### Add Google identity provider

Add Google as an identity provider.  You can do this in the [GCP console](https://console.cloud.google.com/customer-identity/providers) or in the [Firebase console](https://console.firebase.google.com/).  In firebase, navigate to Build > Authentication > Sign-in Method. Refer to authentication component [README.md](https://github.com/GPS-Solutions/core-solution-services/blob/main/components/authentication/README.md) for more information.

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


## Install dependencies
Execute all commands below from the `components/frontend_react/webapp` directory.  You only need to install dependencies once, unless you update the app.

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

### Authorizing Redirect URIs (OAuth 2.0 Authentication)
In the Google Cloud Console -> APIs & Services -> [Credentials](https://console.cloud.google.com/apis/credentials):
- Click on your default Web Client(auto-created by Google Service).
- Under Authorized redirect URIs, add the following with your domain name:
  - `https://<your-domain-name>.web.app/__/auth/handler`

>This allows your backend to authorize your frontend web app in requesting an OAuth 2.0 authentication.Without this authorized redirect URIs, you will receive an unauthorized error.


# Development

## Run a local dev server
This command will start a local instance of the app for development.

```bash
npm run dev
```
