"""
Basic tests for SQL validation and schema retrieval.
Run: pytest tests/ -v
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.validation.sql_validator import validate_sql, extract_sql_from_response, SQLValidationError


def test_valid_select():
    sql = "SELECT * FROM customers LIMIT 10"
    result = validate_sql(sql)
    assert "SELECT" in result.upper()


def test_blocks_drop():
    with pytest.raises(SQLValidationError):
        validate_sql("DROP TABLE customers")


def test_blocks_delete():
    with pytest.raises(SQLValidationError):
        validate_sql("DELETE FROM customers WHERE 1=1")


def test_blocks_insert():
    with pytest.raises(SQLValidationError):
        validate_sql("INSERT INTO customers VALUES (1, 'test')")


def test_auto_adds_limit():
    sql = "SELECT * FROM customers"
    result = validate_sql(sql)
    assert "LIMIT" in result.upper()


def test_strips_markdown_backticks():
    raw = "```sql\nSELECT * FROM customers LIMIT 5\n```"
    sql = extract_sql_from_response(raw)
    assert "SELECT" in sql.upper()
    assert "```" not in sql


def test_empty_sql_raises():
    with pytest.raises(SQLValidationError):
        validate_sql("")


def test_non_select_raises():
    with pytest.raises(SQLValidationError):
        validate_sql("UPDATE customers SET status = 'active'")
