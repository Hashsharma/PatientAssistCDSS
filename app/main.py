from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .guardrails import check_input_safety
from .generation import generate_response
from .audit import log_interaction

app = FastAPI(title="Local Medical CDSS")

class QueryRequest(BaseModel):
    patient_id: str
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: list
    latency_ms: float


@app.post("/clinical/query", response_model=QueryResponse)
async def clinical_query(request: QueryRequest):
    # Guarrail Input
    is_safe, message = check_input_safety(request.query)
    if not is_safe:
        return HTTPException(status_code=400, detail=message)
    
    try:
        answer, docs, latency = generate_response(request.query)

        # Audit Logs
        sources = [d.metadata for d in docs]
        log_interaction(request.query, answer, sources, latency)

        return QueryResponse(answer=answer, sources=sources, latency_ms=latency)
    
    except Exception as e:
        log_interaction(request.query, f"ERROR: {str(e)}", [], 0)
        raise HTTPException(status_code=500, detail=str(e))