from typing import Any

import httpx


class LLMClient:
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._http_client = http_client

    async def post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = await self._http_client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
