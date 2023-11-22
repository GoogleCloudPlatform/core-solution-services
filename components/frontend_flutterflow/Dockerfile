# Stage 1
FROM debian:latest AS build-env

ARG FLUTTER_VERSION=3.16.0

RUN apt-get update
RUN apt-get install -y curl git wget unzip libgconf-2-4 gdb libstdc++6 libglu1-mesa fonts-droid-fallback lib32stdc++6 python3
RUN apt-get clean

RUN git clone -b ${FLUTTER_VERSION} https://github.com/flutter/flutter.git /usr/local/flutter

ENV PATH="/usr/local/flutter/bin:/usr/local/flutter/bin/cache/dart-sdk/bin:${PATH}"

RUN flutter doctor -v
RUN flutter config --enable-web

RUN mkdir /app/
COPY src/ /app/

WORKDIR /app/
RUN flutter build web

RUN ls -l /app/build/web
RUN cat /app/build/web/assets/.env


# Stage 2
FROM nginx:1.21.1-alpine
COPY --from=build-env /app/build/web /usr/share/nginx/html
