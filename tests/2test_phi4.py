import requests

url = "http://127.0.0.1:11434/api/generate"
data = {"model": "phi4",
        "prompt": "Скажи коротко на 10 слів що таке штучний інтелект?",
        "stream": False}

response = requests.post(url, json=data)
print(response.json())
