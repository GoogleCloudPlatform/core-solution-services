ARG COMMON_ML_IMAGE
FROM ${COMMON_ML_IMAGE}

WORKDIR /opt
COPY requirements.txt service_requirements.txt

# add endline in case not there
RUN awk 1 requirements.txt > requirements.txt
RUN cat service_requirements.txt >> requirements.txt
RUN pip install -r requirements.txt

# download spacy model
RUN python -m spacy download en_core_web_md

COPY src/ .

EXPOSE 8888

ENTRYPOINT [ "python", "main.py" ]
