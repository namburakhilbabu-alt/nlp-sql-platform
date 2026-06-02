"""
Schema retrieval system using ChromaDB vector search.
Given a natural language question, finds the most relevant tables.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from database.enterprise_schema import SCHEMA_METADATA
from app.core.config import settings
from app.core.logging_config import logger


_client = None
_collection = None
COLLECTION_NAME = "schema_metadata"


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def get_relevant_tables(question: str, top_k: int = 5) -> list[dict]:
    collection = _get_collection()
    count = collection.count()
    if count == 0:
        logger.warning("Schema index is empty. Run database/schema_indexer.py first. Returning all tables.")
        return SCHEMA_METADATA

    results = collection.query(
        query_texts=[question],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"],
    )

    relevant = []
    for i, table_name in enumerate(results["ids"][0]):
        meta = results["metadatas"][0][i]
        distance = results["distances"][0][i]
        schema = next((t for t in SCHEMA_METADATA if t["table_name"] == table_name), None)
        if schema:
            relevant.append({**schema, "relevance_score": round(1 - distance, 4)})
        logger.debug(f"Schema match: {table_name} | score={1 - distance:.4f}")

    return relevant


def get_table_schema_text(tables: list[dict]) -> str:
    lines = []
    for table in tables:
        lines.append(f"\n-- Table: {table['table_name']}")
        lines.append(f"-- Description: {table['description']}")
        lines.append(f"-- Domain: {table['domain']}")
        cols = ", ".join(
            f"{c['name']} {c['type']}" + (" PK" if c.get("pk") else "") + (f" FK→{c.get('fk')}" if c.get("fk") else "")
            for c in table["columns"]
        )
        lines.append(f"CREATE TABLE {table['table_name']} ({cols});")
    return "\n".join(lines)


def get_all_table_names() -> list[str]:
    return [t["table_name"] for t in SCHEMA_METADATA]
