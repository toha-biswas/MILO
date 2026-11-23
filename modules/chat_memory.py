
import streamlit as st


def initialize_memory():
    """Initialize MILO's session memory."""

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "document_text" not in st.session_state:
        st.session_state.document_text = ""

    if "document_name" not in st.session_state:
        st.session_state.document_name = None

    if "chat_mode" not in st.session_state:
        st.session_state.chat_mode = "General Chat"


def add_message(role, content):
    """Save a conversation message."""

    st.session_state.messages.append({
        "role": role,
        "content": content
    })


def get_chat_history(limit=10):
    """Return recent conversation history."""

    return st.session_state.messages[-limit:]


def clear_chat():
    """Clear conversation history."""

    st.session_state.messages = []
