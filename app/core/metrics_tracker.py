"""
In-memory metrics tracker for monitoring dashboard.
Tracks query counts, latency, cache hits, intent distribution, errors.
"""
from collections import defaultdict
from datetime import datetime
import threading

_lock = threading.Lock()

_metrics = {
    "total_queries": 0,
    "successful_queries": 0,
    "failed_queries": 0,
    "cache_hits": 0,
    "chat_intents": 0,
    "data_intents": 0,
    "total_latency_ms": 0,
    "started_at": datetime.utcnow().isoformat(),
    "recent_queries": [],   # last 20
    "errors": [],           # last 10 errors
}


def record_query(question: str, intent: str, success: bool,
                 latency_ms: int, from_cache: bool = False, error: str = None):
    with _lock:
        _metrics["total_queries"] += 1
        _metrics["total_latency_ms"] += latency_ms

        if success:
            _metrics["successful_queries"] += 1
        else:
            _metrics["failed_queries"] += 1
            if error:
                _metrics["errors"].append({
                    "time": datetime.utcnow().isoformat(),
                    "question": question[:80],
                    "error": error[:200],
                })
                _metrics["errors"] = _metrics["errors"][-10:]

        if from_cache:
            _metrics["cache_hits"] += 1

        if intent == "chat":
            _metrics["chat_intents"] += 1
        else:
            _metrics["data_intents"] += 1

        _metrics["recent_queries"].append({
            "time": datetime.utcnow().strftime("%H:%M:%S"),
            "question": question[:60],
            "intent": intent,
            "success": success,
            "latency_ms": latency_ms,
            "cached": from_cache,
        })
        _metrics["recent_queries"] = _metrics["recent_queries"][-20:]


def get_metrics() -> dict:
    with _lock:
        total = _metrics["total_queries"] or 1
        return {
            **_metrics,
            "avg_latency_ms": round(_metrics["total_latency_ms"] / total),
            "success_rate_pct": round(_metrics["successful_queries"] * 100 / total, 1),
            "cache_hit_rate_pct": round(_metrics["cache_hits"] * 100 / total, 1),
        }
