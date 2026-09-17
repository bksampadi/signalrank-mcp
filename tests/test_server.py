import httpx
import pytest
from mcp import Client
from mcp.types import CallToolResult

from signalrank_mcp.client import SignalRankClient
from signalrank_mcp.server import mcp
from signalrank_mcp.settings import Settings


@pytest.mark.asyncio
async def test_mcp_exposes_single_search_tool() -> None:
    async with Client(mcp, raise_exceptions=True) as client:
        result = await client.list_tools()

    assert len(result.tools) == 1

    tool = result.tools[0]
    assert tool.name == "search"

    properties = tool.input_schema["properties"]

    assert properties["mode"]["enum"] == ["bm25", "dense", "hybrid"]
    assert properties["mode"]["default"] == "dense"

    assert properties["top_k"]["minimum"] == 1
    assert properties["top_k"]["maximum"] == 10
    assert properties["top_k"]["default"] == 5

    assert properties["query"]["minLength"] == 1
    assert properties["query"]["maxLength"] == 500


@pytest.mark.asyncio
async def test_mcp_search_calls_signalrank(monkeypatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/retrieve"

        return httpx.Response(
            200,
            json={
                "query": "counter-evidence",
                "mode": "dense",
                "results": [
                    {
                        "chunk_id": "chunk-001",
                        "doc_id": "doc-001",
                        "text": "Evidence text.",
                        "score": 0.91,
                        "rank": 1,
                        "source_path": "papers/paper-01.txt",
                        "metadata": {},
                    }
                ],
            },
        )

    settings = Settings(
        api_url="http://signalrank.test",
        service_token="test-token",
        retrieve_path="/retrieve",
    )

    def mock_client() -> SignalRankClient:
        return SignalRankClient(
            settings,
            transport=httpx.MockTransport(handler),
        )

    monkeypatch.setattr(
        "signalrank_mcp.server._client",
        mock_client,
    )

    async with Client(mcp, raise_exceptions=True) as client:
        result = await client.call_tool(
            "search",
            {
                "query": "counter-evidence",
                "mode": "dense",
                "top_k": 5,
            },
        )

    assert isinstance(result, CallToolResult)
    assert result.is_error is False
    assert result.structured_content is not None

    structured = result.structured_content

    assert structured["query"] == "counter-evidence"
    assert structured["mode"] == "dense"

    item = structured["results"][0]

    assert item["chunk_id"] == "chunk-001"
    assert item["doc_id"] == "doc-001"
    assert item["source_path"] == "papers/paper-01.txt"