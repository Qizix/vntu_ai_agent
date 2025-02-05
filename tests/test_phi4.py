import requests

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"  # Локальний ендпоінт Ollama API


def test_phi4(model_name="phi4", test_prompt="Скажи коротко на 10 слів що таке штучний інтелект?"):
    print(f"Testing model '{model_name}' with prompt: '{test_prompt}'")

    data = {
        "model": model_name,
        "prompt": test_prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Raw Response Text: {response.text}")

        if response.status_code == 200:
            try:
                json_response = response.json()
                print("Raw JSON response:", json_response)
                if "message" in json_response and "content" in json_response["message"]:
                    result_content = json_response["message"]["content"]
                    if result_content.strip():
                        print("\nResponse from phi 4:")
                        print(result_content)
                        return
                print("No valid content found in response.")
            except Exception as e:
                print(f"Failed to parse response JSON. Error: {e}")
        else:
            print(f"Ollama API returned error. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.ConnectionError:
        print("Error: Unable to connect to Ollama API. Ensure it's running.")
    except Exception as e:
        print(f"Unexpected error: {e}")



if __name__ == "__main__":
    # Тест 1: Запит зі звичайним текстом
    test_phi4(test_prompt="Скажи коротко на 10 слів що таке штучний інтелект?")
