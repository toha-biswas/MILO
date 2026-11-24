
import streamlit as st


def initialize_memory():
    defaults = {
        "messages": [],
        "document_text": "",
        "document_name": None,
        "chat_mode": "General Chat",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_message(role, content):
    st.session_state.messages.append({
        "role": role,
        "content": content,
    })


def get_chat_history(limit=10):
    return st.session_state.messages[-limit:]


def clear_chat():
    st.session_state.messages = []
