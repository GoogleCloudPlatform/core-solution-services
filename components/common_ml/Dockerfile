ARG COMMON_IMAGE
FROM ${COMMON_IMAGE}

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm -Rf /root/.cache/pip
