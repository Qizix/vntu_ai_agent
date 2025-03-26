import requests

url = "http://127.0.0.1:8000/agent"
data = {
    "query": "як створити акаунт jetiq?",
    "num_results": 3
}

response = requests.post(url, json=data)

# Print the response from the age
if response.status_code == 200:
    print("Response:", response.json())
else:
    print("Error:", response.status_code, response.text)
