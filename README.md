# SignalRank MCP

**MCP interface for SignalRank retrieval.**

SignalRank MCP is a thin interoperability layer over
[SignalRank-RAG](https://github.com/bksampadi/SignalRank-RAG).

It exposes SignalRank retrieval to MCP-compatible clients without duplicating retrieval or ranking logic.

```text
MCP client / host
       │
       ▼
SignalRank MCP
       │  authenticated HTTP
       ▼
SignalRank-RAG
```

## Tool

### `search`

Search SignalRank and return ranked evidence with provenance.

```text
search(query, mode="dense", top_k=5)
```

Supported retrieval modes:

```text
bm25
dense
hybrid
```

Results preserve:

```text
chunk_id
doc_id
text
score
rank
source_path
metadata
```

## Install

```bash
git clone https://github.com/bksampadi/signalrank-mcp.git
cd signalrank-mcp
uv sync --extra dev
```

## Environment

SignalRank-RAG must be running.

Set the same service token for SignalRank-RAG and SignalRank MCP:

```text
SIGNALRANK_SERVICE_TOKEN=signalrank-local-dev
```

SignalRank-RAG also requires:

```text
GROQ_API_KEY=<your-groq-api-key>
```

SignalRank MCP defaults to:

```text
SIGNALRANK_API_URL=http://127.0.0.1:8000
```

Do not commit API keys or production service tokens.

## Run

Start SignalRank-RAG:

```bash
uv run uvicorn signalrank.api.main:app --host 127.0.0.1 --port 8000
```

Run with MCP Inspector:

```bash
uv run mcp dev src/signalrank_mcp/server.py --with-editable .
```

Or run directly over stdio:

```bash
uv run signalrank-mcp
```

## Claude Code

Register the server:

```bash
claude mcp add --env SIGNALRANK_SERVICE_TOKEN=signalrank-local-dev --transport stdio signalrank -- uv run signalrank-mcp
```

Check the connection:

```bash
claude mcp get signalrank
```

## Test

```bash
uv run pytest -q
uv run ruff check .
uv run pyright
```

Tested end-to-end with MCP Inspector and Claude Code.

## License

MIT