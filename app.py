
import streamlit as st

from modules.ai_engine import get_ai_response
from modules.chat_memory import (
    initialize_memory,
    add_message,
    get_chat_history,
    clear_chat,
)
from modules.document_chat import (
    extract_document_text,
    create_document_prompt,
)
from modules.general_chat import get_general_response


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="MILO AI Assistant",
    page_icon="🤖",
    layout="wide",
)

initialize_memory()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("🤖 MILO")
    st.caption("Your AI assistant")

    st.divider()

    mode = st.radio(
        "Choose your mode",
        ["General Chat", "Document Chat"],
        index=0,
    )

    st.session_state.chat_mode = mode

    if st.button("＋ New Chat", use_container_width=True):
        clear_chat()
        st.rerun()

    st.divider()

    st.subheader("📁 Your Document")

    if mode == "Document Chat":
        uploaded_file = st.file_uploader(
            "Upload PDF or PowerPoint",
            type=["pdf", "pptx"],
        )

        if uploaded_file:
            if uploaded_file.name != st.session_state.document_name:
                with st.spinner("Reading your document..."):
                    text, error = extract_document_text(uploaded_file)

                if error:
                    st.error(error)
                else:
                    st.session_state.document_text = text
                    st.session_state.document_name = uploaded_file.name
                    clear_chat()
                    st.success("Document uploaded successfully!")

        if st.session_state.document_name:
            st.caption(
                f"Current file: {st.session_state.document_name}"
            )

    else:
        st.caption("Ask MILO anything!")

    st.divider()

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        clear_chat()
        st.rerun()


# --------------------------------------------------
# MAIN INTERFACE
# --------------------------------------------------

st.title("🤖 MILO")

if mode == "General Chat":
    st.caption("Your personal AI assistant. Ask me anything!")

else:
    st.caption("Upload a document and ask questions about it.")


# --------------------------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------------------------

for message in get_chat_history(limit=100):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

if mode == "Document Chat" and not st.session_state.document_text:
    st.info("Upload a PDF or PPTX from the sidebar to start chatting.")

question = st.chat_input("Message MILO...")

if question:

    if mode == "Document Chat" and not st.session_state.document_text:
        st.warning("Please upload a document first.")

    else:
        add_message("user", question)

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("MILO is thinking..."):

                if mode == "General Chat":
                    answer = get_general_response(question)

                else:
                    prompt = create_document_prompt(
                        st.session_state.document_text,
                        question,
                        get_chat_history(limit=10)[:-1],
                    )
                    answer = get_ai_response(prompt)

                st.markdown(answer)

        add_message("assistant", answer)
