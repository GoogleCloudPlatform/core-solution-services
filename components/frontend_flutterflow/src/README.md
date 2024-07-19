# GENIE Flutterflow Frontend UI

A web application built with FlutterFlow (flutterflow.io).

## Development

### Build and deploy with livereload to a GKE cluster

Run the following to build and deploy the web app instance to a GKE cluster with
livereload and port forwarding.

```bash
skaffold dev -p default-deploy -m frontend_flutterflow -n $NAMESPACE
```

### Run Flutter web app locally (for local development)

- [Install Flutter](https://docs.flutter.dev/get-started/install)
  - This FlutterFlow application supports Flutter version 3.10.4

- Update `src/.env` file with the correct API_BASE_URL and PROJECT_ID:
  ```
  WEB_APP_TITLE="GenAI for Enterprise"
  API_BASE_URL="https://your-api-domain.com/"
  PROJECT_ID=your-project-id
  ```
- Run flutter web app locally:
  ```bash
  cd src
  flutter config --enable-web
  flutter run -d chrome
  ```

### Build web assets and run locally

- Update `src/.env` file with the correct API_BASE_URL and PROJECT_ID:
  ```
  WEB_APP_TITLE="GenAI for Enterprise"
  API_BASE_URL="https://your-api-domain.com/"
  PROJECT_ID=your-project-id
  ```

- Build web package and assets:
  ```bash
  flutter build web
  ```

- Run and serve the web UI with a web server like `http-server`:
  - https://www.npmjs.com/package/http-server

  ```bash
  http-server build/
  ```

## Deployment

To build and deploy the Flutter web app to a GKE cluster:

```bash
skaffold run -p default-deploy -m frontend_flutterflow -n $NAMESPACE
```
