from __future__ import annotations

from typing import Any

import httpx

from .models import (
    CounterEvidenceResponse,
    EvidenceItem,
    EvidenceLedger,
    SearchResponse,
)
from .settings import Settings


class SignalRankFeatureUnavailable(RuntimeError):
    """SignalRank deployment does not expose the requested capability."""


class SignalRankClient:
    """Thin async client over the SignalRank service boundary."""

    def __init__(
        self,
        settings: Settings,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.settings = settings
        self._client = httpx.AsyncClient(
            base_url=settings.api_url,
            headers={"X-SignalRank-Service-Token": settings.service_token},
            timeout=httpx.Timeout(30.0),
            transport=transport,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def search(
        self,
        query: str,
        *,
        mode: str = "hybrid",
        top_k: int = 5,
    ) -> SearchResponse:
        response = await self._client.post(
            self.settings.retrieve_path,
            json={"query": query, "mode": mode, "top_k": top_k},
        )
        response.raise_for_status()
        payload = response.json()
        results = _normalize_results(payload)

        return SearchResponse(
            query=query,
            mode=mode,
            results=results[:top_k],
            total=len(results),
        )

    async def retrieve_counter_evidence(
        self,
        claim: str,
        *,
        top_k: int = 5,
    ) -> CounterEvidenceResponse:
        response = await self._client.post(
            self.settings.counter_evidence_path,
            json={"claim": claim, "top_k": top_k},
        )
        _raise_if_feature_missing(response, "counter-evidence retrieval")
        response.raise_for_status()
        payload = response.json()

        return CounterEvidenceResponse(
            claim=str(payload.get("claim", claim)),
            ledger_id=str(payload["ledger_id"]),
            support_count=int(payload.get("support_count", 0)),
            counter_count=int(payload.get("counter_count", 0)),
            unresolved_count=int(payload.get("unresolved_count", 0)),
            counter_evidence=_normalize_results(
                payload.get("counter_evidence", payload.get("counter", []))
            )[:top_k],
        )

    async def get_evidence_ledger(self, ledger_id: str) -> EvidenceLedger:
        path = self.settings.ledger_path.format(ledger_id=ledger_id)
        response = await self._client.get(path)
        _raise_if_feature_missing(response, "evidence ledger")
        response.raise_for_status()
        payload = response.json()

        return EvidenceLedger(
            ledger_id=str(payload.get("ledger_id", ledger_id)),
            claim=str(payload.get("claim", "")),
            support=_normalize_results(payload.get("support", [])),
            counter=_normalize_results(payload.get("counter", [])),
            unresolved=_normalize_results(payload.get("unresolved", [])),
            metadata=_metadata(payload),
        )


def _raise_if_feature_missing(response: httpx.Response, feature: str) -> None:
    if response.status_code in {404, 405, 501}:
        raise SignalRankFeatureUnavailable(
            f"{feature} is not exposed by this SignalRank deployment yet "
            f"(HTTP {response.status_code})."
        )


def _normalize_results(payload: Any) -> list[EvidenceItem]:
    if isinstance(payload, list):
        raw_results = payload
    elif isinstance(payload, dict):
        raw_results = (
            payload.get("results")
            or payload.get("evidence")
            or payload.get("items")
            or []
        )
    else:
        raw_results = []

    if not isinstance(raw_results, list):
        return []

    return [
        _normalize_item(item, rank=index)
        for index, item in enumerate(raw_results, start=1)
        if isinstance(item, dict)
    ]


def _normalize_item(item: dict[str, Any], *, rank: int) -> EvidenceItem:
    metadata = item.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    text = (
        item.get("text")
        or item.get("content")
        or item.get("chunk_text")
        or item.get("document")
        or ""
    )
    source = (
        item.get("source")
        or item.get("document_id")
        or item.get("path")
        or metadata.get("source")
        or metadata.get("document_id")
        or metadata.get("path")
    )
    score = _first_float(
        item.get("score"),
        item.get("rerank_score"),
        item.get("relevance_score"),
    )

    return EvidenceItem(
        rank=int(item.get("rank", rank)) if str(item.get("rank", rank)).isdigit() else rank,
        score=score,
        text=str(text),
        source=str(source) if source is not None else None,
        metadata=metadata,
    )


def _first_float(*values: Any) -> float | None:
    for value in values:
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _metadata(payload: dict[str, Any]) -> dict[str, Any]:
    metadata = payload.get("metadata")
    return metadata if isinstance(metadata, dict) else {}
