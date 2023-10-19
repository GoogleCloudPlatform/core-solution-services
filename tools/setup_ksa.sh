# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

declare -a EnvVars=(
  "SKAFFOLD_NAMESPACE"
  "PROJECT_ID"
  "GSA_NAME"
  "KSA_NAME"
)

for variable in "${EnvVars[@]}"; do
  if [[ -z "${!variable}" ]]; then
    printf "$variable is not set.\n"
    exit 1
  fi
done

echo
echo "SKAFFOLD_NAMESPACE=${SKAFFOLD_NAMESPACE}"
echo "PROJECT_ID=${PROJECT_ID}"
echo "GSA_NAME=${GSA_NAME}"
echo "KSA_NAME=${KSA_NAME}"
echo

# create kubernetes service account if it doesn't exist
declare EXISTING_KSA=$(kubectl get sa -n ${SKAFFOLD_NAMESPACE} | egrep -i "^${KSA_NAME} ")
printf "\nCreating kubernetes service account on the cluster ...\n"
if [[ "$EXISTING_KSA" = "" ]]; then
  kubectl create serviceaccount -n ${SKAFFOLD_NAMESPACE} "${KSA_NAME}"
fi

#declare KSA_KEY="$KSA_NAME-sa-key"
#printf "\nAdding Service Account key '$KSA_KEY' to cluster:\n"
#
# add service account key
#declare EXISTING_SECRET=`kubectl get secrets -n $SKAFFOLD_NAMESPACE | grep "$KSA_NAME-sa-key"`
#if [[ "$EXISTING_SECRET" != "" ]]; then
#  printf "... Removing previous created secret '$KSA_NAME-sa-key' in namespace $SKAFFOLD_NAMESPACE.\n"
#  kubectl delete secret $KSA_KEY -n $SKAFFOLD_NAMESPACE
#fi
#
#printf "\n... Retrieving latest '$KSA_KEY' from Secret Manager\n"
#mkdir -p .tmp
#gcloud secrets versions access latest --secret "$KSA_KEY" > ./.tmp/$PROJECT_ID-$KSA_KEY.json
#
#printf "\n... Adding Service Account key as '$KSA_KEY' to cluster, namespace=$SKAFFOLD_NAMESPACE\n"
#kubectl create secret generic $KSA_KEY --from-file=./.tmp/${PROJECT_ID}-$KSA_KEY.json --namespace=$SKAFFOLD_NAMESPACE
#
#printf "\n\Service Account key added as '$KSA_KEY' in cluster, namespace=$SKAFFOLD_NAMESPACE\n"
#printf "Please make sure the key content is greater than 0 byte:\n"
#kubectl describe secrets $KSA_KEY -n $SKAFFOLD_NAMESPACE | grep bytes
#
#rm ./.tmp/$PROJECT_ID-$KSA_KEY.json

# bind KSA service account to GCP service account
printf "\nAdding Service Account IAM policy ...\n"
gcloud iam service-accounts add-iam-policy-binding \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${PROJECT_ID}.svc.id.goog[${SKAFFOLD_NAMESPACE}/${KSA_NAME}]" \
  ${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

printf "\nConnecting ksa with Service Account ...\n"
kubectl annotate serviceaccount \
  --overwrite \
  --namespace ${SKAFFOLD_NAMESPACE} \
  ${KSA_NAME} \
  iam.gke.io/gcp-service-account=${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
