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
MUSIC_PATH = STATIC_DIR / "milo_music.mp3"

initialize_memory()

st.session_state.setdefault("milo_open", False)
st.session_state.setdefault("chat_mode", "General Chat")
st.session_state.setdefault("quick_prompt", None)


# ============================================================
# MEDIA LOADER (CACHED BASE64 MP3)
# ============================================================

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
                else:
                    recent_history = get_chat_history(limit=10)
                    prompt = create_document_prompt(
                        document_text,
                        question,
                        recent_history,
                    )
                    answer = get_ai_response(prompt)

            add_message("user", question)
            add_message("assistant", str(answer))

        except Exception as exc:
            answer = f"Sorry, I couldn't complete that request. Error: {exc}"
            add_message("user", question)
            add_message("assistant", answer)


# ============================================================
# DESIGN SYSTEM & FULL-SCREEN 3D HOLOGRAPHIC RADAR HUD THEME
# ============================================================

st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
    --red: #ff304f;
    --pink: #ff5c7c;
    --crimson-deep: #b81131;
    --cyan: #00e5ff;
    --dark: #07070b;
    --panel: #0e0e14;
    --border: rgba(255, 255, 255, 0.08);
    --border-crimson: rgba(255, 48, 79, 0.38);
    --text: #f5f5f7;
    --text-muted: #9a9aa6;
    --green: #62e6a4;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text);
}

.stApp {
    background: var(--dark);
}

#MainMenu, footer, header[data-testid="stHeader"] {
    background: transparent !important;
}

#MainMenu, footer {
    visibility: hidden;
}

.main .block-container {
    max-width: 1250px;
    padding-top: 3rem;
    position: relative;
    z-index: 2;
}

/* ============================================================
   FULL-SCREEN 3D HOLOGRAPHIC RADAR RINGS BACKGROUND
   ============================================================ */
.milo-radar-bg {
    position: fixed;
    inset: 0;
    z-index: 0;
    overflow: hidden;
    background-color: #05060b;
    background-image:
        radial-gradient(ellipse at 50% 50%, rgba(0, 229, 255, 0.13) 0%, rgba(255, 48, 79, 0.10) 40%, rgba(5, 6, 11, 0.96) 82%),
        linear-gradient(rgba(0, 229, 255, 0.055) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 229, 255, 0.055) 1px, transparent 1px);
    background-size: 100% 100%, 46px 46px, 46px 46px;
    pointer-events: none;
}

/* Full-Viewport Centered 3D Perspective Stage */
.milo-bg-stage {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 155vmax;
    height: 155vmax;
    transform: translate(-50%, -50%) perspective(920px) rotateX(56deg);
    transform-style: preserve-3d;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Concentric Topographic Radar Rings spanning full screen */
.milo-bg-ring {
    position: absolute;
    border-radius: 50%;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}

.milo-bg-ring-1 {
    width: 24vmax;
    height: 24vmax;
    border: 1.5px solid rgba(0, 229, 255, 0.42);
    box-shadow: 0 0 32px rgba(0, 229, 255, 0.24), inset 0 0 24px rgba(0, 229, 255, 0.16);
    animation: bgSpinCW 18s linear infinite;
}

.milo-bg-ring-2 {
    width: 44vmax;
    height: 44vmax;
    border: 2px dashed rgba(255, 48, 79, 0.36);
    box-shadow: 0 0 40px rgba(255, 48, 79, 0.16);
    animation: bgSpinCCW 28s linear infinite;
}

.milo-bg-ring-3 {
    width: 68vmax;
    height: 68vmax;
    border: 1.5px solid rgba(0, 229, 255, 0.26);
    border-top-color: rgba(255, 48, 79, 0.52);
    border-bottom-color: rgba(0, 229, 255, 0.58);
    animation: bgSpinCW 38s linear infinite;
}

.milo-bg-ring-4 {
    width: 94vmax;
    height: 94vmax;
    border: 2px dashed rgba(0, 229, 255, 0.20);
    animation: bgSpinCCW 52s linear infinite;
}

.milo-bg-ring-5 {
    width: 124vmax;
    height: 124vmax;
    border: 1px solid rgba(255, 48, 79, 0.22);
    border-left-color: rgba(0, 229, 255, 0.42);
    border-right-color: rgba(255, 48, 79, 0.42);
    animation: bgSpinCW 68s linear infinite;
}

/* Full-Screen Sweeping Conic Radar Beam */
.milo-bg-sweep {
    position: absolute;
    width: 128vmax;
    height: 128vmax;
    border-radius: 50%;
    top: 50%;
    left: 50%;
    background: conic-gradient(
        from 0deg,
        rgba(0, 229, 255, 0.26) 0deg,
        rgba(0, 229, 255, 0.08) 28deg,
        rgba(255, 48, 79, 0.06) 55deg,
        transparent 110deg,
        transparent 360deg
    );
    animation: bgSweep 9s linear infinite;
}

/* Expanding Pulse Wave */
.milo-bg-pulse {
    position: absolute;
    width: 30vmax;
    height: 30vmax;
    border-radius: 50%;
    top: 50%;
    left: 50%;
    border: 2px solid rgba(0, 229, 255, 0.45);
    animation: bgRadarPulse 5.5s ease-out infinite;
}

.milo-bg-pulse-red {
    position: absolute;
    width: 30vmax;
    height: 30vmax;
    border-radius: 50%;
    top: 50%;
    left: 50%;
    border: 2px solid rgba(255, 48, 79, 0.42);
    animation: bgRadarPulse 5.5s ease-out 2.75s infinite;
}

/* Glowing Target Nodes Across Both Left & Right Sides */
.milo-bg-node {
    position: absolute;
    width: 10px;
    height: 10px;
    border-radius: 50%;
}

.milo-node-cyan-1 {
    top: 22%;
    left: 24%;
    background: var(--cyan);
    box-shadow: 0 0 18px var(--cyan), 0 0 36px var(--cyan);
    animation: nodeBlink 3.2s ease-in-out infinite;
}

.milo-node-cyan-2 {
    top: 74%;
    left: 72%;
    background: var(--cyan);
    box-shadow: 0 0 18px var(--cyan), 0 0 36px var(--cyan);
    animation: nodeBlink 4.1s ease-in-out 1.1s infinite;
}

.milo-node-red-1 {
    top: 30%;
    left: 78%;
    background: var(--red);
    box-shadow: 0 0 20px var(--red), 0 0 40px var(--red);
    animation: nodeBlink 3.6s ease-in-out 0.6s infinite;
}

.milo-node-red-2 {
    top: 76%;
    left: 22%;
    background: var(--red);
    box-shadow: 0 0 20px var(--red), 0 0 40px var(--red);
    animation: nodeBlink 4.4s ease-in-out 1.9s infinite;
}

/* Crosshair & HUD Corner Telemetry Framing the Full Screen */
.milo-bg-crosshair-h {
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(0, 229, 255, 0.22) 25%, rgba(255, 48, 79, 0.28) 50%, rgba(0, 229, 255, 0.22) 75%, transparent 100%);
}

.milo-bg-crosshair-v {
    position: absolute;
    left: 50%;
    top: 0;
    bottom: 0;
    width: 1px;
    background: linear-gradient(180deg, transparent 0%, rgba(0, 229, 255, 0.22) 25%, rgba(255, 48, 79, 0.28) 50%, rgba(0, 229, 255, 0.22) 75%, transparent 100%);
}

.milo-hud-corner {
    position: fixed;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2.4px;
    color: rgba(0, 229, 255, 0.34);
    z-index: 1;
    pointer-events: none;
}

.milo-corner-tr { top: 22px; right: 28px; }
.milo-corner-br { bottom: 20px; right: 28px; color: rgba(255, 48, 79, 0.38); }
.milo-corner-bl { bottom: 20px; left: 28px; }

/* Subtle Vignette for Crisp Text Contrast */
.milo-overlay {
    position: absolute;
    inset: 0;
    background:
        radial-gradient(circle at 50% 50%, transparent 32%, rgba(4, 5, 9, 0.72) 100%),
        linear-gradient(90deg, rgba(5, 6, 10, 0.62) 0%, rgba(5, 6, 10, 0.24) 55%, rgba(5, 6, 10, 0.35) 100%);
}

/* ============================================================
   SIDEBAR
   ============================================================ */
section[data-testid="stSidebar"] {
    background: rgba(11, 11, 16, 0.94);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] hr {
    border-color: var(--border);
    margin: 1rem 0;
}

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(255, 255, 255, 0.025);
    border: 1px solid var(--border);
    border-radius: 11px;
    padding: 9px 12px;
    transition: all 0.2s ease;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    border-color: var(--border-crimson);
    background: rgba(255, 48, 79, 0.06);
}

/* ============================================================
   LANDING HERO
   ============================================================ */
.milo-ready-pill {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 999px;
    padding: 9px 18px;
    color: #e4e4ec;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10.5px;
    letter-spacing: 2.8px;
    font-weight: 700;
    background: rgba(14, 14, 20, 0.65);
    backdrop-filter: blur(12px);
}

.milo-ready-dot {
    width: 7px;
    height: 7px;
    background: var(--green);
    border-radius: 50%;
    box-shadow: 0 0 12px var(--green);
    animation: pulseGlow 2.4s infinite ease-in-out;
}

.milo-welcome {
    margin-top: 38px;
    color: #d8d8e2;
    font-size: 14.5px;
    letter-spacing: 0.2px;
}

.milo-hero {
    margin-top: 48px;
    animation: entrance 0.85s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.milo-eyebrow {
    color: var(--red);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 4.5px;
    font-weight: 700;
    margin-bottom: 16px;
}

.milo-title {
    color: #ffffff;
    font-size: clamp(78px, 12.5vw, 150px);
    font-weight: 900;
    letter-spacing: -8px;
    line-height: 0.94;
    margin: 0;
    text-shadow: 0 0 70px rgba(255, 48, 79, 0.24);
}

.milo-title span {
    background: linear-gradient(135deg, var(--red), var(--pink));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.milo-subtitle {
    color: #c5c5d0;
    font-size: 17px;
    line-height: 1.85;
    margin-top: 24px;
    max-width: 520px;
}

.milo-meta {
    color: var(--text-muted);
    font-family: 'JetBrains Mono', monospace;
    font-size: 10.5px;
    font-weight: 600;
    letter-spacing: 2.8px;
    margin-top: 38px;
}

.milo-meta .dot {
    color: var(--green);
}

/* ============================================================
   BUTTONS
   ============================================================ */
.stButton > button {
    background: linear-gradient(115deg, var(--red), var(--crimson-deep));
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 12px;
    padding: 13px 26px;
    font-weight: 700;
    letter-spacing: 0.6px;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 8px 28px rgba(255, 48, 79, 0.24);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 36px rgba(255, 48, 79, 0.42);
    border-color: var(--pink);
    color: #ffffff;
}

/* Quick Access & Dialog Buttons */
div[role="dialog"] .stButton > button {
    background: rgba(255, 255, 255, 0.045);
    border: 1px solid rgba(255, 255, 255, 0.11);
    color: #e2e2ee;
    box-shadow: none;
    padding: 8px 14px;
    font-size: 12px;
    font-weight: 600;
    border-radius: 999px;
}

div[role="dialog"] .stButton > button:hover {
    background: linear-gradient(120deg, rgba(255, 48, 79, 0.24), rgba(0, 229, 255, 0.14));
    border-color: var(--pink);
    color: #ffffff;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(255, 48, 79, 0.24);
}

/* ============================================================
   MILO AI WORKSPACE DIALOG
   ============================================================ */
div[data-testid="stDialog"] > div[role="dialog"] {
    background:
        radial-gradient(circle at 50% 42%, rgba(255, 48, 79, 0.09) 0%, rgba(0, 229, 255, 0.04) 45%, transparent 70%),
        rgba(9, 10, 15, 0.97) !important;
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    border: 1px solid rgba(255, 255, 255, 0.09) !important;
    border-top: 1.5px solid rgba(255, 48, 79, 0.55) !important;
    border-radius: 22px !important;
    box-shadow:
        0 30px 90px rgba(0, 0, 0, 0.9),
        0 0 80px rgba(255, 48, 79, 0.14) !important;
    padding: 1.35rem 1.65rem 1.25rem 1.65rem !important;
    max-width: 940px !important;
    width: 94vw !important;
    animation: modalReveal 0.32s cubic-bezier(0.16, 1, 0.3, 1) both;
}

div[role="dialog"] [data-testid="stDialogHeader"] {
    padding-bottom: 0.35rem;
}

div[role="dialog"] [data-testid="stDialogHeader"] h2 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.12rem !important;
    letter-spacing: 1.5px !important;
    color: #ffffff !important;
}

/* Workspace HUD Subheader + Telemetry Strip */
.milo-hud-bar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 9px 14px;
    margin-bottom: 8px;
    background: linear-gradient(90deg, rgba(255, 48, 79, 0.09), rgba(0, 229, 255, 0.04), rgba(255, 255, 255, 0.02));
    border: 1px solid var(--border);
    border-radius: 12px;
}

.milo-hud-left {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}

.milo-mode-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(255, 48, 79, 0.16);
    border: 1px solid rgba(255, 48, 79, 0.42);
    color: #ff7a93;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 1.6px;
}

.milo-doc-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(0, 229, 255, 0.09);
    border: 1px solid rgba(0, 229, 255, 0.28);
    color: #9beeff;
    font-size: 11.5px;
    font-weight: 500;
}

.milo-telemetry-row {
    display: flex;
    align-items: center;
    gap: 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 1.4px;
    color: #888898;
}

.milo-telemetry-row span b {
    color: #d5d5e2;
    font-weight: 700;
}

/* ============================================================
   3D HOLOGRAPHIC RADAR HUD ARENA (CHAT VIEWPORT THEME)
   ============================================================ */
div[role="dialog"] div[data-testid="stVerticalBlockBorderWrapper"] {
    position: relative;
    overflow: hidden;
    border-radius: 16px !important;
    border: 1px solid rgba(255, 48, 79, 0.25) !important;
    background-color: #06070c !important;
    background-image:
        radial-gradient(ellipse at 50% 52%, rgba(0, 229, 255, 0.11) 0%, rgba(255, 48, 79, 0.10) 36%, transparent 72%),
        repeating-radial-gradient(circle at 50% 52%, rgba(0, 229, 255, 0.07) 0px, rgba(0, 229, 255, 0.07) 1px, transparent 1px, transparent 22px),
        linear-gradient(rgba(255, 48, 79, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 229, 255, 0.035) 1px, transparent 1px) !important;
    background-size: 100% 100%, 100% 100%, 36px 36px, 36px 36px !important;
    box-shadow:
        inset 0 0 60px rgba(0, 0, 0, 0.88),
        inset 0 0 28px rgba(0, 229, 255, 0.06) !important;
    padding: 14px 16px !important;
}

div[role="dialog"] div[data-testid="stVerticalBlockBorderWrapper"]::before {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 310px;
    height: 310px;
    margin-top: -155px;
    margin-left: -155px;
    border-radius: 50%;
    border: 1.5px dashed rgba(0, 229, 255, 0.26);
    box-shadow:
        0 0 40px rgba(0, 229, 255, 0.10),
        inset 0 0 30px rgba(255, 48, 79, 0.12);
    animation: radarOrbit 22s linear infinite;
    pointer-events: none;
    z-index: 0;
}

div[role="dialog"] div[data-testid="stVerticalBlockBorderWrapper"]::after {
    content: "SCANNING // MILO NEURAL RADAR · HZ 234";
    position: absolute;
    bottom: 10px;
    right: 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 9.5px;
    font-weight: 700;
    letter-spacing: 2.5px;
    color: rgba(0, 229, 255, 0.24);
    pointer-events: none;
    white-space: nowrap;
    z-index: 0;
}

div[role="dialog"] div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 12px !important;
    position: relative;
    z-index: 1;
}

/* ============================================================
   PURE CSS 3D HOLOGRAPHIC HERO CORE (ZERO SVG SANITIZATION RISK)
   ============================================================ */
.milo-empty-state {
    position: relative;
    text-align: center;
    padding: 20px 20px 18px 20px;
    margin: 2px 0;
    border-radius: 18px;
    background:
        radial-gradient(ellipse at 50% 30%, rgba(0, 229, 255, 0.14), rgba(255, 48, 79, 0.08) 48%, transparent 78%),
        rgba(10, 12, 18, 0.78);
    border: 1px solid rgba(0, 229, 255, 0.24);
    backdrop-filter: blur(10px);
    animation: fadeSlideUp 0.45s ease both;
}

.milo-3d-stage {
    position: relative;
    width: 146px;
    height: 146px;
    margin: 0 auto 10px auto;
    perspective: 750px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.milo-3d-aura {
    position: absolute;
    width: 112px;
    height: 112px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 229, 255, 0.26) 0%, rgba(255, 48, 79, 0.14) 52%, transparent 75%);
    filter: blur(8px);
    animation: pulseGlow 3s ease-in-out infinite;
}

/* 3D Tilted Gyroscope Rings */
.milo-3d-ring {
    position: absolute;
    border-radius: 50%;
    transform-style: preserve-3d;
}

.milo-ring-outer {
    width: 138px;
    height: 138px;
    border: 1.5px dashed rgba(0, 229, 255, 0.58);
    box-shadow: 0 0 18px rgba(0, 229, 255, 0.22);
    animation: gyro3dA 9s linear infinite;
}

.milo-ring-mid {
    width: 112px;
    height: 112px;
    border: 2px solid transparent;
    border-top-color: var(--red);
    border-bottom-color: var(--pink);
    border-left-color: rgba(255, 48, 79, 0.25);
    box-shadow: 0 0 22px rgba(255, 48, 79, 0.35);
    animation: gyro3dB 6.5s linear infinite;
}

.milo-ring-inner {
    width: 84px;
    height: 84px;
    border: 1.5px solid transparent;
    border-left-color: var(--cyan);
    border-right-color: #ffffff;
    box-shadow: inset 0 0 14px rgba(0, 229, 255, 0.3);
    animation: gyro3dC 4.5s linear infinite;
}

/* 3D Horizontal Radar Disc */
.milo-radar-disc {
    position: absolute;
    width: 132px;
    height: 132px;
    border-radius: 50%;
    border: 1px solid rgba(0, 229, 255, 0.28);
    background: conic-gradient(from 0deg, rgba(0, 229, 255, 0.32), rgba(255, 48, 79, 0.12) 45deg, transparent 120deg);
    animation: radarDiscSpin 3.6s linear infinite;
}

/* 3D Glowing Core Orb + Equalizer Bars */
.milo-core-orb {
    position: relative;
    z-index: 3;
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background: radial-gradient(circle at 32% 30%, #ffffff 0%, #7ceeff 26%, #ff304f 72%, #5e0819 100%);
    box-shadow:
        0 0 24px rgba(0, 229, 255, 0.72),
        0 0 42px rgba(255, 48, 79, 0.55),
        inset 0 -6px 12px rgba(0, 0, 0, 0.65);
    display: flex;
    align-items: center;
    justify-content: center;
    animation: coreFloat 3.2s ease-in-out infinite;
}

.milo-core-bars {
    display: flex;
    align-items: center;
    gap: 2.5px;
    height: 16px;
}

.milo-core-bars span {
    width: 2.5px;
    border-radius: 99px;
    background: #ffffff;
    box-shadow: 0 0 6px #ffffff;
    animation: coreWave 1s ease-in-out infinite;
}

.milo-core-bars span:nth-child(1) { height: 6px; animation-delay: 0.0s; }
.milo-core-bars span:nth-child(2) { height: 13px; animation-delay: 0.15s; }
.milo-core-bars span:nth-child(3) { height: 16px; animation-delay: 0.3s; }
.milo-core-bars span:nth-child(4) { height: 11px; animation-delay: 0.45s; }
.milo-core-bars span:nth-child(5) { height: 7px; animation-delay: 0.6s; }

.milo-empty-tag {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2.5px;
    color: var(--cyan);
    margin-bottom: 4px;
}

.milo-empty-title {
    font-size: 19px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.3px;
    margin-bottom: 5px;
}

.milo-empty-sub {
    font-size: 13px;
    color: var(--text-muted);
    max-width: 460px;
    margin: 0 auto;
    line-height: 1.55;
}

/* ============================================================
   WHATSAPP-STYLE CHAT BUBBLES (NO CLIPPING, CLEAN TAILS)
   ============================================================ */
div[data-testid="stChatMessage"] {
    display: inline-flex !important;
    align-items: flex-start !important;
    width: fit-content !important;
    min-width: 64px !important;
    max-width: 78% !important;
    height: auto !important;
    min-height: unset !important;
    overflow: visible !important;
    padding: 11px 16px !important;
    margin: 2px 0 !important;
    box-sizing: border-box !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.42) !important;
    animation: fadeSlideUp 0.24s cubic-bezier(0.16, 1, 0.3, 1) both;
}

div[data-testid="stChatMessage"] > div:first-child {
    display: none !important;
}

div[data-testid="stChatMessageContent"] {
    display: block !important;
    width: auto !important;
    height: auto !important;
    min-height: unset !important;
    overflow: visible !important;
    padding: 0 !important;
    margin: 0 !important;
}

div[data-testid="stChatMessageContent"] > div,
div[data-testid="stChatMessageContent"] [data-testid="stMarkdownContainer"] {
    display: block !important;
    height: auto !important;
    overflow: visible !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* MILO (Assistant) Bubble — Left aligned */
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]),
div[data-testid="stChatMessage"]:has([aria-label*="assistant"]) {
    align-self: flex-start !important;
    margin-right: auto !important;
    margin-left: 0 !important;
    background: linear-gradient(145deg, rgba(22, 26, 38, 0.95), rgba(14, 16, 24, 0.97)) !important;
    border: 1px solid rgba(0, 229, 255, 0.22) !important;
    border-left: 2.5px solid var(--cyan) !important;
    border-radius: 18px 18px 18px 4px !important;
    backdrop-filter: blur(8px);
}

/* User Bubble — Right aligned */
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
div[data-testid="stChatMessage"]:has([aria-label*="user"]) {
    align-self: flex-end !important;
    margin-left: auto !important;
    margin-right: 0 !important;
    background: linear-gradient(135deg, #d81b42, #910e29) !important;
    border: 1px solid rgba(255, 110, 138, 0.42) !important;
    box-shadow: 0 6px 22px rgba(255, 48, 79, 0.28) !important;
    border-radius: 18px 18px 4px 18px !important;
}

div[data-testid="stChatMessage"] p {
    font-size: 14.5px !important;
    line-height: 1.55 !important;
    color: #ffffff !important;
    margin: 0 !important;
    padding: 0 !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
}

div[data-testid="stChatMessage"] p + p {
    margin-top: 8px !important;
}

div[data-testid="stChatMessage"] code {
    background: rgba(0, 0, 0, 0.48) !important;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 6px;
    padding: 2px 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12.5px;
}

/* ============================================================
   WHATSAPP-STYLE PILL INPUT COMPOSER
   ============================================================ */
div[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
    padding-top: 6px !important;
}

div[data-testid="stChatInput"] > div {
    background: #161620 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 999px !important;
    padding: 2px 6px 2px 14px !important;
    box-shadow: 0 8px 26px rgba(0, 0, 0, 0.45) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

div[data-testid="stChatInput"] > div:focus-within {
    border-color: var(--red) !important;
    box-shadow: 0 0 0 3px rgba(255, 48, 79, 0.16), 0 10px 30px rgba(0, 0, 0, 0.55) !important;
}

div[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #ffffff !important;
    border: none !important;
    font-size: 14px !important;
    line-height: 1.45 !important;
    padding: 10px 8px !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #7d7d8c !important;
}

div[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, var(--red), var(--crimson-deep)) !important;
    color: #ffffff !important;
    border-radius: 50% !important;
    width: 36px !important;
    height: 36px !important;
    border: none !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease !important;
}

div[data-testid="stChatInput"] button:hover {
    transform: scale(1.06);
    box-shadow: 0 0 16px rgba(255, 48, 79, 0.55) !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 5px;
    height: 5px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.14);
    border-radius: 999px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 48, 79, 0.5);
}

/* ============================================================
   KEYFRAMES & 3D ANIMATIONS
   ============================================================ */
@keyframes bgSpinCW {
    0% { transform: translate(-50%, -50%) rotate(0deg); }
    100% { transform: translate(-50%, -50%) rotate(360deg); }
}

@keyframes bgSpinCCW {
    0% { transform: translate(-50%, -50%) rotate(360deg); }
    100% { transform: translate(-50%, -50%) rotate(0deg); }
}

@keyframes bgSweep {
    0% { transform: translate(-50%, -50%) rotate(0deg); }
    100% { transform: translate(-50%, -50%) rotate(360deg); }
}

@keyframes bgRadarPulse {
    0% {
        transform: translate(-50%, -50%) scale(0.35);
        opacity: 0.85;
    }
    100% {
        transform: translate(-50%, -50%) scale(3.8);
        opacity: 0;
    }
}

@keyframes nodeBlink {
    0%, 100% { transform: scale(1); opacity: 0.9; }
    50% { transform: scale(1.7); opacity: 0.3; }
}

@keyframes entrance {
    from { opacity: 0; transform: translateY(22px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes modalReveal {
    from { opacity: 0; transform: translateY(14px) scale(0.985); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulseGlow {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.65; transform: scale(0.92); }
}

@keyframes radarOrbit {
    0% { transform: perspective(520px) rotateX(58deg) rotateZ(0deg); }
    100% { transform: perspective(520px) rotateX(58deg) rotateZ(360deg); }
}

@keyframes radarDiscSpin {
    0% { transform: rotateX(64deg) rotateZ(0deg); }
    100% { transform: rotateX(64deg) rotateZ(360deg); }
}

@keyframes gyro3dA {
    0% { transform: rotateX(62deg) rotateY(16deg) rotateZ(0deg); }
    100% { transform: rotateX(62deg) rotateY(16deg) rotateZ(360deg); }
}

@keyframes gyro3dB {
    0% { transform: rotateX(-55deg) rotateY(32deg) rotateZ(360deg); }
    100% { transform: rotateX(-55deg) rotateY(32deg) rotateZ(0deg); }
}

@keyframes gyro3dC {
    0% { transform: rotateX(28deg) rotateY(-64deg) rotateZ(0deg); }
    100% { transform: rotateX(28deg) rotateY(-64deg) rotateZ(360deg); }
}

@keyframes coreFloat {
    0%, 100% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-4px) scale(1.06); }
}

@keyframes coreWave {
    0%, 100% { transform: scaleY(0.45); opacity: 0.78; }
    50% { transform: scaleY(1.15); opacity: 1; }
}

@media (max-width: 768px) {
    .main .block-container {
        padding: 1.75rem 1rem;
    }

    .milo-title {
        font-size: 74px;
        letter-spacing: -4px;
    }

    .milo-subtitle {
        font-size: 14.5px;
    }

    div[data-testid="stDialog"] > div[role="dialog"] {
        padding: 1.1rem 1rem !important;
        width: 97vw !important;
        border-radius: 16px !important;
    }

    div[data-testid="stChatMessage"] {
        max-width: 86% !important;
    }

    .milo-telemetry-row, .milo-hud-corner {
        display: none;
    }
}
</style>
""")


# ============================================================
# FULL-SCREEN HOLOGRAPHIC RADAR BACKGROUND
# ============================================================

st.html("""
<div class="milo-radar-bg">
    <div class="milo-bg-crosshair-h"></div>
    <div class="milo-bg-crosshair-v"></div>
    <div class="milo-bg-stage">
        <div class="milo-bg-sweep"></div>
        <div class="milo-bg-pulse"></div>
        <div class="milo-bg-pulse-red"></div>
        <div class="milo-bg-ring milo-bg-ring-1"></div>
        <div class="milo-bg-ring milo-bg-ring-2"></div>
        <div class="milo-bg-ring milo-bg-ring-3"></div>
        <div class="milo-bg-ring milo-bg-ring-4"></div>
        <div class="milo-bg-ring milo-bg-ring-5"></div>
        <div class="milo-bg-node milo-node-cyan-1"></div>
        <div class="milo-bg-node milo-node-cyan-2"></div>
        <div class="milo-bg-node milo-node-red-1"></div>
        <div class="milo-bg-node milo-node-red-2"></div>
    </div>
    <div class="milo-overlay"></div>
</div>
<div class="milo-hud-corner milo-corner-tr">RADAR GRID // 360° ACTIVE</div>
<div class="milo-hud-corner milo-corner-bl">SECTOR 01 · NEURAL FIELD</div>
<div class="milo-hud-corner milo-corner-br">SCAN HZ · 234.8</div>
""")


# ============================================================
# PERSISTENT HTML5 AUDIO ENGINE (18s AUTO-STOP + SMOOTH FADE)
# ============================================================

def render_persistent_music_controller():
    music_src = get_music_source(str(MUSIC_PATH))

    if not music_src:
        st.warning(
            f"Background music not found: `{MUSIC_PATH}`. "
            "Place `milo_music.mp3` inside `static/` to enable audio."
        )
        return

    components.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800&family=JetBrains+Mono:wght@600;700&display=swap');
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
                background: transparent;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                color: #f5f5f7;
                overflow: hidden;
            }}
            .audio-deck {{
                background: linear-gradient(145deg, rgba(255, 48, 79, 0.11), rgba(14, 14, 21, 0.95));
                border: 1px solid rgba(255, 48, 79, 0.36);
                border-radius: 14px;
                padding: 11px 12px;
                box-shadow: 0 8px 26px rgba(0, 0, 0, 0.4);
            }}
            .header-row {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 8px;
                margin-bottom: 9px;
            }}
            .track-info {{
                display: flex;
                align-items: center;
                gap: 8px;
                min-width: 0;
            }}
            .eq {{
                display: flex;
                align-items: flex-end;
                gap: 2.5px;
                height: 14px;
                flex-shrink: 0;
            }}
            .eq span {{
                width: 2.5px;
                height: 4px;
                background: #ff304f;
                border-radius: 99px;
                transition: height 0.2s ease;
            }}
            .is-playing .eq span {{
                animation: eqBounce 0.85s infinite ease-in-out;
            }}
            .is-playing .eq span:nth-child(2) {{ animation-delay: 0.18s; }}
            .is-playing .eq span:nth-child(3) {{ animation-delay: 0.36s; }}
            .is-playing .eq span:nth-child(4) {{ animation-delay: 0.52s; }}
            @keyframes eqBounce {{
                0%, 100% {{ height: 4px; opacity: 0.6; }}
                50% {{ height: 14px; opacity: 1; }}
            }}
            .track-name {{
                font-size: 11.5px;
                font-weight: 700;
                color: #f4f4fa;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .status-pill {{
                font-family: 'JetBrains Mono', monospace;
                font-size: 9.5px;
                font-weight: 700;
                letter-spacing: 1px;
                color: #ff7a93;
                background: rgba(255, 48, 79, 0.16);
                border: 1px solid rgba(255, 48, 79, 0.34);
                padding: 2px 7px;
                border-radius: 999px;
                flex-shrink: 0;
            }}
            .is-playing .status-pill {{
                color: #62e6a4;
                background: rgba(98, 230, 164, 0.12);
                border-color: rgba(98, 230, 164, 0.35);
            }}
            #enableBanner {{
                display: none;
                margin-bottom: 8px;
            }}
            #enableSoundBtn {{
                width: 100%;
                padding: 9px 12px;
                border-radius: 10px;
                border: 1px solid rgba(255, 122, 147, 0.65);
                background: linear-gradient(115deg, #ff304f, #b81131);
                color: #ffffff;
                font-size: 12px;
                font-weight: 800;
                letter-spacing: 0.5px;
                cursor: pointer;
                box-shadow: 0 0 20px rgba(255, 48, 79, 0.42);
                animation: pulseBtn 2s infinite ease-in-out;
            }}
            #enableSoundBtn:hover {{
                filter: brightness(1.08);
            }}
            @keyframes pulseBtn {{
                0%, 100% {{ box-shadow: 0 0 14px rgba(255, 48, 79, 0.35); }}
                50% {{ box-shadow: 0 0 26px rgba(255, 48, 79, 0.7); }}
            }}
            .controls {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 7px;
            }}
            .ctrl-btn {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 5px;
                padding: 7px 10px;
                border-radius: 9px;
                font-size: 11.5px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            #playPauseBtn {{
                background: rgba(255, 48, 79, 0.2);
                color: #ffffff;
                border: 1px solid rgba(255, 48, 79, 0.45);
            }}
            #playPauseBtn:hover {{
                background: linear-gradient(120deg, #ff304f, #b81131);
                box-shadow: 0 0 14px rgba(255, 48, 79, 0.45);
            }}
            #muteBtn {{
                background: rgba(255, 255, 255, 0.05);
                color: #d5d5e2;
                border: 1px solid rgba(255, 255, 255, 0.12);
            }}
            #muteBtn:hover {{
                background: rgba(255, 48, 79, 0.14);
                border-color: rgba(255, 48, 79, 0.4);
                color: #ffffff;
            }}
        </style>
        </head>
        <body>
        <div id="deck" class="audio-deck">
            <div class="header-row">
                <div class="track-info">
                    <div class="eq"><span></span><span></span><span></span><span></span></div>
                    <div class="track-name" title="milo_music.mp3 (18s Intro)">milo_music.mp3</div>
                </div>
                <span id="statusBadge" class="status-pill">STANDBY</span>
            </div>

            <div id="enableBanner">
                <button id="enableSoundBtn" type="button">🔊 Enable MILO Sound</button>
            </div>

            <div class="controls">
                <button id="playPauseBtn" class="ctrl-btn" type="button">▶ Play</button>
                <button id="muteBtn" class="ctrl-btn" type="button">🔊 Mute</button>
            </div>
        </div>

        <script>
            const musicSrc = {repr(music_src)};
            const parentDoc = window.parent.document;
            const parentWin = window.parent;
            const MAX_PLAY_MS = 18000;

            const deck = document.getElementById("deck");
            const enableBanner = document.getElementById("enableBanner");
            const enableSoundBtn = document.getElementById("enableSoundBtn");
            const playPauseBtn = document.getElementById("playPauseBtn");
            const muteBtn = document.getElementById("muteBtn");
            const statusBadge = document.getElementById("statusBadge");

            let audio = parentDoc.getElementById("milo-persistent-audio");
            if (!audio) {{
                audio = parentDoc.createElement("audio");
                audio.id = "milo-persistent-audio";
                audio.src = musicSrc;
                audio.loop = false;
                audio.preload = "auto";
                audio.volume = 0.45;
                audio.style.display = "none";
                parentDoc.body.appendChild(audio);
            }}

            function clearStopTimers() {{
                if (parentWin.__miloStopTimer) {{
                    clearTimeout(parentWin.__miloStopTimer);
                    parentWin.__miloStopTimer = null;
                }}
                if (parentWin.__miloFadeInterval) {{
                    clearInterval(parentWin.__miloFadeInterval);
                    parentWin.__miloFadeInterval = null;
                }}
            }}

            function scheduleAutoOff() {{
                clearStopTimers();
                audio.volume = 0.45;

                parentWin.__miloStopTimer = setTimeout(() => {{
                    parentWin.__miloFadeInterval = setInterval(() => {{
                        if (audio.volume > 0.05) {{
                            audio.volume = Math.max(0, audio.volume - 0.05);
                        }} else {{
                            clearStopTimers();
                            audio.pause();
                            audio.currentTime = 0;
                            audio.volume = 0.45;
                            parentWin.__miloUserPaused = true;
                            parentWin.__miloAutoStopped = true;
                            updateUI();
                        }}
                    }}, 150);
                }}, MAX_PLAY_MS - 1500);
            }}

            function updateUI() {{
                const isPlaying = !audio.paused && !audio.ended;
                const isMuted = audio.muted;

                if (isPlaying) {{
                    deck.classList.add("is-playing");
                    playPauseBtn.textContent = "⏸ Pause";
                    statusBadge.textContent = isMuted ? "MUTED" : "18S LIVE";
                    enableBanner.style.display = "none";
                }} else {{
                    deck.classList.remove("is-playing");
                    playPauseBtn.textContent = "▶ Play";
                    if (parentWin.__miloAutoStopped) {{
                        statusBadge.textContent = "AUTO OFF";
                    }} else {{
                        statusBadge.textContent = parentWin.__miloUserPaused ? "PAUSED" : "BLOCKED";
                    }}
                }}

                muteBtn.textContent = isMuted ? "🔇 Unmute" : "🔊 Mute";
            }}

            function attemptAutoplay() {{
                if (parentWin.__miloUserPaused || parentWin.__miloAutoStopped) {{
                    updateUI();
                    return;
                }}

                if (!audio.paused) {{
                    updateUI();
                    return;
                }}

                const playPromise = audio.play();
                if (playPromise !== undefined) {{
                    playPromise
                        .then(() => {{
                            enableBanner.style.display = "none";
                            scheduleAutoOff();
                            updateUI();
                        }})
                        .catch(() => {{
                            enableBanner.style.display = "block";
                            updateUI();
                        }});
                }}
            }}

            function enableAndPlay() {{
                parentWin.__miloUserPaused = false;
                parentWin.__miloAutoStopped = false;
                audio.muted = false;
                audio.currentTime = 0;
                audio.play()
                    .then(() => {{
                        enableBanner.style.display = "none";
                        scheduleAutoOff();
                        updateUI();
                    }})
                    .catch(updateUI);
            }}

            enableSoundBtn.addEventListener("click", enableAndPlay);

            playPauseBtn.addEventListener("click", () => {{
                if (audio.paused) {{
                    parentWin.__miloUserPaused = false;
                    parentWin.__miloAutoStopped = false;
                    if (audio.currentTime >= 17.5 || audio.ended) {{
                        audio.currentTime = 0;
                    }}
                    audio.play().then(() => {{
                        scheduleAutoOff();
                        updateUI();
                    }}).catch(updateUI);
                }} else {{
                    clearStopTimers();
                    parentWin.__miloUserPaused = true;
                    audio.pause();
                    updateUI();
                }}
            }});

            muteBtn.addEventListener("click", () => {{
                audio.muted = !audio.muted;
                updateUI();
            }});

            audio.addEventListener("ended", () => {{
                clearStopTimers();
                parentWin.__miloAutoStopped = true;
                parentWin.__miloUserPaused = true;
                updateUI();
            }});
            audio.addEventListener("play", updateUI);
            audio.addEventListener("pause", updateUI);
            audio.addEventListener("volumechange", updateUI);

            if (!parentWin.__miloGestureHooked) {{
                parentWin.__miloGestureHooked = true;
                parentDoc.addEventListener("pointerdown", () => {{
                    if (audio.paused && !parentWin.__miloUserPaused && !parentWin.__miloAutoStopped) {{
                        audio.play().then(() => {{
                            scheduleAutoOff();
                            updateUI();
                        }}).catch(() => {{}});
                    }}
                }}, {{ once: true }});
            }}

            attemptAutoplay();
        </script>
        </body>
        </html>
        """,
        height=124,
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("# 🤖 MILO")
    st.caption("PERSONAL AI WORKSPACE")

    st.divider()

    st.session_state.chat_mode = st.radio(
        "WORKSPACE",
        ["General Chat", "Document Chat"],
        index=(
            0 if st.session_state.chat_mode == "General Chat"
            else 1
        ),
    )

    if st.session_state.chat_mode == "Document Chat":
        st.divider()
        st.markdown("### 📄 DOCUMENT")

        uploaded_file = st.file_uploader(
            "Upload PDF or PowerPoint",
            type=["pdf", "pptx"],
        )

        if uploaded_file:
            if (
                st.session_state.get("document_name")
                != uploaded_file.name
            ):
                with st.spinner("Reading document..."):
                    document_text, error = extract_document_text(
                        uploaded_file
                    )

                if error:
                    st.error(error)
                else:
                    st.session_state.document_text = document_text
                    st.session_state.document_name = uploaded_file.name
                    st.success("Document loaded successfully!")

        if st.session_state.get("document_name"):
            st.caption(
                f"Loaded: {st.session_state.document_name}"
            )

    st.divider()
    st.markdown("### 🎵 AMBIENT AUDIO")
    render_persistent_music_controller()

    st.divider()

    if st.button("🗑 Clear conversation", use_container_width=True):
        clear_chat()
        st.rerun()

    st.caption("MILO V4 · CINEMATIC EDITION")


# ============================================================
# CHAT DIALOG
# ============================================================

@st.dialog("MILO  /  AI WORKSPACE", width="large")
def milo_chat_dialog():
    pending_prompt = st.session_state.pop("quick_prompt", None)
    if pending_prompt:
        handle_user_prompt(pending_prompt)
        st.rerun()

    mode_label = st.session_state.chat_mode.upper()
    doc_name = st.session_state.get("document_name") or ""
    safe_doc_name = html.escape(doc_name)
    doc_badge = (
        f'<span class="milo-doc-badge">📄 {safe_doc_name}</span>'
        if st.session_state.chat_mode == "Document Chat" and doc_name
        else ""
    )

    st.html(f"""
    <div class="milo-hud-bar">
        <div class="milo-hud-left">
            <span class="milo-mode-badge">● ACTIVE MODE / {mode_label}</span>
            {doc_badge}
        </div>
        <div class="milo-telemetry-row">
            <span>RADAR // <b>SYNCED</b></span>
            <span>CORE // <b>MILO-V4</b></span>
            <span>LINK // <b>ENCRYPTED</b></span>
        </div>
    </div>
    """)

    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        if st.button("✦ Instant Answers", key="qa_instant", use_container_width=True):
            st.session_state.chat_mode = "General Chat"
            st.session_state.quick_prompt = (
                "Give me 3 fascinating insights or productive ideas I can explore right now."
            )
            st.rerun()
    with qa2:
        if st.button("⚡ Code & Logic", key="qa_code", use_container_width=True):
            st.session_state.chat_mode = "General Chat"
            st.session_state.quick_prompt = (
                "Help me write, debug, or optimize code. Ask me what language or problem I'm working on."
            )
            st.rerun()
    with qa3:
        if st.button("📄 PDF & PPTX Analysis", key="qa_doc", use_container_width=True):
            st.session_state.chat_mode = "Document Chat"
            if st.session_state.get("document_text"):
                st.session_state.quick_prompt = (
                    "Summarize the uploaded document and highlight the top 5 key takeaways."
                )
            else:
                add_message(
                    "assistant",
                    "Switched to **Document Chat** 📄 — upload your PDF or PPTX in the left sidebar and ask me anything about it!",
                )
            st.rerun()

    history = get_chat_history(limit=100)

    chat_container = st.container(height=390, border=True)
    with chat_container:
        if not history:
            st.html("""
            <div class="milo-empty-state">
                <div class="milo-3d-stage">
                    <div class="milo-3d-aura"></div>
                    <div class="milo-radar-disc"></div>
                    <div class="milo-3d-ring milo-ring-outer"></div>
                    <div class="milo-3d-ring milo-ring-mid"></div>
                    <div class="milo-3d-ring milo-ring-inner"></div>
                    <div class="milo-core-orb">
                        <div class="milo-core-bars">
                            <span></span>
                            <span></span>
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                </div>
                <div class="milo-empty-tag">HOLOGRAPHIC RADAR ONLINE</div>
                <div class="milo-empty-title">Hello! I'm MILO.</div>
                <div class="milo-empty-sub">
                    Tap any quick-access mode above or type below to start chatting, writing code, or analyzing documents.
                </div>
            </div>
            """)

        for message in history:
            role = message.get("role", "assistant")
            with st.chat_message(role):
                st.markdown(message.get("content", ""))

    question = st.chat_input("Message MILO...")

    if question:
        handle_user_prompt(question)
        st.rerun()

    col_spacer, col_close = st.columns([4, 1.3])
    with col_close:
        if st.button("Close workspace", use_container_width=True):
            st.session_state.milo_open = False
            st.rerun()


# ============================================================
# LANDING PAGE
# ============================================================

main_left, main_right = st.columns([1, 11])

with main_right:
    st.html("""
    <div class="milo-ready-pill">
        <span class="milo-ready-dot"></span>
        SYSTEM READY
    </div>

    <div class="milo-welcome">
        <span style="color:#ff304f;">◎</span>
        &nbsp; Welcome! <b>MILO</b> is ready to assist you.
    </div>

    <div class="milo-hero">
        <div class="milo-eyebrow">
            PERSONAL ARTIFICIAL INTELLIGENCE
        </div>

        <h1 class="milo-title">MI<span>LO.</span></h1>

        <div class="milo-subtitle">
            Not just another chatbot.<br>
            A smarter space to think, learn, create,<br>
            and explore ideas with AI.
        </div>

        <div class="milo-meta">
            <span class="dot">●</span> SYSTEM READY
            &nbsp; / &nbsp; AI EXPERIENCE V4
        </div>
    </div>
    """)

    st.write("")

    if st.button("ENTER MILO  →", key="enter_milo"):
        st.session_state.milo_open = True
        st.rerun()


# ============================================================
# OPEN WORKSPACE
# ============================================================

if st.session_state.milo_open:
    milo_chat_dialog()
