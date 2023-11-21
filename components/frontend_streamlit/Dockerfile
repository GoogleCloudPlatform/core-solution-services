ARG COMMON_IMAGE
FROM ${COMMON_IMAGE}

WORKDIR /opt
COPY requirements.txt service_requirements.txt

# add endline in case not there
RUN awk 1 requirements.txt > requirements.txt
RUN cat service_requirements.txt >> requirements.txt

RUN pip install -r requirements.txt

COPY src/ .

EXPOSE 80

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ENTRYPOINT [ "python", "main.py", "--prod=True" ]
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=80", "--server.address=0.0.0.0", "--server.baseUrlPath=/streamlit"]
