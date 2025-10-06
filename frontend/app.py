import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"
st.set_page_config(page_title="FlexOne", page_icon="logo.svg")

# Sidebar
st.sidebar.image("logo.svg", width=40)

st.sidebar.header("Applications")

# Track current application
if "current_app" not in st.session_state:
    st.session_state.current_app = "Consumer Edge"

if st.sidebar.button("Consumer Edge"):
    st.session_state.current_app = "Consumer Edge"
    # r = requests.get(f"{BACKEND_URL}/")
    # st.sidebar.json(r.json())

# if st.sidebar.button("Speciphic Ask (/)"):
#    st.session_state.current_app = "Speciphic Ask"

#if st.sidebar.button("New chat"):
#    st.session_state.messages = []

# Chat interface
st.title("FlexOne")

# Chat
st.subheader(st.session_state.current_app)

def send_chat(messages):
    """
    Send a list of chat messages to the backend `/chat/details` endpoint.

    Params:
        messages (list[dict[str, str]]): Chat history with "role" and "content".
            Example:
                [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"},
                    {"role": "assistant", "content": "Hi there! How can I help?"},
                    {"role": "user", "content": "Tell me a joke."}
                ]
    Returns:
        str: Assistant's reply text from the backend.
            Example:
                "Why don't scientists trust atoms? Because they make up everything!"
    """ 
    payload = {"messages": messages}
    r = requests.post(f"{BACKEND_URL}/chat/details", json=payload, timeout=60)
    r.raise_for_status()
    return r.json().get("response", "")

# chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="user.svg"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="logo.svg"):
            st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask me here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="user.svg"):
        st.markdown(prompt)

    # Send to backend
    try:
        bot_reply = send_chat(st.session_state.messages)
    except Exception as e:
        bot_reply = f"Error contacting backend: {e}"

    # Add bot message
    st.session_state.messages.append(
        {"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant", avatar="logo.svg"):
        st.markdown(bot_reply)