import urllib.parse
from aiohttp import ClientSession, ClientResponseError
import feedparser
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("News-MCP-User")

def _normalize_entries(entries):
    out = []
    for e in entries or []:
        # Some RSS items may miss a few fields; guard accordingly
        source = getattr(e, "source", None)
        source_name = source.get("title") if isinstance(source, dict) else "Google News"
        out.append({
            "title": getattr(e, "title", "").strip(),
            "source": source_name or "Google News",
            "url": getattr(e, "link", None),
            "publishedAt": getattr(e, "published", None),
            "description": getattr(e, "summary", None),
        })
    return out

async def _fetch_rss(query: str, hl: str, gl: str, ceid: str):
    """
    Fetch Google News RSS with aiohttp and parse with feedparser.
    No API key required.
    """
    qs = urllib.parse.urlencode({"q": query, "hl": hl, "gl": gl, "ceid": ceid})
    url = f"https://news.google.com/rss/search?{qs}"

    async with ClientSession() as session:
        async with session.get(url) as resp:
            try:
                resp.raise_for_status()
            except ClientResponseError:
                text = await resp.text()
                return {"error": f"HTTP {resp.status}", "details": text, "via": "google-news-rss"}
            # Read the raw feed text and parse
            data = await resp.read()
            feed = feedparser.parse(data)
            entries = feed.entries if hasattr(feed, "entries") else []
            articles = _normalize_entries(entries)
            return {
                "total": len(articles),
                "articles": articles,
                "via": "google-news-rss",
            }

@mcp.tool()
async def get_latest_news_about(query: str,
                                max_results: int = 10,
                                hl: str = "en-US",
                                gl: str = "US",
                                ceid: str = "US:en"):
    """
    Get latest news about {user input} using Google News RSS (free, no API key).
    Args:
      - query: your topic text (e.g., "Apple", "FSU football", "NVIDIA GPUs")
      - max_results: limit number of articles returned (default 10)
      - hl: interface language (default en-US)
      - gl: country code (default US)
      - ceid: edition code (default US:en)
    Returns:
      { total, articles: [ {title, source, url, publishedAt, description} ], via }
    """
    q = (query or "").strip()
    if not q:
        return {"error": "Provide a non-empty 'query'."}

    payload = await _fetch_rss(q, hl, gl, ceid)
    if payload.get("error"):
        return payload

    # apply max_results trimming here to keep transport light
    n = max(1, min(int(max_results), 50))
    payload["articles"] = payload.get("articles", [])[:n]
    payload["total"] = len(payload["articles"])
    return payload

if __name__ == "__main__":
    mcp.run(transport="stdio")
