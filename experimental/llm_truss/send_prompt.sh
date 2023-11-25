curl --location "http://${MODEL_IP}:8080/v1/models/model:predict" \
--header 'Content-Type: application/json' \
--data '{
    "prompt": "Whats is Medicaid?",
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40,
}'