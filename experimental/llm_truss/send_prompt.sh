curl --location "http://${MODEL_IP}:8080/v1/models/model:predict" \
--header 'Content-Type: application/json' \
--data '{ "prompt": "Whats is Medicaid?", "top_p": 0.95, "max_length": 100, "temperature": 0.9, "top_k": 40 }'
