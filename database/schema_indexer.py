"""
Indexes table schemas into ChromaDB using sentence-transformers embeddings.
Run this once after seeding: python database/schema_indexer.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.config import Settings as ChromaSettings
from database.enterprise_schema import SCHEMA_METADATA
from app.core.config import settings


def build_table_document(table: dict) -> str:
    col_descriptions = " | ".join(
        f"{c['name']}: {c.get('description', '')}"
        for c in table["columns"]
    )
    sample_qs = " | ".join(table.get("sample_questions", []))
    return (
        f"Table: {table['table_name']}. "
        f"Description: {table['description']}. "
        f"Domain: {table['domain']}. "
        f"Columns: {col_descriptions}. "
        f"Example questions: {sample_qs}"
    )


def index_schemas():
    client = chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )

    try:
        client.delete_collection("schema_metadata")
    except Exception:
        pass

    collection = client.create_collection(
        name="schema_metadata",
        metadata={"hnsw:space": "cosine"},
    )

    ids = []
    documents = []
    metadatas = []

    for table in SCHEMA_METADATA:
        doc = build_table_document(table)
        ids.append(table["table_name"])
        documents.append(doc)
        metadatas.append({
            "table_name": table["table_name"],
            "domain": table["domain"],
            "description": table["description"],
        })
        print(f"  Prepared: {table['table_name']}")

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    print(f"\nIndexed {len(ids)} tables into ChromaDB at '{settings.chroma_persist_dir}'")
    print("Schema index ready!")


if __name__ == "__main__":
    print("Building schema vector index...")
    index_schemas()
