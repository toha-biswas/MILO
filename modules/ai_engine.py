
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage


MODELS = [
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
]

SYSTEM_PROMPT = """
You are MILO, a friendly and intelligent personal AI assistant.

Rules:
- Give clear, natural and helpful answers.
- Explain difficult concepts simply.
- Help with Python, C, AI and data science.
- Use headings and bullets when helpful.
- Keep simple answers concise.
- Never invent information.
"""


@st.cache_resource
def get_ai_model(model_name):
    return ChatGroq(
        model=model_name,
        api_key=st.secrets["GROQ_API_KEY"],
        temperature=0.7,
        max_retries=0,
    )


def get_ai_response(prompt):
    """Generate an AI response with model fallback."""

    errors = []

    for model_name in MODELS:
        try:
            model = get_ai_model(model_name)

            response = model.invoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=str(prompt)),
            ])

            answer = response.content

            if isinstance(answer, str) and answer.strip():
                print(f"MILO SUCCESS: {model_name}")
                return answer

            errors.append(f"{model_name}: Empty response")

        except Exception as exc:
            error_message = str(exc)
            print(f"MILO ERROR ({model_name}): {error_message}")

            errors.append(f"{model_name}: {error_message}")

            error_lower = error_message.lower()

            fallback_errors = [
                "429",
                "rate_limit",
                "rate limit",
                "too many requests",
                "503",
                "service unavailable",
                "overloaded",
                "model_decommissioned",
                "model not found",
                "does not exist",
                "not supported",
            ]

            if any(item in error_lower for item in fallback_errors):
                continue

            return f"MILO AI Error: {error_message}"

    return (
        "MILO is temporarily unable to respond. "
        "Please check your Groq model availability and API limits, "
        "then try again."
    )
