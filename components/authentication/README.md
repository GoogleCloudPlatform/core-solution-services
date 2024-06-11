# Authentication Service

## Setup

### Enable Identity Platform

- Go to GCP console and [enable the Identity Platform](https://console.cloud.google.com/customer-identity).
  ![Enable IDP](../../.github/assets/idp_enable.png)

- Add an Email/Password provider [in Identity Platform page](https://console.cloud.google.com/customer-identity/providers):
  ![Add IDP provider](../../.github/assets/idp_add_provider.png)

- Make sure to enable the Email/Password provider as the screenshot below:
  ![Alt text](../../.github/assets/idp_emailpass.png)

## Automatic User Creation with whitelisted email domains

Set the following two environment variables:

```
export AUTH_AUTO_CREATE_USERS=true
export AUTH_EMAIL_DOMAINS_WHITELIST=google.com
```

- Please note that `AUTH_EMAIL_DOMAINS_WHITELIST` matches exact email domain, not wildcard support yet.

## Manually add Users

### Add users with the firebase console

Please verify that email/password provider is enabled.

You can add users to the platform in the [firebase console](https://console.firebase.google.com).

- Navigate to the console and select your project
- Navigate to the Authentication section (under Build > Authentication)
- Click "Add User" on the UX.
  ![Add User](../../docs/assets/add_user.jpg)
- Enter the email and password for the user.
- You can send a password reset email to the user via firebase so the user can create their own password.
- The user can now log in via the UX apps for the platform.
- A user model will be created for the user when they log in. Note that user model will be populated with test first name/last name and should be updated if you care about those fields.

### Add users with the create_users script

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

### Get an ID Access Token

Get an access token for a particular user:

```
PYTHONPATH=components/common/src/ python components/authentication/scripts/user_tool.py get_token
```

- This will print out the token in the terminal.

```
Signed in with existing user 'user@my.domain.com'. ID Token:

<my-id-token...>
```

## Notes on Refresh token flow

[Difference Between OAuth, OpenID Connect, and SAML](https://www.okta.com/identity-101/whats-the-difference-between-oauth-openid-connect-and-saml/) - helpful background

Code involved in this flow:

- `main.py` of a GENIE service
- `common.utils.auth_service.validate_token`
  - `common.utils.auth_service.validate_oauth_token` (unless it is a service account). This calls the GENIE /validate API endpoint.
- `components/authentication/src/routes/validate_token.validate_id_token`
  - `components/authentication/src/services/validation_service.validate_token`
    - `common.utils.cache_service.get_token_cache`
    - `firebase.admin.auth.verify_id_token`
  - `common.utils.user_handler.get_user_by_email`

Explanation of each step:

1. _main.py_. The main.py of every service sets up the FastAPI router for that service using code similar to this, which is from `components/llm_service/src/main.py` (see below).
   `Depends(valdate_token)` is the FastAPI syntax that requires that every call to the API first invokes `common.utils.auth_service.validate_token` function with the payload.

```
api = FastAPI(
    title=service_title,
    version="latest",
    # docs_url=None,
    # redoc_url=None,
    dependencies=[Depends(validate_token)]
    )
```

2.  `common.utils.auth_service.validate_token`. This function calls `common.utils.auth_service.validate_oauth_token`, which checks for a credentials entry in the payload, and constructs the URL of the GENIE authentication service `/validate` endpoint. It passes the scheme and the credentials as part of the Authorization headers. The `/validate` endpoint is mapped to the `components/authentication/src/routes/validate_token` function.

```
  if not token:
    raise TokenNotFoundError("Unauthorized: token is empty.")

  token_dict = dict(token)
  if token_dict["credentials"]:
    api_endpoint = f"http://{AUTH_SERVICE_NAME}/{AUTH_SERVICE_NAME}/" \
        "api/v1/validate"
    res = requests.get(
        url=api_endpoint,
        headers={
            "Content-Type": "application/json",
            "Authorization":
                f"{token_dict['scheme']} {token_dict['credentials']}"
        },
        timeout=60)
    data = res.json()
```

3. `components/authentication/src/routes/validate_token`. This function does two things:

- Calls `components/authentication/src/services/validation_service.validate_token` (see code below)
  - Checks for it in the redis cache - uses `common.utils.cache_service.get_token_cache`
  - If its not in the cache, calls `firebase.admin.auth.verify_id_token`. Any errors raised from `verify_id_token` are not caught here and will propogate back to the calling function
  - Returns a decoded token

```
  token = bearer_token
  decoded_token = None

  cached_token = get_token_cache(f"cache::{token}")
  decoded_token = cached_token if cached_token else verify_id_token(token)
  if not cached_token:
    cached_token = set_token_cache(f"cache::{token}", decoded_token)
    Logger.info(f"Id Token caching status: {cached_token}")

  Logger.info(f"Id Token: {decoded_token}")
  return decoded_token
```

- Calls `common.utils.user_handler.get_user_by_email` to make sure the user is in firestore

## Front end files involved in authentication

- `src\navigation\SignInForm.tsx`
- src\contexts\auth.tsx
- src\utils\api.ts
- src\utils\firebase.ts

## Notes on Sign in token flow

For the RIT standard SPA starter app the sign in code is in `src\navigation\SignInForm.tsx`
The code handles both sign in with Google and sign in with email and password, using `firebase/auth` functions (see below). It does not use the GENIE `/signin` endpoint.

```
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
} from "firebase/auth"
```

## Notes on calling GENIE APIs

Pages that import firebase/auth

- webapp\src\navigation\SignInForm.tsx
- webapp\src\contexts\auth.tsx
  ```
  import { User, onIdTokenChanged } from "firebase/auth"
  ```
  Note that many other nav components (Sidebard, etc), take firebase/auth/User as a prop.

`src\routes\AIRoute.tsx`:

- calls `useAuth` in `src\contexts\auth.tsx` to get the token from the `AuthContext`
  - creates an `AuthContext`
    - `firebase.auth.User`, token string, loading flag
  - creates an `AuthProvider` that
    - listens for `onIdTokenChange`and then calls `user.getIdToken`
    - refreshes token every 10 minues calling `user.getIdToken`
  - the `useAuth` function returns a 'full' `AuthContext`
- embeds the `src/components/chat/Chat` component and passes it the `userToken` from `useAuth()`

`src/components/chat/Chat.tsx`:

- calls `fetchQuery, createQuery, resumeQuery` from `utils\api.ts`

  - calls `src/utils\api.ts`:
    - The base URL to the NASA GENIE endpoint is stored in `VITE_PUBLIC_API_ENDPOINT` and is defined in:
      ```
      .env.demo
      .env.prod
      .env.dev
      ```
    - uses the base `endpoint` to build the full URL to individual GENIE endpoints (code example below). The users token is passed as a Bearer token in the header.

  ```
  export const fetchQuery =
    (token: string, queryId: string | null) => (): Promise<Query | undefined | null> => {
      if (!queryId) return Promise.resolve(null)
      const url = `${endpoint}/query/${queryId}`
      const headers = { Authorization: `Bearer ${token}` }
      return axios.get(url, { headers }).then(path(["data", "data"]))
    }
  ```

  There is also `src/utils\firebase.ts` that sets up firebase objects.

## Steps to add additional provider to the React UI

1. Add provider initialization to src/utils/firebase.ts

```
const microsoftProvider = new OAuthProvider('microsoft.com');
microsoftProvider.setCustomParameters({
    // Optional "tenant" parameter in case you are using an Azure AD tenant.
    // eg. '8eaef023-2b34-4da1-9baa-8bc8c9d6a490' or 'contoso.onmicrosoft.com'
    // or "common" for tenant-independent tokens.
    // The default value is "common".
    tenant: 'e2ccceae-06d8-4f6c-861a-d0292a5fe32a'
});
```

And make sure it is exported.

2. Update `src/utils/types.ts` to include the name of the new provider in `IAuthProvider` type.

3. Update `src/utils/Appconfig.ts` to include the name of the new provider in `authProviders` field.

4. Update `src/navigation/SignInForm.tsx`. Add code to render the new provider sign in and to submit it.

5. Add to AUTHORIZED_DOMAIN environment variable the new email domain.
