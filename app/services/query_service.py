"""
Main query orchestration service.
Pipeline: question → schema retrieval → graph join discovery →
          adaptive prompt → SQL generation → validation → execution → explanation
"""
import time
from app.schema.schema_manager import get_relevant_tables, get_table_schema_text
from app.schema.schema_graph import discover_joins
from app.llm.gemini_client import generate_with_retry
from app.llm.prompt_builder import build_sql_prompt, build_explanation_prompt, build_correction_prompt
from app.validation.sql_validator import validate_sql, extract_sql_from_response, SQLValidationError
from app.models.database import execute_query
from app.services.cache_service import get_cached_sql, cache_query
from app.services.conversation_service import get_history, add_turn
from app.core.logging_config import logger

MAX_RETRIES = 3


class QueryResult:
    def __init__(self, question, sql, data, explanation,
                 relevant_tables, from_cache, confidence, execution_time_ms):
        self.question = question
        self.sql = sql
        self.data = data
        self.row_count = len(data)
        self.explanation = explanation
        self.relevant_tables = relevant_tables
        self.from_cache = from_cache
        self.confidence = confidence
        self.execution_time_ms = execution_time_ms

    def to_dict(self):
        return {
            "question": self.question,
            "sql": self.sql,
            "data": self.data,
            "row_count": self.row_count,
            "explanation": self.explanation,
            "relevant_tables": self.relevant_tables,
            "from_cache": self.from_cache,
            "confidence_score": self.confidence,
            "execution_time_ms": self.execution_time_ms,
        }


def run_query(question: str, session_id: str = "default") -> QueryResult:
    start = time.time()
    logger.info(f"Query | session={session_id} | question={question}")

    # 1. Semantic cache check — instant return if similar query seen before
    cached_sql = get_cached_sql(question)
    if cached_sql:
        data = execute_query(cached_sql)
        elapsed = int((time.time() - start) * 1000)
        explanation = _get_explanation(question, cached_sql, data)
        add_turn(session_id, question, cached_sql, len(data), explanation)
        logger.info(f"Cache hit | rows={len(data)} | {elapsed}ms")
        return QueryResult(question, cached_sql, data, explanation, [], True, 1.0, elapsed)

    # 2. Schema retrieval — find relevant tables from 800+ table space
    relevant_tables = get_relevant_tables(question, top_k=5)
    table_names = [t["table_name"] for t in relevant_tables]
    schema_text = get_table_schema_text(relevant_tables)
    logger.info(f"Relevant tables: {table_names}")

    # 3. Graph-based join discovery — autonomous JOIN path detection
    join_hints = discover_joins(table_names)
    if join_hints:
        logger.info(f"Auto-discovered JOINs: {join_hints}")

    # 4. Conversation history for multi-turn support
    history = get_history(session_id)

    # 5. SQL generation with adaptive prompts + retry + auto-correction
    sql = None
    data = []
    last_error = None
    confidence = 0.0

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if attempt == 1:
                prompt = build_sql_prompt(question, schema_text, history, join_hints)
            else:
                # Adaptive: correction prompt also gets join hints
                prompt = build_correction_prompt(
                    question, schema_text, sql or "", str(last_error), join_hints
                )

            raw = generate_with_retry(prompt)
            sql = extract_sql_from_response(raw)
            sql = validate_sql(sql)
            data = execute_query(sql)
            confidence = round(1.0 - (attempt - 1) * 0.15, 2)
            logger.info(f"SQL succeeded on attempt {attempt} | rows={len(data)}")
            break

        except SQLValidationError as e:
            last_error = e
            logger.warning(f"Attempt {attempt} validation: {e}")
        except Exception as e:
            last_error = e
            logger.warning(f"Attempt {attempt} execution: {e}")

    if sql is None:
        raise RuntimeError(
            f"Could not generate valid SQL after {MAX_RETRIES} attempts. "
            f"Last error: {last_error}"
        )

    # 6. Business explanation
    explanation = _get_explanation(question, sql, data)

    # 7. Cache successful query for future semantic matches
    cache_query(question, sql)

    # 8. Store in conversation history
    add_turn(session_id, question, sql, len(data), explanation)

    elapsed = int((time.time() - start) * 1000)
    logger.info(f"Query complete | rows={len(data)} | {elapsed}ms | confidence={confidence}")

    return QueryResult(
        question, sql, data, explanation,
        table_names, False, confidence, elapsed
    )


def _get_explanation(question: str, sql: str, data: list[dict]) -> str:
    try:
        prompt = build_explanation_prompt(question, sql, data)
        return generate_with_retry(prompt, temperature=0.3)
    except Exception as e:
        logger.warning(f"Explanation failed: {e}")
        return f"Query returned {len(data)} rows."
