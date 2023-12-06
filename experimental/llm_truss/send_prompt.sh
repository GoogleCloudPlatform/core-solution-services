curl --location "http://${MODEL_IP}/v1/models/model:predict" \
--header "Content-Type: application/json" \
--data "{ \"prompt\": \"What is Medicaid?\", \"temperature\": 0.2, \"max_length\": 100, \"top_p\": 0.95,  \"top_k\": 40 }"

curl --location "http://${MODEL_IP}/v1/models/model:predict" \
--header "Content-Type: application/json" \
--data "{ \"prompt\": \"What is Medicare?\",
          \"temperature\": 0.2,
          \"max_length\": 100,
          \"top_p\": 0.95,
          \"top_k\": 40
}"
