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

The `common.utils.auth_service.validate_token` method makes a call to the authentication service `validate_token` endpoint defined in `components/authentication/src/routes/validate_token.py`. The validate_token method will throw an `InvalidTokenError` if the authentication API call returns a response indicating the token is invalid. 

See `components/authentication/src/services/validation_service.py` which is the internal service module the Authentication service uses to perform token validation.  The `validate_token` method in this module looks for the token in cache via Redis, if the Redis cache is present in the platform.  If it finds the token in cache it returns back with a successful resopnse.  If the token is not present in cache it attempts to validate the token using a firebase library. This library is a proxy for GCP Identity Platform which validates the token according to the identity providers that are enabled for the project.

## How auth works in the React frontend


### How to add Microsoft sign-in to the React frontend


## How to generate an auth token



