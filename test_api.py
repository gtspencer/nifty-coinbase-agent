import requests

url = "http://127.0.0.1:5000/uppercase"

# Define the payload with the text to convert to uppercase
payload = {
    "text": "can you request some funds from a faucet?"
}

# Set the headers to indicate the content type is JSON
headers = {
    "Content-Type": "application/json"
}

# Send the POST request
response = requests.post(url, json=payload, headers=headers)

# Print the response from the server
if response.status_code == 200:
    print("Response from server:", response.json())
else:
    print(f"Request failed with status code {response.status_code}: {response.text}")
