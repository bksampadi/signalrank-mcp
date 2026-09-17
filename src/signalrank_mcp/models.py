from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """Normalized evidence returned by SignalRank."""

    rank: int | None = None
    score: float | None = None
    text: str
    source: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """MCP-facing search result."""

    query: str
    mode: str
    results: list[EvidenceItem]
    total: int


class CounterEvidenceResponse(BaseModel):
    """Counter-evidence retrieval result with a persisted ledger reference."""

    claim: str
    ledger_id: str
    support_count: int
    counter_count: int
    unresolved_count: int
    counter_evidence: list[EvidenceItem] = Field(default_factory=list)


class EvidenceLedger(BaseModel):
    """Evidence ledger for one claim."""

    ledger_id: str
    claim: str
    support: list[EvidenceItem] = Field(default_factory=list)
    counter: list[EvidenceItem] = Field(default_factory=list)
    unresolved: list[EvidenceItem] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class FeatureUnavailable(BaseModel):
    """Returned when a SignalRank deployment does not yet expose a capability."""

    available: bool = False
    feature: str
    message: str
