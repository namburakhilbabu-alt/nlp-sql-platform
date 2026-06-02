"""
Multi-turn conversation session management.
Stores conversation history in memory (keyed by session_id).
"""
from collections import defaultdict
from app.core.logging_config import logger

_sessions: dict[str, list[dict]] = defaultdict(list)
MAX_HISTORY = 10


def get_history(session_id: str) -> list[dict]:
    return _sessions.get(session_id, [])


def add_turn(session_id: str, question: str, sql: str, result_count: int, explanation: str = ""):
    _sessions[session_id].append({
        "question": question,
        "sql": sql,
        "result_count": result_count,
        "explanation": explanation,
    })
    if len(_sessions[session_id]) > MAX_HISTORY:
        _sessions[session_id] = _sessions[session_id][-MAX_HISTORY:]
    logger.debug(f"Session {session_id}: {len(_sessions[session_id])} turns in history")


def clear_session(session_id: str):
    if session_id in _sessions:
        del _sessions[session_id]
        logger.info(f"Session {session_id} cleared.")


def list_sessions() -> list[str]:
    return list(_sessions.keys())
