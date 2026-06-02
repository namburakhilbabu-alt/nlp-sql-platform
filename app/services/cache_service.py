"""
Semantic caching using ChromaDB.
If a semantically similar question was asked before, return the cached SQL.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.core.logging_config import logger

CACHE_COLLECTION = "query_cache"
SIMILARITY_THRESHOLD = 0.92

_client = None
_cache_collection = None


def _get_cache():
    global _client, _cache_collection
    if _cache_collection is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        _cache_collection = _client.get_or_create_collection(
            name=CACHE_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
    return _cache_collection


def get_cached_sql(question: str) -> str | None:
    cache = _get_cache()
    if cache.count() == 0:
        return None
    try:
        results = cache.query(
            query_texts=[question],
            n_results=1,
            include=["metadatas", "distances"],
        )
        if not results["ids"][0]:
            return None
        distance = results["distances"][0][0]
        similarity = 1 - distance
        if similarity >= SIMILARITY_THRESHOLD:
            cached_sql = results["metadatas"][0][0].get("sql")
            logger.info(f"Cache HIT | similarity={similarity:.4f} | sql={cached_sql[:60]}...")
            return cached_sql
    except Exception as e:
        logger.warning(f"Cache lookup failed: {e}")
    return None


def cache_query(question: str, sql: str):
    cache = _get_cache()
    try:
        existing = cache.get(ids=[question[:100]])
        if existing["ids"]:
            return
        cache.add(
            ids=[question[:100]],
            documents=[question],
            metadatas=[{"sql": sql, "question": question}],
        )
        logger.info(f"Query cached: {question[:60]}")
    except Exception as e:
        logger.warning(f"Cache write failed: {e}")
