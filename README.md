# SignalRank MCP

**MCP access to SignalRank retrieval, with interfaces for counter-evidence and evidence ledgers.**

SignalRank MCP is a thin interoperability layer over  
[SignalRank-RAG](https://github.com/bksampadi/SignalRank-RAG).

It exposes SignalRank's evidence system to MCP-compatible clients without moving retrieval or ranking logic into the MCP server.

```text
MCP client / host
       │
       ▼
SignalRank MCP
       │  authenticated HTTP
       ▼
SignalRank-RAG
```

## Tools

### `search`

Search SignalRank and return ranked evidence without LLM synthesis.

```text
search(query, mode="hybrid", top_k=5)
```

### `retrieve_counter_evidence`

Interface for retrieving evidence that challenges a claim and returning an evidence-ledger ID.

```text
retrieve_counter_evidence(claim, top_k=5)
```

### `get_evidence_ledger`

Interface for reading the support, counter, and unresolved evidence for a previous claim.

```text
get_evidence_ledger(ledger_id)
```

Evidence ledgers are also exposed as MCP resources:

```text
signalrank://ledger/{ledger_id}
```

## Status

```text
[x] MCP Python SDK v2
[x] SignalRank search
[x] typed structured outputs
[x] stdio
[x] HTTP client tests
[x] end-to-end MCP Inspector search
[ ] Streamable HTTP smoke test
[ ] counter-evidence service endpoint
[ ] evidence-ledger service endpoint
```

## Install

```bash
git clone https://github.com/bksampadi/signalrank-mcp.git
cd signalrank-mcp
uv sync --extra dev
```

## Environment

SignalRank MCP expects a running SignalRank-RAG service.

For local development, use any matching service token in both projects. For example:

```text
SIGNALRANK_SERVICE_TOKEN=signalrank-local-dev
```

SignalRank-RAG also requires your own Groq API key:

```text
GROQ_API_KEY=<your-groq-api-key>
```

SignalRank MCP optionally accepts:

```text
SIGNALRANK_API_URL=http://127.0.0.1:8000
```

Do not commit API keys or production service tokens.

## Run

### 1. Start SignalRank-RAG

Windows CMD:

```cmd
set SIGNALRANK_SERVICE_TOKEN=signalrank-local-dev
set GROQ_API_KEY=<your-groq-api-key>

uv run uvicorn signalrank.api.main:app --host 127.0.0.1 --port 8000
```

### 2. Start SignalRank MCP

In a separate terminal:

```cmd
set SIGNALRANK_SERVICE_TOKEN=signalrank-local-dev

uv run mcp dev src/signalrank_mcp/server.py --with-editable .
```

MCP Inspector will open in the browser.

### stdio

To run the MCP server directly over stdio:

```bash
uv run signalrank-mcp
```

## Test

```bash
uv run pytest -q
uv run ruff check .
uv run pyright
```

## License

MIT