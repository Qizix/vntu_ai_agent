import asyncio
import json
import requests
import streamlit as st
import os

# Підключення до зовнішнього FAISS-індексу та моделі SentenceTransformer
from sentence_transformers import SentenceTransformer
import faiss


OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"  # Ендпоінт Ollama
FAISS_INDEX_PATH = "Data/processed/big/vector_index.faiss"
MODEL_PATH = "Data/processed/big/sentence_transformer_model"

os.environ["STREAMLIT_WATCH_FILE"] = "false"


# Завантаження моделі та FAISS індексу
@st.cache_resource
def load_resources():
    print("Loading model and index...")
    model = SentenceTransformer(MODEL_PATH)
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open("Data/processed/big_processed_results.json", "r", encoding="utf-8") as f:
        texts = json.load(f)
    return model, index, texts


model, index, texts = load_resources()


# *** Допоміжна функція: Запит до FAISS ***
def find_similar_texts(query, k=5):
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, k)
    # Повертаємо найближчі сусіди
    results = [{"text": texts[idx], "distance": float(distance)} for idx, distance in zip(indices[0], distances[0])]
    return results


# *** Допоміжна функція: Стрімінг відповідей від Ollama ***
async def call_ollama(prompt):
    data = {"model": "phi4", "prompt": prompt}
    with requests.post(OLLAMA_API_URL, json=data, stream=True) as response:
        if response.status_code == 200:
            for chunk in response.iter_lines(decode_unicode=True):
                if chunk:
                    try:
                        chunk_data = json.loads(chunk)
                        if "response" in chunk_data:
                            yield chunk_data["response"]
                    except json.JSONDecodeError:
                        continue
        else:
            yield f"Error: {response.status_code} {response.text}"


# *** Веб-інтерфейс на основі Streamlit ***
st.title("🎓 Дружній AI-помічник ВНТУ")

# Для збереження історії чату
if "messages" not in st.session_state:
    st.session_state.messages = []


# Основна функція пошуку
async def handle_user_input(user_input):
    # Додаємо повідомлення користувача
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Шукаємо релевантні відповіді у FAISS
    similar_texts = find_similar_texts(user_input)

    # Якщо текстів не знайдено
    if not similar_texts:
        st.session_state.messages.append({"role": "agent",
                                          "content": "На жаль, я поки що не можу знайти інформацію про це. Але можу спробувати допомогти іншим способом!"})
        return

    # Формуємо обмежений контекст для Ollama
    MAX_LENGTH = 5000  # Максимальна кількість символів для контексту
    context = "\n\n".join(
        [
            f"Context {i + 1}: {result['text']['processed_text'][:500]}"
            for i, result in enumerate(similar_texts)
        ][:5]  # Беремо максимум 5 релевантних частин
    )[:MAX_LENGTH]  # Обрізаємо контекст, якщо він перевищує максимально допустиму довжину

    friendly_prompt = (
        "Ти — дружній і доброзичливий віртуальний помічник Вінницького національного технічного університету (ВНТУ). "
        "Відповідай коротко і по суті, зосереджуючись лише на підтверджених даних. "
        "Не вигадуй деталей, якщо не маєш точної інформації. "
        "Використовуй наступний контекст для відповіді:\n\n"
        f"{context}\n\nЗапит: {user_input}\nВідповідь:"
    )

    # Ініціюємо стрімінг відповіді
    response_placeholder = st.empty()  # Вікно для виведення відповіді
    agent_response = []

    # Збір часткової відповіді
    MAX_AGENT_RESPONSE_LENGTH = 5000  # Максимальна довжина відповіді у символах
    async for partial_response in call_ollama(friendly_prompt):
        if len("".join(agent_response)) < MAX_AGENT_RESPONSE_LENGTH:
            agent_response.append(partial_response)
            response_placeholder.write("".join(agent_response))  # Поступове оновлення тексту

    # Записуємо остаточну відповідь в історію
    st.session_state.messages.append({"role": "agent", "content": "".join(agent_response)})


# Рендеринг чату
def render_chat():
    for message in st.session_state.messages:
        st.markdown(f"<div style='text-align: right; background: #0078d7; color: white; padding: 10px; "
                    f"border-radius: 5px; margin: 10px 5px;'>{message['content']}</div>", unsafe_allow_html=True)



# Виведення чату
render_chat()

# Поле для введення запиту
user_input = st.text_input("Введіть свій запит до помічника ВНТУ:")
if user_input:
    # Виконання обробки asynchronously
    asyncio.run(handle_user_input(user_input))

# Перерендер чату
render_chat()

