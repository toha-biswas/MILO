import base64
import html
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

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


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MILO | AI Experience",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
VIDEO_PATH = STATIC_DIR / "milo_intro.mp4"
MUSIC_PATH = STATIC_DIR / "milo_music.mp3"

initialize_memory()

st.session_state.setdefault("milo_open", False)
st.session_state.setdefault("chat_mode", "General Chat")
st.session_state.setdefault("quick_prompt", None)


# ============================================================
# MEDIA LOADERS (STATIC SERVING FOR VIDEO + CACHED BASE64 MP3)
# ============================================================

@st.cache_data(show_spinner=False)
def get_video_source(video_path_str: str) -> str | None:
    """
    Embed normal-sized MP4 files directly so playback does not depend on
    Streamlit Cloud's static-file route. For large files, use Streamlit's
    static-serving URL to avoid creating a very large HTML data URI.
    """
    path = Path(video_path_str)
    if not path.is_file():
        return None

    # Data URI is reliable for small/medium background clips on Cloud.
    max_embed_size = 30 * 1024 * 1024
    if path.stat().st_size <= max_embed_size:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:video/mp4;base64,{encoded}"

    # Large videos should be served from the app's static directory.
    return "/app/static/milo_intro.mp4"


@st.cache_data(show_spinner=False)
def get_music_source(music_path_str: str) -> str | None:
    path = Path(music_path_str)
    if not path.is_file():
        return None
    if path.stat().st_size <= 25 * 1024 * 1024:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:audio/mpeg;base64,{encoded}"
    return "/app/static/milo_music.mp3"


# ============================================================
# HELPER: PROCESS USER PROMPT (MANUAL OR ONE-CLICK QUICK ACTION)
# ============================================================

def handle_user_prompt(question: str):
    with st.spinner("MILO is thinking..."):
        try:
            if st.session_state.chat_mode == "General Chat":
                answer = get_general_response(question)
            else:
                document_text = st.session_state.get("document_text", "")
                if not document_text:
                    answer = (
                        "Document Chat mode is now active! Please upload a readable "
                        "PDF or PPTX file from the sidebar on the left, then ask your question."
                    )
