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
export CLUSTER_ID=${PROJECT_ID}-db
export CPU_COUNT=2
export NODE_COUNT=1
export REGION="us-central1"
export PASSWORD="$(gcloud secrets versions access latest --secret=${POSTGRES_USER_PASSWD})"
export NETWORK="default-vpc"

gcloud services enable alloydb.googleapis.com
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

# Create AlloyDB cluster
gcloud alloydb clusters create ${CLUSTER_ID} \
    --region=${REGION} \
    --password=${PASSWORD} \
    --project=${PROJECT_ID} \
    --network=${NETWORK}
gcloud alloydb clusters list

# Create AlloyDB instance
gcloud alloydb instances create ${INSTANCE_ID} \
    --instance-type=PRIMARY \
    --cpu-count=${CPU_COUNT} \
    --read-pool-node-count=${NODE_COUNT} \
    --region=${REGION} \
    --cluster=${CLUSTER_ID}
gcloud alloydb instances list

# Get the IP address for database host
export PG_HOST=$(gcloud alloydb instances describe ${INSTANCE_ID} \
 --cluster ${CLUSTER_ID} --region ${REGION} --format="value(ipAddress)")
echo "AlloyDB Host IP address is ${PG_HOST}"
