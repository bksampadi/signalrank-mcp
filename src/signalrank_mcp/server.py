from typing import Annotated

from mcp.server import MCPServer
from pydantic import Field, StringConstraints

from signalrank_mcp.client import SignalRankClient
from signalrank_mcp.models import RetrievalMode, SearchResponse
from signalrank_mcp.settings import Settings

mcp = MCPServer("SignalRank MCP")


Query = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=500,
    ),
]

TopK = Annotated[
    int,
    Field(
        ge=1,
        le=10,
    ),
]


def _client() -> SignalRankClient:
    return SignalRankClient(Settings.from_env())


@mcp.tool()
async def search(
    query: Query,
    mode: RetrievalMode = "dense",
    top_k: TopK = 5,
) -> SearchResponse:
    """Search SignalRank and return ranked evidence without LLM synthesis."""
    client = _client()
    try:
        return await client.search(query, mode=mode, top_k=top_k)
    finally:
        await client.aclose()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
