from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_url: str
    service_token: str
    retrieve_path: str
    counter_evidence_path: str
    ledger_path: str
    transport: str

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            api_url=os.getenv("SIGNALRANK_API_URL", "http://127.0.0.1:8000").rstrip("/"),
            service_token=os.getenv(
                "SIGNALRANK_SERVICE_TOKEN",
                "signalrank-local-dev",
            ),
            retrieve_path=os.getenv("SIGNALRANK_RETRIEVE_PATH", "/retrieve"),
            counter_evidence_path=os.getenv(
                "SIGNALRANK_COUNTER_EVIDENCE_PATH",
                "/counter-evidence",
            ),
            ledger_path=os.getenv(
                "SIGNALRANK_LEDGER_PATH",
                "/evidence-ledgers/{ledger_id}",
            ),
            transport=os.getenv("SIGNALRANK_MCP_TRANSPORT", "stdio"),
        )
