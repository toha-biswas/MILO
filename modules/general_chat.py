
from modules.ai_engine import get_ai_response
from modules.chat_memory import get_chat_history


MAX_HISTORY_MESSAGES = 12


GENERAL_SYSTEM_PROMPT = """
You are MILO, a helpful, intelligent and friendly personal AI assistant.

PERSONALITY:
- Be natural, friendly, and conversational.
- Be clear and confident without pretending to know everything.
- Understand that the user may be a beginner.

CAPABILITIES:
- General knowledge and explanations.
- Python, C, programming and debugging.
- Data science, AI and technology.
- Writing, brainstorming and problem-solving.
- Learning guidance and project assistance.

RESPONSE RULES:
- Answer the actual question first.
- Use simple language when explaining difficult topics.
- Use headings and bullet points when useful.
- Keep simple answers concise.
- Give detailed explanations when requested.
- For coding questions, provide readable code and explain important parts.
- If information is uncertain, say so honestly.
- Use conversation history to understand follow-up questions.
"""


def create_general_prompt(question):
    """Build a context-aware prompt for general conversation."""

    history = get_chat_history(limit=MAX_HISTORY_MESSAGES)

    conversation = []

    for message in history:
        role = message.get("role", "user").upper()
        content = str(message.get("content", "")).strip()

        if content:
            conversation.append(f"{role}: {content}")

    history_text = (
        "\n".join(conversation)
        if conversation
        else "No previous conversation."
    )

    return f"""
{GENERAL_SYSTEM_PROMPT}

RECENT CONVERSATION:
{history_text}

CURRENT USER QUESTION:
{question}

Remember:
- Answer the current question.
- Use previous messages only when relevant.
- Do not repeat the conversation unnecessarily.
- Never invent missing information.

MILO RESPONSE:
"""


def get_general_response(question):
    """Generate a general AI response."""

    if not isinstance(question, str) or not question.strip():
        return "Please enter a question so I can help."

    prompt = create_general_prompt(question.strip())

    try:
        response = get_ai_response(prompt)

        if not response:
            return "I couldn't generate a response. Please try again."

        return str(response).strip()

    except Exception:
        return (
            "Something went wrong while generating your response. "
            "Please try again."
        )
