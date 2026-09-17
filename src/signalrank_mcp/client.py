import httpx

from signalrank_mcp.models import RetrievalMode, SearchResponse
from signalrank_mcp.settings import Settings


class SignalRankClient:
    def __init__(
        self,
        settings: Settings,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.settings = settings
        self._client = httpx.AsyncClient(
            base_url=settings.api_url,
            headers={
                "X-SignalRank-Service-Token": settings.service_token,
            },
            timeout=httpx.Timeout(30.0),
            transport=transport,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def search(
        self,
        query: str,
        *,
        mode: RetrievalMode = "dense",
        top_k: int = 5,
    ) -> SearchResponse:
        response = await self._client.post(
            self.settings.retrieve_path,
            json={
                "query": query,
                "mode": mode,
                "top_k": top_k,
            },
        )
        response.raise_for_status()

        return SearchResponse.model_validate(response.json())