# Frontend Streamlit app

## Development

### Run streamlit locally

Set up API endpoint

```
export API_BASE_URL=https://my.domain.com
```

Set the subpath where the streamlit will deploy to. By default, it sets to "/streamlit"

```
export APP_BASE_PATH="/streamlit"
```

Install virtualenv and dependencies
```
python -m virtualenv .venv
source .venv/bin/activate
pip install -r ../common/requirements.txt
pip install -r requirements.txt
```

```
PYTHONPATH=components/common/src streamlit run components/frontend_streamlit/src/main.py \
  --server.baseUrlPath=$APP_BASE_PATH
```

### Deploy and run at remote GKE cluster

Deploy the microservice with livereload.
- This will run `skaffold dev` behind the scene.

```
sb deploy -n $NAMESPACE -m frontend_streamlit --dev
```

Once deployed successfully, you will see the output like below:
```
Deployments stabilized in 32.744 seconds
Port forwarding service/frontend-streamlit in namespace <namespace>, remote port 80 -> http://127.0.0.1:8080
```

At this point, the frontend app is ready and accessible at http://127.0.0.1:8080.

### Deploy to remote GKE cluster

Deploy the microservice.
- This will run `skaffold run` behind the scene.

```
sb deploy -n $NAMESPACE -m frontend_streamlit
```
