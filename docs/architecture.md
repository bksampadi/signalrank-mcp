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
│ counter-evidence     │
│ ledger               │
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
