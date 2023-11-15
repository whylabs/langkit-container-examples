import requests
import sys
import os

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
model_id = sys.argv[1]
prompt = sys.argv[2]

resp = requests.post(
    url="http://localhost:8000/v1/chat/completions",
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "whylabs_dataset_id": f"{model_id}",
        "X-API-Key": "password"
    },
    json={
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ],
})

print(resp.json())
