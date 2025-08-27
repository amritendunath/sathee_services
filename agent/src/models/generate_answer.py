from pydantic import BaseModel
from typing import Optional

class ErrorResponse(BaseModel):
    error: str
    detail: str


class GenerationRequest(BaseModel):
    query: str
    queryModeType: str


class GenerationResponse(BaseModel):
    answer: str
    session_id: str
    # dialog_state: str

class GraphResponse(BaseModel):
    thread_id: str
    answer: Optional[str] = None

class StartRequest(BaseModel):
    query: str
    queryModeType: str