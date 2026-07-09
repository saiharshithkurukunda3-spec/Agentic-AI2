from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class SourceItem(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None
    relevance_score: Optional[float] = None

class HistoryBase(BaseModel):
    query: str
    response: str
    sources: List[SourceItem] = []

class HistoryCreate(HistoryBase):
    pass

class HistoryOut(HistoryBase):
    id: str = Field(..., alias="_id")
    user_id: str
    timestamp: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "60c72b2f9b1d8b2a1c8b4568",
                "user_id": "60c72b2f9b1d8b2a1c8b4567",
                "query": "Lightweight RAG benefits",
                "response": "VERITAS AI: Lightweight RAG reduces memory overhead by keeping indexing in memory...",
                "sources": [
                    {
                        "title": "RAG Architectures",
                        "url": "https://example.com/rag",
                        "snippet": "RAG has massive storage requirements unless keeping text chunks transient...",
                        "relevance_score": 0.95
                    }
                ],
                "timestamp": "2026-07-09T12:05:00Z"
            }
        }
    )
