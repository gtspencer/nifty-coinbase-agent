import requests

url = "http://127.0.0.1:5000/uppercase"

payload = {
    "text": "Can you post a tweet that says Buy Bonk?"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    print("Response from server:", response.json())
else:
    print(f"Request failed with status code {response.status_code}: {response.text}")
