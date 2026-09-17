import os
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class Settings:
    api_url: str
    service_token: str
    retrieve_path: str

    @classmethod
    def from_env(cls) -> Self:
        return cls(
            api_url=os.getenv("SIGNALRANK_API_URL", "http://127.0.0.1:8000").rstrip("/"),
            service_token=os.getenv(
                "SIGNALRANK_SERVICE_TOKEN",
                "signalrank-local-dev",
            ),
            retrieve_path=os.getenv("SIGNALRANK_RETRIEVE_PATH", "/retrieve"),
        )
