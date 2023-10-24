# Authentication Service

## Setup

### Enable Identity Platform

- Go to GCP console and [enable the Identity Platform](https://console.cloud.google.com/customer-identity).
  ![Enable IDP](../../.github/assets/idp_enable.png)

- Add an Email/Password provider [in Identity Platform page](https://console.cloud.google.com/customer-identity/providers):
  ![Add IDP provider](../../.github/assets/idp_add_provider.png)

- Make sure to enable the Email/Password provider as the screenshot below:
  ![Alt text](../../.github/assets/idp_emailpass.png)

### Create users

Please verify that email/password provider is enabled.

Get the IP address for the GKE ingress endpoint:
```
IP_ADDRESS=$(gcloud compute addresses describe gke-ingress-ip --global --format='value(address)')
BASE_URL="http://$IP_ADDRESS"
```

In the source code folder:
```
pip install -r components/common/requirements.txt
pip install -r components/authentication/requirements.txt
PYTHONPATH=components/common/src/ python components/authentication/scripts/user_tool.py create_user --base-url=$BASE_URL
```
- You can use the IP address, e.g. http://127.0.0.1/
- This will register the user to Identity Platform and a user record in Firestore (in `users` collection).

Once complete, it will show the ID token in the output. E.g.:
```
User 'user@my.domain.com' created successfully. ID Token:

<my-id-token...>
```

### Get ID Access Token

Get the access token for a particular user:
```
PYTHONPATH=components/common/src/ python components/authentication/scripts/user_tool.py get_token
```
- This will print out the token in the terminal.

```
Signed in with existing user 'user@my.domain.com'. ID Token:

<my-id-token...>
```
