import streamlit as st
import requests

# URL вашого агент
AGENT_API_URL = "http://127.0.0.1:8000/agent"

st.title("🤖 AI Chat Interface")

# Додатковістилі
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


# Функція для рендерингу чату
def render_chat():
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='message'>{message['content']}</div>", unsafe_allow_html=True)


# Рендер чату
render_chat()

# Поле для вводу користувача
user_input = st.text_input("Введіть своє повідомлення:")

# Якщо є вхід від користувача
if user_input:
    # Додавання повідомлення користувача до сесії
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Порожній контейнер для стрімінгової відповіді
    placeholder = st.empty()

    # Надсилаємо запит до агента
    try:
        with requests.post(AGENT_API_URL, json={"query": user_input, "num_results": 5}, stream=True) as response:
            if response.status_code == 200:
                agent_response = ""
                for chunk in response.iter_lines(decode_unicode=True):
                    if chunk:
                        # Декодуємо та додаємо наступну частину
                        agent_response += chunk
                        placeholder.markdown(f"<div class='message'>{agent_response}</div>", unsafe_allow_html=True)
            else:
                st.error(f"Помилка агента: {response.status_code} {response.text}")
    except Exception as e:
        st.error(f"Помилка зв'язку з агентом: {e}")

    # Додаємо фінальну відповідь до чату
    st.session_state.messages.append({"role": "agent", "content": agent_response})

    # Оновлюємо чат
    render_chat()
