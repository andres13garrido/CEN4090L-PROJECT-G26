import os
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv, find_dotenv
from aiohttp import ClientSession, ClientResponseError
from mcp.server.fastmcp import FastMCP

load_dotenv(find_dotenv())  # finds News-MCP/.env

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_BASE = "https://newsapi.org/v2"

mcp = FastMCP("News-MCP")

def _iso_from_hours(hours: int) -> str:
    # NewsAPI expects ISO8601 with timezone; use UTC
    dt = datetime.now(timezone.utc) - timedelta(hours=max(1, int(hours)))
    return dt.isoformat(timespec="seconds")

def _normalize_articles(articles):
    # Keep it small + MCP-friendly
    out = []
    for a in articles or []:
        out.append({
            "title": a.get("title"),
            "source": (a.get("source") or {}).get("name"),
            "url": a.get("url"),
            "publishedAt": a.get("publishedAt"),
            "description": a.get("description"),
        })
    return out

async def _newsapi_get(session: ClientSession, path: str, params: dict):
    if not NEWS_API_KEY:
        return {"error": "Missing NEWS_API_KEY env var"}
    headers = {"X-Api-Key": NEWS_API_KEY}
    async with session.get(f"{NEWS_API_BASE}/{path}", headers=headers, params=params) as resp:
        try:
            resp.raise_for_status()
        except ClientResponseError:
            text = await resp.text()
            return {"error": f"HTTP {resp.status}", "details": text}
        return await resp.json()

@mcp.tool()
async def get_latest_news(query: str, hours: int = 24, max_results: int = 10, language: str = "en"):
    """
    Get recent articles about a topic from the last N hours (default 24).
    Returns a compact list with title, source, url, publishedAt, description.
    """
    try:
        if not query or not query.strip():
            return {"error": "Provide a non-empty 'query'."}

        params = {
            "q": query.strip(),
            "from": _iso_from_hours(hours),
            "sortBy": "publishedAt",
            "language": language,
            "pageSize": max(1, min(int(max_results), 100)),
        }
        async with ClientSession() as session:
            data = await _newsapi_get(session, "everything", params)
            if "error" in data:
                return data
            return {
                "total": data.get("totalResults"),
                "articles": _normalize_articles(data.get("articles")),
            }
    except Exception as e:
        return {"error": f"get_latest_news failed: {e}"}

@mcp.tool()
async def get_headlines(country: str = "us", category: str | None = None, max_results: int = 10):
    """
    Get top headlines by country and optional category (business, tech, sports, etc.).
    """
    try:
        params = {
            "country": country,
            "pageSize": max(1, min(int(max_results), 100)),
        }
        if category:
            params["category"] = category
        async with ClientSession() as session:
            data = await _newsapi_get(session, "top-headlines", params)
            if "error" in data:
                return data
            return {
                "total": data.get("totalResults"),
                "articles": _normalize_articles(data.get("articles")),
            }
    except Exception as e:
        return {"error": f"get_headlines failed: {e}"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
