# Authentication in CSS

This document describes the authentication scheme used in the CSS platform (and GENIE, which is based on the platform).  It also describes how to add an identity provider, using SAML as an example.

## The identity platform

By default we use [Google Cloud Identity Platform (IDP)](https://cloud.google.com/security/products/identity-platform?hl=en) as the identity provider for GENIE and CSS.  We use firebase libraries to validate identity tokens in the authentication service.  Firebase is a proxy for GCP Identity Plaform - we just use firebase because the libraries are convenient. 

GCP IDP allows for adding and configuring identity providers like Microsoft or SAML.  Please consult [the docs for Identity Platform](https://cloud.google.com/identity-platform/docs/) for details on adding identity providers.  It is easy to add Microsoft identity to the GENIE backend - you add that provider via Identity Platform.  There are additional changes necessary to the frontend code that is calling GENIE APIs to enable a user to sign in via your chosen provider (for example) Microsoft.  We include details below on how to update the React frontend for Microsoft identity.

It is possible to implement an alternative identity platform (for example Federal CAC).  This would require adding support in the authentication service for this provider.

## How auth works in the platform

All API calls to CSS microservices require an authentication token to be passed as an HTTP Bearer token.  This token is validated for every call, via the authentication service.  Every microservice in CSS includes this directive in the main.py for that service. For example, in `components/llm_service/src/main.py`:

```
from common.utils.auth_service import validate_token

...

api = FastAPI(
    title=service_title,
    version="latest",
    # docs_url=None,
    # redoc_url=None,
    dependencies=[Depends(validate_token)]
    )
```

This code tells FastAPI that every call to the api defined in this service depends on a call to the method `common.utils.auth_service.validate_token`.  See FastAPI docs on dependencies for details on the dependencies feature in FastAPI:  [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/#share-annotated-dependencies).

The `common.utils.auth_service.validate_token` method makes a call to the authentication service `validate_token` endpoint defined in `components/authentication/src/routes/validate_token.py`. The `validate_token` method will throw an `InvalidTokenError` if the authentication API call returns a response indicating the token is invalid. 

See `components/authentication/src/services/validation_service.py` which is the internal service module the Authentication service uses to perform token validation.  The `validate_token` method in this module looks for the token in cache via Redis, if the Redis cache is present in the platform.  If it finds the token in cache it returns back with a successful resopnse.  If the token is not present in cache it attempts to validate the token using a firebase library. This library is a proxy for GCP Identity Platform which validates the token according to the identity providers that are enabled for the project.

## How auth works in the React frontend
The React frontend uses firebase to perform authentication.  We use the Firebase [typescript libraries](https://firebase.google.com/docs/auth/web/start) that allow a React app to manage authentication and use a Google sign-in popup to log the user in, if the app is using Google authentication.  The app also supports email/password authentication.

The React frontend creates a [React Context](https://react.dev/learn/passing-data-deeply-with-context#context-an-alternative-to-passing-props) that contains the current signed-in user, the identity token associated with that signin, and a global "loading" variable that indicates the frontend is loading something from the backend.  This context is defined in `components/frontend_react/webapp/src/contexts/auth.tsx`.  The context is available to the entire app codebase, as defined in the main module for the app: see `components/frontend_react/webapp/src/main.tsx`.  This allows any module in the code to access the current identity token, which must be passed to any backend API call (defined in `components/frontend_react/webapp/src/utils/api.ts`).  

For example in the AIRoute module (`components/frontend_react/webapp/src/routes/AIRoute.tsx`) which provides the React route for both Chat and Query pages, the auth token is retrieved from the auth context and passed to the components that render Chat and Query pages:

```
import { useAuth } from "@/contexts/auth"
import { useQueryParams } from "@/utils/routing"

export const AIChatRoute = () => {
  const params = useQueryParams()
  const { token } = useAuth()

  if (!token) return <></>

  return <GenAIChat userToken={token} initialChatId={params.get("chat_id")} />
}

export const AIQueryRoute = () => {
  const params = useQueryParams()
  const { token } = useAuth()

  if (!token) return <></>

  return <GenAIQuery userToken={token} initialQueryId={params.get("query_id")} />
}
```
As you can see in the code, if the user is not signed in, the Chat and Query pages will not be active and instead will render as blank.

The line `const { token } = useAuth()` retrieves the current token (one of the three global context variables defined in that context) from the Auth context, by calling the `useAuth` access method defined in the auth context module.

The signin code itself is lives in `components/frontend_react/webapp/src/navigation/SigninForm.tsx`.  Depending on the identity providers configured in `components/frontend_react/webapp/src/utils/AppConfig.ts` the signin module will display different popups to enable the user to sign in.


### Configuring auth providers in the React frontend

The frontend currently supports Google, Email/Password, and Microsoft as identity providers.  See the [README for the React frontend](../components/frontend_react/README.md) for info on configuring auth providers in the React frontend.  


## How to generate an auth token

You can generate an identity token (for example, for testing the APIs) using the gcloud CLI:

```
gcloud auth print-access-token
```

For example, to call the LLM Service to build a query engine from the command line:

```
BASE_URL=https://your.domain.com
ID_TOKEN=$(gcloud auth print-access-token)
QUERY_ENGINE_NAME="qe1"

curl --location "$BASE_URL/llm-service/api/v1/query/engine" \
--header "Content-Type: application/json" \
--header "Authorization: Bearer $ID_TOKEN" \
--data "{
    \"doc_url\": \"gs://$PROJECT_ID-llm-docs\",
    \"query_engine\": \"$QUERY_ENGINE_NAME\",
    \"description\": "test"
}"

```
