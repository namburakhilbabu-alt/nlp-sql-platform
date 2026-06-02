"""
SQL safety validation layer.
Blocks dangerous statements and checks for valid SQL structure.
"""
import re
import sqlparse
from app.core.logging_config import logger

BLOCKED_KEYWORDS = [
    r"\bDROP\b", r"\bDELETE\b", r"\bINSERT\b", r"\bUPDATE\b",
    r"\bTRUNCATE\b", r"\bALTER\b", r"\bCREATE\b", r"\bGRANT\b",
    r"\bREVOKE\b", r"\bEXEC\b", r"\bEXECUTE\b", r"\bXP_\b",
    r"--", r"/\*", r"\bUNION\b.*\bSELECT\b",
]


class SQLValidationError(Exception):
    pass


def validate_sql(sql: str) -> str:
    if not sql or not sql.strip():
        raise SQLValidationError("Empty SQL query generated.")

    sql_clean = sql.strip()

    # Strip markdown code blocks if model wrapped in them
    if sql_clean.startswith("```"):
        sql_clean = re.sub(r"^```[a-zA-Z]*\n?", "", sql_clean)
        sql_clean = re.sub(r"```$", "", sql_clean).strip()

    sql_upper = sql_clean.upper()

    # Must start with SELECT
    if not sql_upper.lstrip().startswith("SELECT"):
        raise SQLValidationError(f"Only SELECT queries are allowed. Got: {sql_clean[:80]}")

    # Block dangerous keywords
    for pattern in BLOCKED_KEYWORDS:
        if re.search(pattern, sql_upper, re.IGNORECASE):
            raise SQLValidationError(f"Blocked keyword detected in SQL: pattern='{pattern}'")

    # Parse and check structure
    try:
        parsed = sqlparse.parse(sql_clean)
        if not parsed or not parsed[0].tokens:
            raise SQLValidationError("SQL parse failed — no valid tokens found.")
    except Exception as e:
        raise SQLValidationError(f"SQL parsing error: {e}")

    # Warn if no LIMIT
    if "LIMIT" not in sql_upper:
        sql_clean = sql_clean.rstrip(";") + " LIMIT 100"
        logger.info("Auto-added LIMIT 100 to query.")

    logger.info(f"SQL validation passed.")
    return sql_clean


def extract_sql_from_response(raw_response: str) -> str:
    raw = raw_response.strip()
    # If model returned markdown block
    match = re.search(r"```(?:sql)?\s*(.*?)```", raw, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # If response has SELECT somewhere
    match = re.search(r"(SELECT\s.+)", raw, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return raw
