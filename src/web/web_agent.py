import streamlit as st
import requests

# URL вашого агента
AGENT_API_URL = "http://127.0.0.1:8000/agent"

# Назва заголовка сторінки
st.title("🤖 AI Chat Interface")

# Додаткові стилі
st.markdown("""
   <style>
   .message {
       background-color: #f1f1f1;
       border-radius: 5px;
       padding: 10px;
       margin: 10px 0;
   }
   .user-message {
       background-color: #0078D7;
       color: white;
       border-radius: 5px;
       padding: 10px;
       text-align: right;
       margin: 10px 0;
   }
   </style>
   """, unsafe_allow_html=True)

# Ініціалізуємо сесію для збереження повідомлень
if "messages" not in st.session_state:
    st.session_state.messages = []


# Функція для відображення чату
def render_chat():
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='message'>{message['content']}</div>", unsafe_allow_html=True)


# Рендер історії чату
render_chat()

# Поле для вводу від користувача
placeholder = st.empty()  # Використовуємо порожній контейнер для динамічного поля вводу
user_input = placeholder.text_input("Введіть своє повідомлення:")

# Якщо є текст від користувача
if user_input:
    # Додаємо повідомлення користувача
    st.session_state.messages.append({"role": "user", "content": user_input})
    placeholder.empty()  # Очищаємо поле вводу

    # Відправляємо запит до агента
    try:
        response = requests.post(AGENT_API_URL, json={"query": user_input, "num_results": 5})
        if response.status_code == 200:
            data = response.json()
            # Перевіряємо чи агент повернув помилку або відповідь
            if "error" in data and data["error"]:
                agent_response = f"Помилка агента: {data['message']}"
            else:
                agent_response = data.get("response", "Немає відповіді від агента.")
        else:
            agent_response = f"Помилка: {response.status_code} {response.text}"
    except Exception as e:
        agent_response = f"Помилка під час звернення до API: {e}"

    # Додаємо відповідь агента
    st.session_state.messages.append({"role": "agent", "content": agent_response})

    # Перерендер чату — функція викликається автоматично
    render_chat()