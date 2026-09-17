# Architecture

SignalRank MCP is a protocol adapter.

```text
┌──────────────────────┐
│ MCP host             │
│ Claude / IDE / agent │
└──────────┬───────────┘
           │ MCP
           ▼
┌──────────────────────┐
│ SignalRank MCP       │
│                      │
│ search               │
└──────────┬───────────┘
           │ HTTP + service token
           ▼
┌──────────────────────┐
│ SignalRank-RAG       │
│                      │
│ SearchService        │
│ reranking            │
│ counter-evidence     │
│ evidence ledger      │
└──────────────────────┘
```
