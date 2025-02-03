import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
from pydantic import BaseModel
import requests  # Для запитів до Ollama API

# Ініціалізація FastAPI
app = FastAPI()

# Завантаження необхідних компонентів
print("Loading model, FAISS index, and texts...")

# Завантаження SentenceTransformer моделі
model = SentenceTransformer("Data/processed/sentence_transformer_model")  # Ваша модель векторайзера
print("Model loaded.")

# Завантаження FAISS-індексу
index = faiss.read_index("Data/processed/vector_index.faiss")
print("FAISS index loaded.")

# Завантаження даних текстів
with open("Data/processed/processed_results_fixed.json", "r", encoding="utf-8") as file:
    texts = json.load(file)
print("Texts loaded.")

# Налаштування API Ollama
OLLAMA_API_URL = "http://127.0.0.1:11435/api/chat"  # Локальний ендпоінт Ollama API


# Допоміжна функція: Знаходження схожих текстів
def find_similar_texts(query: str, k: int = 5):
    # Генерація ембеддингу для запиту
    query_embedding = model.encode([query])

    # Пошук найближчих сусідів у FAISS
    distances, indices = index.search(query_embedding, k)

    # Формування результатів
    results = [{"text": texts[idx], "distance": float(distance)} for idx, distance in zip(indices[0], distances[0])]
    return results


# Допоміжна функція: Запит до Ollama
def query_ollama(model_name: str, prompt: str):
    # Data structure for the request
    data = {
        "model": model_name,  # Model name used by Ollama
        "message": prompt
    }

    # Query Ollama API
    response = requests.post(OLLAMA_API_URL, json=data)

    # Verify and process the response
    if response.status_code == 200:
        try:
            json_response = response.json()

            # Check if the 'message' field and 'content' exist in the response
            if "message" in json_response and "content" in json_response["message"]:
                return json_response["message"]["content"]
            else:
                raise KeyError(
                    f"'content' key not found in API response under 'message': {json_response}"
                )
        except json.JSONDecodeError:
            raise Exception(
                f"Failed to decode JSON response from Ollama API: {response.text}"
            )
    else:
        # Raise an informative error if the API response status is not 200
        raise Exception(f"Ollama API error: {response.status_code}, {response.text}")


# FastAPI маршрут: Запит до агента
class QueryRequest(BaseModel):
    query: str
    num_results: int = 5  # Кількість результатів FAISS


@app.post("/agent")
def agent_endpoint(request: QueryRequest):
    # Крок 1: Пошук схожих текстів у FAISS
    similar_texts = find_similar_texts(request.query, request.num_results)

    # Крок 2: Формування інструкції для Ollama
    context = "\n\n".join([f"Context {i + 1}: {result['text']}" for i, result in enumerate(similar_texts)])
    prompt = f"Use the following context to answer the query:\n\n{context}\n\nQuery: {request.query}\nAnswer:"

    # Крок 3: Звернення до Ollama через API
    response = query_ollama("phi4", prompt)  # Заміни "your-model-name" на назву моделі в Ollama

    # Крок 4: Формування результату для користувача
    return {
        "query": request.query,
        "response": response,
        "context": similar_texts
    }
