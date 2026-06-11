from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, Field

from src.tools.base import BaseTool


class WebSearchParams(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    num_results: int = Field(5, ge=1, le=20, description="Number of results")


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web using Google Search"
    parameters = WebSearchParams

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.api_key = self.config.get("api_key", "")
        self.search_engine_id = self.config.get("search_engine_id", "")

    async def execute(self, params: WebSearchParams) -> list[dict]:
        if self.api_key and self.search_engine_id:
            return await self._google_search(params.query, params.num_results)
        return await self._basic_search(params.query, params.num_results)

    async def _google_search(self, query: str, num: int) -> list[dict]:
        url = "https://www.googleapis.com/customsearch/v1"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                url,
                params={"key": self.api_key, "cx": self.search_engine_id, "q": query, "num": num},
            )
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", [])
            return [
                {"title": i.get("title"), "link": i.get("link"), "snippet": i.get("snippet")}
                for i in items
            ]

    async def _basic_search(self, query: str, num: int) -> list[dict]:
        url = "https://html.duckduckgo.com/html/"
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.post(url, data={"q": query})
            resp.raise_for_status()
        return [{"title": f"Results for: {query}", "link": "", "snippet": resp.text[:500]}]
