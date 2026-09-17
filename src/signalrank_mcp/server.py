from mcp.server import MCPServer

from signalrank_mcp.client import SignalRankClient, SignalRankFeatureUnavailable
from signalrank_mcp.models import (
    CounterEvidenceResponse,
    EvidenceLedger,
    FeatureUnavailable,
    SearchResponse,
)
from signalrank_mcp.settings import Settings

mcp = MCPServer("SignalRank MCP")


def _client() -> SignalRankClient:
    # Intentionally constructed per call for v0.1. This keeps lifecycle behavior
    # simple across stdio and HTTP transports. We can pool it later if profiling
    # shows connection setup matters.
    return SignalRankClient(Settings.from_env())


@mcp.tool()
async def search(
    query: str,
    mode: str = "hybrid",
    top_k: int = 5,
) -> SearchResponse:
    """Search SignalRank and return ranked evidence without LLM synthesis."""
    client = _client()
    try:
        return await client.search(query, mode=mode, top_k=top_k)
    finally:
        await client.aclose()


@mcp.tool()
async def retrieve_counter_evidence(
    claim: str,
    top_k: int = 5,
) -> CounterEvidenceResponse | FeatureUnavailable:
    """Retrieve evidence that challenges a claim and return its evidence-ledger ID."""
    client = _client()
    try:
        try:
            return await client.retrieve_counter_evidence(claim, top_k=top_k)
        except SignalRankFeatureUnavailable as exc:
            return FeatureUnavailable(
                feature="counter-evidence retrieval",
                message=str(exc),
            )
    finally:
        await client.aclose()


@mcp.tool()
async def get_evidence_ledger(
    ledger_id: str,
) -> EvidenceLedger | FeatureUnavailable:
    """Read the support/counter/unresolved evidence ledger for a prior claim."""
    client = _client()
    try:
        try:
            return await client.get_evidence_ledger(ledger_id)
        except SignalRankFeatureUnavailable as exc:
            return FeatureUnavailable(
                feature="evidence ledger",
                message=str(exc),
            )
    finally:
        await client.aclose()


@mcp.resource(
    "signalrank://ledger/{ledger_id}",
    mime_type="application/json",
)
async def evidence_ledger_resource(
    ledger_id: str,
) -> dict[str, object]:
    """Address an evidence ledger as an MCP resource."""
    result = await get_evidence_ledger(ledger_id)
    return result.model_dump(mode="json")


def main() -> None:
    settings = Settings.from_env()

    if settings.transport == "streamable-http":
        mcp.run(transport="streamable-http", json_response=True)
        return

    if settings.transport != "stdio":
        raise ValueError(
            "SIGNALRANK_MCP_TRANSPORT must be 'stdio' or 'streamable-http'"
        )

    mcp.run()


if __name__ == "__main__":
    main()
