import requests
import os
import argparse
import time


parser = argparse.ArgumentParser()
parser.add_argument("prompt", type=str)
parser.add_argument("--model_ip", type=str, help="Model endpoint ip")
parser.add_argument("--max_length", type=str, help="Maximum request length")
parser.add_argument("--temperature", type=str, help="Temperature")
parser.add_argument("--top_p", type=str, help="Token selection Top-P sampling")
parser.add_argument("--top_k", type=str, help="Token selection Top-K sampling")
args = parser.parse_args()


# Temperature controls the degree of randomness in token selection.
# Token limit determines the maximum amount of text output.
# Tokens are selected from most probable to least until the sum of
#  their probabilities equals the top_p value.
# top_k of 1 means the selected token is the most probable among all tokens.

if args.model_ip:
    MODEL_IP = args.model_ip
else:
    MODEL_IP = os.getenv("MODEL_IP")

assert MODEL_IP, "MODEL_IP is not set, should be set either " \
                 "via environment variable `MODEL_IP` or " \
                 "via --model-ip input parameter."

data = {
    "prompt": args.prompt,
    "temperature": float(args.temperature) if args.temperature else 0.2,
    "top_p": float(args.top_p) if args.top_p else 0.95,
    "top_k": int(args.top_k) if args.top_k else 40,
}

if args.max_length:
    data.update({"max_length": int(args.max_length)})

MODEL_ENDPOINT = f"http://{MODEL_IP}:8080/v1/models/model:predict"
print(f"Using model endpoint {MODEL_ENDPOINT} with data: {data}")

start_time = time.time()
res = requests.post(MODEL_ENDPOINT, json=data)
process_time = round(time.time() - start_time)
print(res.json())
print(f"Received response in {process_time} seconds.")


