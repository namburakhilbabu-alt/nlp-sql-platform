"""
Constraint guard for the semantic cache.

Sentence embeddings rate "unpaid invoices above 5 lakhs from last month" and
"... from last quarter" as near-identical (cosine ~0.95), yet the SQL must differ.
A cached query is therefore reused only when both questions agree on the parts
that change the answer: numbers, time window, comparison direction and status.
"""
import re

_NUMBER = re.compile(r"\d+(?:\.\d+)?")
_WORD = re.compile(r"[a-z0-9]+")

_TIME_WORDS = {
    "today", "yesterday", "tomorrow", "day", "days", "week", "weeks", "weekly",
    "month", "months", "monthly", "quarter", "quarters", "quarterly", "year", "years",
    "yearly", "annual", "ytd", "mtd", "qtd", "last", "this", "previous", "current",
    "next", "past", "recent", "since", "before", "after", "q1", "q2", "q3", "q4",
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december",
}

_DIRECTION = {
    "above": ">", "over": ">", "more": ">", "greater": ">", "exceeding": ">",
    "exceeds": ">", "exceed": ">", "higher": ">", "highest": ">", "top": ">", "most": ">",
    "below": "<", "under": "<", "less": "<", "fewer": "<", "lower": "<",
    "lowest": "<", "bottom": "<", "least": "<",
}

_STATUS_WORDS = {
    "paid", "unpaid", "pending", "approved", "rejected", "overdue", "outstanding",
    "active", "inactive", "open", "closed", "cancelled", "delivered", "delayed",
    "partial", "partially", "not", "no", "without",
}

_UNIT_WORDS = {"lakh", "lakhs", "crore", "crores", "thousand", "million", "k", "percent"}


def constraint_signature(question: str) -> tuple:
    text = question.lower()
    words = set(_WORD.findall(text))
    return (
        tuple(sorted(_NUMBER.findall(text))),
        frozenset(words & _TIME_WORDS),
        frozenset(_DIRECTION[w] for w in words if w in _DIRECTION),
        frozenset(words & _STATUS_WORDS),
        frozenset(w.rstrip("s") for w in words & _UNIT_WORDS),
    )


def constraints_match(question: str, cached_question: str) -> bool:
    return constraint_signature(question) == constraint_signature(cached_question)
