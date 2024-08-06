# Deploying Gemma 2B
Reference: https://cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm

## Pre-Requisites
Kubernetes cluster with L4 GPUs nodepool
```shell
export CLUSTER_NAME="main-cluster"
export REGION="us-central1"
gcloud container node-pools create gpu-node-pool \
  --accelerator type=nvidia-l4,count=2,gpu-driver-version=latest \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --node-locations=${REGION}-a \
  --cluster=${CLUSTER_NAME} \
  --service-account gke-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --machine-type=g2-standard-24 \
  --disk-type pd-balanced \
  --disk-size 100 \
  --num-nodes=1
gcloud container node-pools list --region=${REGION} --cluster=${CLUSTER_NAME}
```


## HuggingFace API Token
```shell
export HF_TOKEN=...
```
Create secret:
```shell
kubectl create secret generic hf-secret \
  --from-literal=hf_api_token=$HF_TOKEN \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl describe secret hf-secret
```


## Deployment
Deploy Gemma 2B LLM using `kubectl`
```shell
kubectl apply -f vllm-gemma-2b-it.yaml
```
