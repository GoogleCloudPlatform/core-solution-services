# Google CLP AI v2

A new Flutter project.

## Getting Started (Docker)

> Note: this Dockerfile will not work on Mac M1/M2 machines
> because of this [qemu bug](https://github.com/docker/for-mac/issues/5123)

To build the docker container for this FlutterFlow application, run

```bash
docker build --platform linux/amd64 -t edai-web .
```

To run the docker container, use

```bash
docker run --rm -p 8080:80 --name edai edai-web
```

## Getting Started (Manual)

1. [Install Flutter](https://docs.flutter.dev/get-started/install)
    - This FlutterFlow application supports Flutter version 3.10.4

1. Build web assets

```bash
flutter config --enable-web
flutter build web
```

1. Create a Dockerfile in the project root directory

```
FROM nginx:1.21.1-alpine
COPY ./build/web /usr/share/nginx/html
```

1. Build docker image and run docker container

```
docker build --platform linux/amd64 -t [tag] .
docker run --rm -p 8080:80 --name edai [tag]
```
## Cloud Run Deployment

```bash
export IMAGE_TAG=<IMAGE_TAG>
export REGION=us-central1

gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_TAG \
  --execution-environment=gen2 \
  --platform managed \
  --region $REGION \
  --port 80
```
