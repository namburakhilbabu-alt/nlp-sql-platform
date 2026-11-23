"""
Pipeline tests for run_query with the LLM, vector store and database stubbed out,
so they run without Groq/Ollama, ChromaDB or the seeded SQLite file.
Run: pytest tests/ -v
"""
import os
import sys
import types

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _stub(name, **attrs):
    module = types.ModuleType(name)
    module.__dict__.update(attrs)
    sys.modules[name] = module


# Heavy dependencies (ChromaDB, sentence-transformers, SQLite) are replaced before import.
_stub("app.schema.schema_manager",
      get_relevant_tables=lambda q, top_k=5: [{"table_name": "invoices"}],
      get_table_schema_text=lambda tables: "invoices(id, amount)")
_stub("app.schema.schema_graph", discover_joins=lambda tables: [])
_stub("app.services.cache_service", get_cached_sql=lambda q: None, cache_query=lambda q, s: None)
_stub("app.models.database", execute_query=lambda sql: [{"id": 1}])

from app.services import query_service  # noqa: E402
from app.llm.gemini_client import LLMUnavailableError  # noqa: E402


@pytest.fixture
def cached(monkeypatch):
    calls = []
    monkeypatch.setattr(query_service, "cache_query", lambda q, s: calls.append((q, s)))
    monkeypatch.setattr(query_service, "_get_explanation", lambda q, s, d: "ok")
    return calls


def test_successful_query_is_cached(monkeypatch, cached):
    monkeypatch.setattr(query_service, "generate_with_retry",
                        lambda prompt, **kw: "SELECT id FROM invoices LIMIT 5")
    result = query_service.run_query("show invoices", session_id="t1")
    assert result.data == [{"id": 1}]
    assert cached == [("show invoices", "SELECT id FROM invoices LIMIT 5")]


def test_failing_sql_is_not_returned_or_cached(monkeypatch, cached):
    monkeypatch.setattr(query_service, "generate_with_retry",
                        lambda prompt, **kw: "SELECT nope FROM missing LIMIT 5")

    def broken(sql):
        raise Exception("no such table: missing")

    monkeypatch.setattr(query_service, "execute_query", broken)
    with pytest.raises(RuntimeError, match="Could not generate valid SQL"):
        query_service.run_query("show invoices", session_id="t2")
    assert cached == []


def test_llm_outage_is_not_retried_as_bad_sql(monkeypatch, cached):
    calls = []

    def down(prompt, **kw):
        calls.append(prompt)
        raise LLMUnavailableError("Groq down")

    monkeypatch.setattr(query_service, "generate_with_retry", down)
    with pytest.raises(LLMUnavailableError):
        query_service.run_query("show invoices", session_id="t3")
    assert len(calls) == 1
