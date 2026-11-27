"""
The semantic cache must not reuse SQL when a question changes a constraint
(number, time window, comparison direction or status), even if the embeddings
say the questions are ~95% similar.
Run: pytest tests/ -v
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.cache_guard import constraints_match  # noqa: E402

CACHED_QUARTER = "Show unpaid invoices above 5 lakhs from last quarter"
CACHED_PLAIN = "unpaid invoices above 5 lakhs"


@pytest.mark.parametrize("question, cached", [
    ("show unpaid invoices above 5 lakhs", CACHED_PLAIN),
    ("list unpaid invoices over 5 lakhs", CACHED_PLAIN),
    ("unpaid invoices above 5 lakhs last quarter", CACHED_QUARTER),
    ("Show unpaid invoices above 5 lakhs from last quarter", CACHED_QUARTER),
])
def test_same_constraints_reuse_cache(question, cached):
    assert constraints_match(question, cached)


@pytest.mark.parametrize("question, cached", [
    ("show unpaid invoices above 5 lakhs", CACHED_QUARTER),                  # time window dropped
    ("show unpaid invoices above 5 lakhs from last month", CACHED_QUARTER),  # different window
    ("show unpaid invoices above 5 lakhs this year", CACHED_QUARTER),
    ("unpaid invoices above 5 lakhs last quarter", CACHED_PLAIN),            # window added
    ("show unpaid invoices above 10 lakhs", CACHED_PLAIN),                   # different amount
    ("show unpaid invoices below 5 lakhs", CACHED_PLAIN),                    # opposite direction
    ("show paid invoices above 5 lakhs", CACHED_PLAIN),                      # different status
    ("unpaid invoices above 5 crores", CACHED_PLAIN),                        # different unit
    ("top 5 vendors by payment delays", "Top 10 vendors by payment delays"),
])
def test_changed_constraints_skip_cache(question, cached):
    assert not constraints_match(question, cached)
