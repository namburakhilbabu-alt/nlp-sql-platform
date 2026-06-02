from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.core.metrics_tracker import get_metrics
from app.schema.schema_graph import get_graph_summary
import json

router = APIRouter()


@router.get("/metrics")
def monitoring_dashboard():
    m = get_metrics()
    g = get_graph_summary()
    return {
        "platform": "NLP-SQL Platform v1.0",
        "uptime_since": m["started_at"],
        "queries": {
            "total": m["total_queries"],
            "successful": m["successful_queries"],
            "failed": m["failed_queries"],
            "success_rate_pct": m["success_rate_pct"],
        },
        "performance": {
            "avg_latency_ms": m["avg_latency_ms"],
            "cache_hits": m["cache_hits"],
            "cache_hit_rate_pct": m["cache_hit_rate_pct"],
        },
        "intent_distribution": {
            "data_queries": m["data_intents"],
            "chat_messages": m["chat_intents"],
        },
        "schema_graph": g,
        "recent_queries": m["recent_queries"],
        "recent_errors": m["errors"],
    }
