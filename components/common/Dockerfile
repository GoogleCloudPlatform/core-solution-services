FROM python:3.9-slim
WORKDIR /opt

RUN apt-get update && apt-get -y upgrade && \
    apt-get -y install gcc vim && \
    apt-get autoremove -yqq --purge && apt-get clean

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm -Rf /root/.cache/pip

COPY src/ .
