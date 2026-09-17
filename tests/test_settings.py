from __future__ import annotations

from signalrank_mcp.settings import Settings


def test_defaults(monkeypatch) -> None:
    for name in (
        "SIGNALRANK_API_URL",
        "SIGNALRANK_SERVICE_TOKEN",
        "SIGNALRANK_RETRIEVE_PATH",
        "SIGNALRANK_MCP_TRANSPORT",
    ):
        monkeypatch.delenv(name, raising=False)

    value = Settings.from_env()

    assert value.api_url == "http://127.0.0.1:8000"
    assert value.retrieve_path == "/retrieve"