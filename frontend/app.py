import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

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


# Chat interface
st.title("FlexOne")

# Chat
st.subheader(st.session_state.current_app)

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
        r = requests.post(f"{BACKEND_URL}/chat", json={"message": prompt})
        r.raise_for_status()
        bot_reply = r.json().get("reply", "No reply from backend.")
    except Exception as e:
        bot_reply = f"Error: {e}"

    # Add bot message
    st.session_state.messages.append(
        {"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant", avatar="logo.svg"):
        st.markdown(bot_reply)
