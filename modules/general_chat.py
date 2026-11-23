
from modules.ai_engine import get_ai_response
from modules.chat_memory import get_chat_history


def create_general_prompt(question):
    """Prepare a prompt for general AI conversation."""

    history = get_chat_history(limit=10)

    conversation = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in history
    )

    return f"""
You are MILO, a friendly, intelligent and helpful AI assistant.

Your responsibilities:
- Answer general questions clearly.
- Explain difficult topics in simple language.
- Help with Python, C, programming and data science.
- Help with writing, brainstorming and problem-solving.
- Keep answers concise unless more detail is requested.
- Understand follow-up questions using conversation history.
- Never pretend to know something you don't.

CONVERSATION HISTORY:
{conversation}

USER QUESTION:
{question}

MILO'S RESPONSE:
"""


def get_general_response(question):
    """Generate a general AI response."""

    prompt = create_general_prompt(question)

    return get_ai_response(prompt)
