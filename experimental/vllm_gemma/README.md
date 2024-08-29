# Deploying Gemma 2B

Reference: https://cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm

## Prerequisites

### Hugging Face API Token
* You will need API Token from Hugging Face to download the model.
```shell
export HF_TOKEN=...
```

### Cluster with Regional GPU nodepool

```shell
export PROJECT_ID=...
export CLUSTER_NAME="main-cluster"
export REGION="us-central1"

gcloud container clusters get-credentials ${CLUSTER_NAME} --location=${REGION}
```

### Create a Kubernetes secret for Hugging Face credentials
```shell
kubectl create secret generic hf-secret \
  --from-literal=hf_api_token=$HF_TOKEN \
  --dry-run=client -o yaml | kubectl apply -f -
```
#### Create GPU node pool
```shell
gcloud container node-pools create gpu-node-pool \
  --accelerator type=nvidia-l4,count=2,gpu-driver-version=latest \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --node-locations=${REGION}-a \
  --cluster=${CLUSTER_NAME} \
  --machine-type=g2-standard-24 \
  --disk-type pd-balanced \
  --disk-size 100 \
  --num-nodes=1
```

## Deployment
Deploy Gemma 2B LLM using `kubectl`
```shell
kubectl apply -f vllm-gemma-2b-it.yaml
```
