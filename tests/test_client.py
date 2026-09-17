from __future__ import annotations

import httpx
import pytest

from signalrank_mcp.client import SignalRankClient
from signalrank_mcp.settings import Settings


def settings() -> Settings:
    return Settings(
        api_url="http://signalrank.test",
        service_token="test-token",
        retrieve_path="/retrieve",
    )


@pytest.mark.asyncio
async def test_search_preserves_signalrank_response() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-SignalRank-Service-Token"] == "test-token"
        assert request.url.path == "/retrieve"

        return httpx.Response(
            200,
            json={
                "query": "counter-evidence",
                "mode": "hybrid",
                "results": [
                    {
                        "chunk_id": "chunk-001",
                        "doc_id": "doc-001",
                        "text": "Counter-evidence was absent from the exposed context.",
                        "score": 0.91,
                        "rank": 1,
                        "source_path": "papers/paper-01.txt",
                        "metadata": {
                            "source": "paper-01",
                        },
                    }
                ],
            },
        )

    client = SignalRankClient(
        settings(),
        transport=httpx.MockTransport(handler),
    )

    try:
        result = await client.search(
            "counter-evidence",
            mode="hybrid",
            top_k=5,
        )
    finally:
        await client.aclose()

    assert result.query == "counter-evidence"
    assert result.mode == "hybrid"

    item = result.results[0]

    assert item.chunk_id == "chunk-001"
    assert item.doc_id == "doc-001"
    assert item.source_path == "papers/paper-01.txt"
    assert item.text.startswith("Counter-evidence")
    assert item.score == pytest.approx(0.91)
    assert item.rank == 1


@pytest.mark.asyncio
async def test_search_rejects_invalid_signalrank_response() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "query": "test",
                "mode": "hybrid",
                "results": [
                    {
                        "text": "Missing provenance fields",
                        "score": 0.8,
                        "rank": 1,
                    }
                ],
            },
        )

    client = SignalRankClient(
        settings(),
        transport=httpx.MockTransport(handler),
    )

    try:
        with pytest.raises(ValueError):
            await client.search("test")
    finally:
        await client.aclose()