# Frontend Streamlit app

## Development

### Run streamlit locally

Set up API endpoint

```
export API_BASE_URL=https://my.domain.com
```

Install virtualenv and dependencies
```
python -m virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r ../common/requirements.txt
```

```
PYTHONPATH=components/common/src streamlit run components/frontend_streamlit/src/main.py
```

### Deploy and run at remote GKE cluster

Deploy the microservice with livereload.
- This will run `skaffold dev` behind the scene.

```
sb deploy -n $NAMESPACE -m frontend_streamlit --dev
```

### Deploy to remote GKE cluster

Deploy the microservice.
- This will run `skaffold run` behind the scene.

```
sb deploy -n $NAMESPACE -m frontend_streamlit
```
