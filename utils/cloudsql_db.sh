#!/bin/bash
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

if [ -z "${PROJECT_ID}" ]; then
    echo "ERROR: PROJECT_ID is not set"
    exit 1;
fi

export POSTGRES_USER_PASSWD="postgres-user-passwd"
if [ $(gcloud secrets list | grep -c "${POSTGRES_USER_PASSWD}") == 0 ]; then
    echo "ERROR: Secret ${POSTGRES_USER_PASSWD} not found"
    exit 1;
fi

export INSTANCE_ID=${PROJECT_ID}-db
export REGION="us-central1"
export PASSWORD="$(gcloud secrets versions access latest --secret=${POSTGRES_USER_PASSWD})"
export NETWORK="default-vpc"

if [ $(gcloud compute networks list | grep -c ${NETWORK}) == 0 ]; then
    echo "ERROR: Network ${NETWORK} not found"
    exit 1;
fi

gcloud services enable sqladmin.googleapis.com
gcloud services enable servicenetworking.googleapis.com

# Reserve an IP block for VPC-peering
gcloud compute addresses create vpc-peering-ip-${NETWORK} \
    --global \
    --purpose=VPC_PEERING \
    --prefix-length=16 \
    --network=${NETWORK}

# Create VPC Peering
gcloud services vpc-peerings connect \
    --service=servicenetworking.googleapis.com \
    --ranges=vpc-peering-ip-${NETWORK} \
    --network=${NETWORK}
gcloud compute networks peerings list

# Create PostgreSQL Instance
gcloud sql instances create ${INSTANCE_ID} \
    --database-version=POSTGRES_15 \
    --region=us-central1 \
    --tier=db-perf-optimized-N-2 \
    --edition=ENTERPRISE_PLUS \
    --enable-data-cache \
    --storage-size=250 \
    --network=${NETWORK} \
    --enable-google-private-path \
    --availability-type=REGIONAL \
    --no-assign-ip
gcloud sql users set-password postgres --instance=${INSTANCE_ID} --password=${PASSWORD}

gcloud sql instances list

# Get the IP address for database host
export PG_HOST=$(gcloud sql instances describe ${INSTANCE_ID} \
    --format="value(ipAddresses.ipAddress)")
echo "Cloud SQL Host IP address is ${PG_HOST}"
