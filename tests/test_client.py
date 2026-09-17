from __future__ import annotations

import httpx
import pytest

from signalrank_mcp.client import SignalRankClient, SignalRankFeatureUnavailable
from signalrank_mcp.settings import Settings


def settings() -> Settings:
    return Settings(
        api_url="http://signalrank.test",
        service_token="test-token",
        retrieve_path="/retrieve",
        counter_evidence_path="/counter-evidence",
        ledger_path="/evidence-ledgers/{ledger_id}",
        transport="stdio",
    )


@pytest.mark.asyncio
async def test_search_normalizes_signalrank_results() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-SignalRank-Service-Token"] == "test-token"
        assert request.url.path == "/retrieve"
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "content": "Counter-evidence was absent from the exposed context.",
                        "rerank_score": 0.91,
                        "metadata": {"source": "paper-01"},
                    }
                ]
            },
        )

    client = SignalRankClient(
        settings(),
        transport=httpx.MockTransport(handler),
    )
    try:
        result = await client.search("counter-evidence", top_k=5)
    finally:
        await client.aclose()

    assert result.query == "counter-evidence"
    assert result.total == 1
    assert result.results[0].text.startswith("Counter-evidence")
    assert result.results[0].source == "paper-01"
    assert result.results[0].score == pytest.approx(0.91)


@pytest.mark.asyncio
async def test_counter_evidence_feature_gate_is_explicit() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Not Found"})

    client = SignalRankClient(
        settings(),
        transport=httpx.MockTransport(handler),
    )
    try:
        with pytest.raises(SignalRankFeatureUnavailable):
            await client.retrieve_counter_evidence("claim")
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_ledger_normalizes_three_evidence_classes() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/evidence-ledgers/ledger-123"
        return httpx.Response(
            200,
            json={
                "ledger_id": "ledger-123",
                "claim": "A claim",
                "support": [{"text": "supports", "score": 0.8}],
                "counter": [{"text": "challenges", "score": 0.7}],
                "unresolved": [{"text": "ambiguous"}],
                "metadata": {"retrieval_mode": "hybrid"},
            },
        )

    client = SignalRankClient(
        settings(),
        transport=httpx.MockTransport(handler),
    )
    try:
        ledger = await client.get_evidence_ledger("ledger-123")
    finally:
        await client.aclose()

    assert ledger.ledger_id == "ledger-123"
    assert len(ledger.support) == 1
    assert len(ledger.counter) == 1
    assert len(ledger.unresolved) == 1
    assert ledger.metadata["retrieval_mode"] == "hybrid"
