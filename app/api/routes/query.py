from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from app.services.query_service import run_query
from app.llm.intent_classifier import classify_intent, generate_chat_response
from app.llm.gemini_client import generate_with_retry
from app.services.conversation_service import get_history, clear_session, add_turn
from app.core.metrics_tracker import record_query
from app.core.logging_config import logger
import httpx, json
from app.core.config import settings

router = APIRouter()


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = Field(default="default")


class QueryResponse(BaseModel):
    question: str
    intent: str                          # "data" or "chat"
    answer: Optional[str] = None         # chat reply (intent=chat)
    sql: Optional[str] = None            # generated SQL (intent=data)
    data: Optional[list[dict]] = None    # query results (intent=data)
    row_count: int = 0
    explanation: Optional[str] = None
    relevant_tables: list[str] = []
    from_cache: bool = False
    confidence_score: float = 1.0
    execution_time_ms: int = 0


@router.post("/query", response_model=QueryResponse)
def ask_question(req: QueryRequest):
    session = req.session_id or "default"
    question = req.question.strip()

    try:
        intent = classify_intent(question)

        if intent == "chat":
            answer = generate_chat_response(question)
            add_turn(session, question, sql="", result_count=0, explanation=answer)
            record_query(question, "chat", True, 0)
            return QueryResponse(
                question=question,
                intent="chat",
                answer=answer,
            )

        # DATA path — full pipeline
        result = run_query(question, session_id=session)
        record_query(question, "data", True, result.execution_time_ms, result.from_cache)
        return QueryResponse(
            question=result.question,
            intent="data",
            sql=result.sql,
            data=result.data,
            row_count=result.row_count,
            explanation=result.explanation,
            relevant_tables=result.relevant_tables,
            from_cache=result.from_cache,
            confidence_score=result.confidence,
            execution_time_ms=result.execution_time_ms,
        )

    except RuntimeError as e:
        record_query(question, intent, False, 0, error=str(e))
        logger.error(f"Query pipeline failed: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        record_query(question, intent, False, 0, error=str(e))
        logger.error(f"Unexpected error in /query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Check logs.")


@router.get("/query/history/{session_id}")
def get_conversation_history(session_id: str):
    history = get_history(session_id)
    return {"session_id": session_id, "turns": len(history), "history": history}


@router.delete("/query/session/{session_id}")
def reset_session(session_id: str):
    clear_session(session_id)
    return {"message": f"Session '{session_id}' cleared."}


@router.post("/query/stream")
def stream_query(req: QueryRequest):
    """Streaming endpoint — returns Server-Sent Events (SSE) as Ollama generates tokens."""
    def generate():
        prompt = f"Answer this business question concisely: {req.question}"
        try:
            with httpx.stream("POST", f"{settings.ollama_base_url}/api/generate",
                              json={"model": settings.ollama_model, "prompt": prompt, "stream": True},
                              timeout=120.0) as r:
                for line in r.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        yield f"data: {json.dumps({'token': token})}\n\n"
                        if chunk.get("done"):
                            yield "data: [DONE]\n\n"
                            break
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
