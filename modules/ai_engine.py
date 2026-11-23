
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage


# MILO model priority
MODELS = [
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
]

# MILO response style
SYSTEM_PROMPT = """
You are MILO, a helpful personal AI assistant.

Instructions:
- Give short, clear and simple answers.
- Use bullet points when helpful.
- Avoid unnecessary explanations.
- Keep answers around 3-6 sentences.
- Give more detail when the user asks.
- Be friendly and natural.
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
    for model_name in MODELS:
        try:
            model = get_ai_model(model_name)

            response = model.invoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=str(prompt))
            ])

            print(f"MILO SUCCESS: {model_name}")
            return response.content

        except Exception as e:
            error = str(e).lower()
            print(f"MILO ERROR ({model_name}): {e}")

            fallback_errors = [
                "429",
                "rate_limit",
                "rate limit",
                "too many requests",
                "503",
                "service unavailable",
                "overloaded",
            ]

            if any(item in error for item in fallback_errors):
                continue

            return f"MILO AI Error: {e}"

    return (
        "MILO is temporarily busy. "
        "Please try again in a little while."
    )

