from fastapi import APIRouter, Query
from app.schema.schema_manager import get_relevant_tables, get_all_table_names, SCHEMA_METADATA

router = APIRouter()


@router.get("/schema/tables")
def list_tables():
    return {
        "total_tables": len(SCHEMA_METADATA),
        "tables": [
            {
                "table_name": t["table_name"],
                "description": t["description"],
                "domain": t["domain"],
                "column_count": len(t["columns"]),
            }
            for t in SCHEMA_METADATA
        ],
    }


@router.get("/schema/table/{table_name}")
def get_table_detail(table_name: str):
    table = next((t for t in SCHEMA_METADATA if t["table_name"] == table_name), None)
    if not table:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    return table


@router.get("/schema/search")
def search_schema(q: str = Query(..., description="Natural language query to find relevant tables")):
    tables = get_relevant_tables(q, top_k=5)
    return {
        "query": q,
        "relevant_tables": [
            {
                "table_name": t["table_name"],
                "description": t["description"],
                "domain": t["domain"],
                "relevance_score": t.get("relevance_score", 0),
            }
            for t in tables
        ],
    }
