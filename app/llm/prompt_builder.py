"""
Prompt engineering for NLP-to-SQL generation and business response formatting.
Includes adaptive optimization: join hints from graph reasoning are injected
into the prompt automatically based on which tables were retrieved.
"""
from datetime import date


def build_sql_prompt(
    question: str,
    schema_text: str,
    conversation_history: list[dict] = None,
    join_hints: list[str] = None,
) -> str:
    today = date.today().isoformat()

    history_text = ""
    if conversation_history:
        lines = []
        for turn in conversation_history[-4:]:
            lines.append(f"User: {turn['question']}")
            lines.append(f"SQL: {turn.get('sql', 'N/A')}")
        history_text = "\nPrevious conversation:\n" + "\n".join(lines) + "\n"

    # Adaptive: inject discovered JOIN paths into prompt
    join_section = ""
    if join_hints:
        join_section = "\nDISCOVERED JOIN CONDITIONS (use these exactly):\n"
        join_section += "\n".join(f"  - {h}" for h in join_hints) + "\n"

    return f"""You are an expert SQL analyst for an enterprise ERP system. Today's date is {today}.

DATABASE SCHEMA (SQLite):
{schema_text}

BUSINESS GLOSSARY:
- "lakh" = 100000  (e.g. "5 lakhs" = 500000)
- "crore" = 10000000
- "last quarter" = invoice_date >= date('now', '-3 months')
- "this month" = strftime('%Y-%m', column) = strftime('%Y-%m', 'now')
- "this year" = strftime('%Y', column) = strftime('%Y', 'now')
- "outstanding" = paid_amount < total_amount
- "overdue" = due_date < date('now') AND paid_amount < total_amount
- "payment delay" = julianday(actual_delivery) - julianday(expected_delivery)
- "unpaid" = status IN ('unpaid', 'overdue') OR paid_amount < total_amount
{join_section}{history_text}
RULES:
1. Return ONLY the SQL query — no explanation, no markdown, no code blocks.
2. SQLite syntax only: strftime() for date parts, julianday() for date math.
3. Always alias tables (FROM invoices AS i).
4. Use meaningful column aliases in SELECT (total_amount AS amount_rupees).
5. NEVER use DROP, DELETE, INSERT, UPDATE, ALTER, TRUNCATE.
6. Add LIMIT 100 unless the user asks for a specific number.
7. For date arithmetic always use julianday(), never subtract dates directly.
8. For payment delays: AVG(julianday(actual_delivery) - julianday(expected_delivery)).

Question: {question}

SQL:"""


def build_explanation_prompt(question: str, sql: str, results: list[dict]) -> str:
    preview = str(results[:5]) if results else "No rows returned"
    return f"""You are a business analyst presenting results to a non-technical manager.

The user asked: "{question}"

Query results summary — first 5 rows: {preview}
Total rows returned: {len(results)}

Write 2-3 sentences in plain business English. Highlight the key number or finding.
Do NOT mention SQL, databases, tables, or technical terms."""


def build_correction_prompt(
    question: str,
    schema_text: str,
    failed_sql: str,
    error: str,
    join_hints: list[str] = None,
) -> str:
    today = date.today().isoformat()
    join_section = ""
    if join_hints:
        join_section = "\nCORRECT JOIN CONDITIONS:\n" + "\n".join(f"  - {h}" for h in join_hints) + "\n"

    return f"""You are an expert SQL analyst. Today is {today}.
Fix the SQL query below. It failed with an error.

DATABASE SCHEMA (SQLite):
{schema_text}
{join_section}
Original question: {question}

Failed SQL:
{failed_sql}

Error: {error}

Rules: SQLite only. No markdown. Return ONLY the corrected SQL query.

Fixed SQL:"""
