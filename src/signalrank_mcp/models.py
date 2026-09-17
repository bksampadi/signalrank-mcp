from typing import Literal

from pydantic import BaseModel, ConfigDict

RetrievalMode = Literal["bm25", "dense", "hybrid"]


class SearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    doc_id: str
    text: str
    score: float
    rank: int
    source_path: str
    metadata: dict[str, object]


class SearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    mode: RetrievalMode
    results: list[SearchResult]