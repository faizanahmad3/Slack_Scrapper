from typing import List, Optional

from pydantic import BaseModel, Field


class QARequest(BaseModel):
    channel: str = Field(..., description="Slack channel name, used as Qdrant collection")
    query: str = Field(..., description="User question")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of context chunks to retrieve")
    refresh: bool = Field(default=False, description="If true, ingest new messages before answering")
    force_full_refresh: bool = Field(default=False, description="If true with refresh, re-ingest entire channel")


class SourceDoc(BaseModel):
    text: str
    metadata: dict


class QAResponse(BaseModel):
    answer: str
    sources: List[SourceDoc]


class ChannelStatsResponse(BaseModel):
    channel: str
    last_timestamp: Optional[str] = None
    total_messages: int = 0
    last_updated: Optional[str] = None
