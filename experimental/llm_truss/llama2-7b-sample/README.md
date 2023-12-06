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

### Service Account and Workload Identity 

These instructions assume that you have service account `gke-sa` existing in the GCP project and that there is gke-sa Kubernetes service account (which is required and used within this project )

If you are using a different project without service account, make sure to:

* Create service account named `gke-sa`:  `gke-sa@$PROJECT_ID.iam.gserviceaccount.com`
  * Assign the following roles:
      * Secret Manager Admin
      * Kubernetes Engine Admin
      * Storage Admin
      * Workload Identity User
    
* Create Kubernetes Service Account (gke-sa)  and bind it to the GCP service account used for GKE:
  ```
  export PROJECT_ID=<your-dev-project-id>
  bash ./setup/setup_ksa.sh
  ```
    - This will create a service account in the GKE cluster.
    - It will also bind the GKE service account with the regular GCP service account named "gke-sa".
    - You can verify it on the GCP Console > Service Accounts > "gke-sa" service account > Permissions.


### GPU cluster with nvidia Drivers
You will need a GPU cluster with nvidia drivers installed.

#### Cluster with Regional GPU nodepool

Node pool details: 
* Name: explanatory name, such as `gpu-node-pool` 
* Size (Number of nodes): 1
* Enable cluster autoscaler - Checkbox on
  ** Location policy -> Balanced
  ** Total limits:
  * Minimum number of all nodes 1,
  * Maximum number of all nodes 3,
    ** Specify node locations - Checkbox on
    * us-central1-c

Nodes:
  * Change Machine Configuration from General Purpose to GPU
    * GPU type: Nvidia T4
    * Number of GPUs: 1
    * Enable GPU time sharing (*)
      * Max shared clients per GPU: 8
  * GPU Driver installation
    - Google-managed (latest)    
  * Machine type: n1-standard-4
  * Boot disk size: 100 GB

Security:
  * Specify service account: `gke-sa@$PROJECT_ID.iam.gserviceaccount.com`

(*) GPU sharing does not come up as an option, when adding new nodepool to the existing cluster, and is available for the new cluster creation onlu.


Following Org Policy needs to be disabled: (need to have `orgpolicy.policies.create` permission):
```shell
gloud org-policies reset constraints/compute.vmExternalIpAccess --project $PROJECT_ID
```

```shell
export PROJECT_ID=...
export CLUSTER_NAME=...
export REGION="us-central1"
```


#### Connect to the cluster

```shell
gcloud container clusters get-credentials main-cluster --region $REGION --project $PROJECT_ID
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

### Llama2 Configuration
Before the deployment you can tune llama2 prediction parameters and change the default values:  

* `DEFAULT_MAX_LENGTH` - max_length in the request payload (default is 256)
You can increase or decrease it by exporting value into the env variable:

```shell
export DEFAULT_MAX_LENGTH=1024
```

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

Note, it will take ~10 minutes for the pod to download the model. 

You can track the progress via logs
```shell
kubectl logs <pod-name> 
```

Wait till it gets to 100%:
```text
Downloading shards:  50%|█████     | 1/2 [01:03<01:03, 63.31s/it]1:03<00:00, 194MB/s]

```

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
kubectl port-forward service/truss-llama2-7b-service 28015:80 &
export MODEL_IP=localhost:28015
echo MODEL_IP=${MODEL_IP}
```

Now you can test prediction:

```shell
python main.py "What is Medicaid?" 
```

Sample Output:

```text
python main.py "What is Medicaid?"
Using model endpoint http://truss-llama2-7b-service/v1/models/model:predict with data: {'prompt': 'What is Medicaid?', 'temperature': 0.2, 'top_p': 0.95, 'top_k': 40}
{'data': {'generated_text': 'What is Medicaid?\n\nMedicaid is a government program that provides health coverage to eligible individuals with low income and limited resources. It is a joint federal-state program, meaning that both the federal government and each individual state contribute funding to the program. Medicaid is designed to help ensure that certain groups of people, such as low-income children, pregnant women, and people with disabilities, have access to necessary medical care.\n\nWho is eligible for Medicaid?\n\nMedicaid eligibility varies by state, but generally, individuals who have'}}
Received response in 8 seconds.
```

Optionally overwrite parameters:

```shell
python main.py "what is medicaid?"  --max_length 100 --temperature 1 --top_p 0.9 --top_k 30
```

Help:
```text
python main.py --help
usage: main.py [-h] [--model_ip MODEL_IP] [--max_length MAX_LENGTH] [--temperature TEMP] [--top_p TOP_P] [--top_k TOP_K] prompt

positional arguments:
  prompt

optional arguments:
  -h, --help            show this help message and exit
  --model_ip MODEL_IP   Model endpoint ip
  --max_length MAX_LENGTH Maximum request length
  --temperature TEMP    Temperature
  --top_p TOP_P         Token selection Top-P sampling
  --top_k TOP_K         Token selection Top-K sampling
```
