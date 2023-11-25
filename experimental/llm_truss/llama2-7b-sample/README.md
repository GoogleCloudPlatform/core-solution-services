<!-- TOC -->
* [Deploying Llama2 7B Into GCP](#deploying-llama2-7b-into-gcp)
  * [Prerequisites](#prerequisites)
    * [Hugging Face API Token](#hugging-face-api-token)
    * [GPU cluster with nvidia Drivers](#gpu-cluster-with-nvidia-drivers)
      * [Create GPU cluster (if does not exist)](#create-gpu-cluster--if-does-not-exist-)
      * [Connect to the cluster](#connect-to-the-cluster)
  * [Create Truss Foundation](#create-truss-foundation)
  * [Build and Deploy Llama2](#build-and-deploy-llama2)
  * [Using Model Predictions](#using-model-predictions)
<!-- TOC -->
# Deploying Llama2 7B Into GCP

## Prerequisites

### Hugging Face API Token
* You will need API Token from Hugging Face to download the model.
* Also you will need to have  [requested access](https://ai.meta.com/resources/models-and-libraries/llama-downloads) from Meta. 
* And access from [HuggingFace](https://huggingface.co/meta-llama/Llama-2-7b) so that you can download the model through HF.

```shell
export HUGGINGFACE_API_KEY=...
```

Create secret:
```shell
gcloud secrets create "huggingface-api-key" --project $PROJECT_ID
echo $HUGGINGFACE_API_KEY | gcloud secrets versions add "huggingface-api-key" --data-file=-
```

TODO:
* Currently secret is not being used, since deployment needs a service account with access to the secret manager (it is being passed as an environment variable to ConfigMap).
  This part shall be added later during the integration with the main project

### GPU cluster with nvidia Drivers
You will need a GPU cluster with nvidia drivers installed.

#### Create GPU cluster (if does not exist)
Create GPU GKE Cluster:
* In the default-pool >
  * Enable cluster autoscaler
* In the Nodes tab:
  * Change Machine Configuration from General Purpose to GPU
    * GPU type: Nvidia TF
    * Number of GPUs: 1
    * Enable GPU time sharing
    * Max shared clients per GPU: 8
  * GPU Driver installation
    - Google-managed (latest)    
  * Machine type: n1-standard-4
  * Boot disk size: 100 GB


Following Org Policy needs to be disabled: (need to have `orgpolicy.policies.create` permission):
```shell
gloud org-policies reset constraints/compute.vmExternalIpAccess --project $PROJECT_ID
```

gcloud command line:

```shell
export PROJECT_ID=...
export CLUSTER_NAME=...
export REGION="us-central1"
export ZONE="us-central1-c"
```

```shell
gcloud beta container --project "$PROJECT_ID" clusters create "$CLUSTER_NAME" \
  --no-enable-basic-auth --cluster-version "1.27.3-gke.100" --release-channel "regular" \
  --machine-type "n1-standard-4" \
  --accelerator "type=nvidia-tesla-t4,count=1,gpu-sharing-strategy=time-sharing,max-shared-clients-per-gpu=8" \
  --image-type "COS_CONTAINERD" --disk-type "pd-balanced" --disk-size "100" \
  --metadata disable-legacy-endpoints=true \
  --scopes "https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" \
  --num-nodes "3" --logging=SYSTEM,WORKLOAD --monitoring=SYSTEM --enable-ip-alias \
  --network "projects/$PROJECT_ID/global/networks/jump-vpc" \
  --subnetwork "projects/$PROJECT_ID/regions/$REGION/subnetworks/jump-vpc-subnet" \
  --no-enable-intra-node-visibility --default-max-pods-per-node "110" \
  --security-posture=standard --workload-vulnerability-scanning=disabled \
  --no-enable-master-authorized-networks \
  --addons HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver \
  --enable-autoupgrade --enable-autorepair --max-surge-upgrade 1 \
  --max-unavailable-upgrade 0 --binauthz-evaluation-mode=DISABLED \
  --enable-managed-prometheus --enable-shielded-nodes --node-locations "$ZONE"
```

#### Connect to the cluster

```shell
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION --project $PROJECT_ID
```

## Create Truss Foundation

```shell
cd experimental/llm_truss
```

1. Create a virtual environment and install truss:
```shell
python -m venv venv
source venv/bin/activate
```

Init Llama2 foundation:
```shell
pip install truss

export MODEL_NAME=llama2-7b
truss init $MODEL_NAME
```

When prompted model name, type in the model as you have set it up:
```text
? What's the name of your model? llama2-7b
```

2. Copy model.py and config.yaml

```shell
cp llama2-7b-sample/config.yaml $MODEL_NAME/
cp llama2-7b-sample/model/model.py $MODEL_NAME/model/model.py
```
3. Run main.py to generate the Docker file:

```shell
python llama2-7b-sample/main.py $MODEL_NAME
```

4. Fix requirements.txt
```shell
cp llama2-7b-sample/requirements.txt $MODEL_NAME/
```

5. Copy `yaml` files for deployment:

```shell
cp -r llama2-7b-sample/kustomize $MODEL_NAME/
cp llama2-7b-sample/skaffold.yaml $MODEL_NAME/
```


## Build and Deploy Llama2

Build and deploy into the default namespace:

```shell
cd $MODEL_NAME
skaffold run  --default-repo=gcr.io/${PROJECT_ID}
```

Build and deploy into the custom namespace:

```shell
kubectl create ns <namespace-name>
skaffold run  --default-repo=gcr.io/${PROJECT_ID} --namespace=<namespace-name>
```


Wait till pod becomes available and status is `Running`:

```shell
kubectl get pods
```

Grab the full name of the running pod, such as `llama2-7b-7f9c8888d5-rlxr4`

Make sure cuda is activated:

```shell
kubectl logs <pod-name> | grep cuda
```

Expected output:

```text
THE DEVICE INFERENCE IS RUNNING ON IS: cuda 
```

## Using Model Predictions

```shell
cd experimental/llm_truss
```

First you need to get IP address of the Prediction model:

```shell
export MODEL_IP=$(kubectl describe service/llama2-7b-service | grep 'LoadBalancer Ingress:' | awk '{print $3}')
echo MODEL_IP=$MODEL_IP
```

Now you can test prediction:

```shell
python main.py "What is Medicaid?" 
```

Sample Output:

```text
python main.py "What is Medicaid?"
Using model endpoint http://35.224.143.29:8080/v1/models/model:predict with data: {'prompt': 'What is Medicaid?', 'temperature': 0.2, 'top_p': 0.95, 'top_k': 40}
{'data': {'generated_text': 'What is Medicaid?\n\nMedicaid is a government program that provides health coverage to eligible individuals with low income and limited resources. It is a joint federal-state program, meaning that both the federal government and each individual state contribute funding to the program. Medicaid is designed to help ensure that certain groups of people, such as low-income children, pregnant women, and people with disabilities, have access to necessary medical care.\n\nWho is eligible for Medicaid?\n\nMedicaid eligibility varies by state, but generally, individuals who have'}}
Received response in 8 seconds.
```

Optionally overwrite parameters:

```shell
python main.py "what is medicaid?" --temp 1 --top_p 1 --top_k 10
```

Help:
```text
python main.py --help
usage: main.py [-h] [--model_ip MODEL_IP] [--temperature TEMPERATURE] [--top_p TOP_P] [--top_k TOP_K] prompt

positional arguments:
  prompt

optional arguments:
  -h, --help            show this help message and exit
  --model_ip MODEL_IP   Model endpoint ip
  --temperature TEMPERATURE
                        Temperature
  --top_p TOP_P         Token selection Top-P sampling
  --top_k TOP_K         Token selection Top-K sampling
```
