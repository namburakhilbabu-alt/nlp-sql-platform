"""
Intent classifier — decides if a message needs SQL pipeline or plain chat.
One fast LLM call before the full pipeline runs.
"""
from app.llm.gemini_client import generate_with_retry
from app.core.logging_config import logger

CLASSIFY_PROMPT = """You are an intent classifier for an enterprise data assistant.

Classify the user's message into exactly one of these two categories:

DATA  — if the message is asking about business data, reports, metrics, records, or
        anything that could be answered by querying a database (invoices, vendors,
        customers, sales, orders, payments, expenses, employees, products, inventory,
        contracts, leaves, purchase orders, outstanding amounts, delays, etc.)

CHAT  — if the message is a greeting, small talk, general question, thank you,
        or anything NOT related to business data.

Examples:
"Hi there" → CHAT
"How are you?" → CHAT
"What can you do?" → CHAT
"show unpaid invoices above 5 lakhs" → DATA
"top 10 vendors by payment delay" → DATA
"which customers have outstanding balance?" → DATA
"thanks" → CHAT
"explain what an invoice is" → CHAT

User message: "{question}"

Reply with a single word only — DATA or CHAT:"""


def classify_intent(question: str) -> str:
    """Returns 'data' or 'chat'."""
    try:
        prompt = CLASSIFY_PROMPT.format(question=question.strip())
        raw = generate_with_retry(prompt, max_retries=2, temperature=0.0)
        result = raw.strip().upper().split()[0] if raw.strip() else "DATA"
        intent = "data" if "DATA" in result else "chat"
        logger.info(f"Intent classified: '{question[:40]}' → {intent}")
        return intent
    except Exception as e:
        logger.warning(f"Intent classification failed, defaulting to 'data': {e}")
        return "data"


CHAT_PROMPT = """You are DataMind, a friendly enterprise AI data assistant.
You help business users query their company database using plain English.

The user said: "{question}"

Reply in 2-3 sentences. Be helpful and friendly. If they're asking what you can do,
mention you can answer business questions about invoices, vendors, customers, sales,
expenses, employees, inventory, and more — just ask in plain English."""


def generate_chat_response(question: str) -> str:
    try:
        prompt = CHAT_PROMPT.format(question=question.strip())
        return generate_with_retry(prompt, max_retries=2, temperature=0.7)
    except Exception as e:
        logger.warning(f"Chat response failed: {e}")
        return "Hi! I'm DataMind, your enterprise data assistant. Ask me any business question like 'show unpaid invoices above 5 lakhs' and I'll query the database for you."
