import os
import json
import asyncio
from mcp.server.fastmcp import FastMCP

# Your modules
# Keep these imports exactly matching your structure
from gmailapi import send_email, search_emails  # uses tools.gmail.auth.auth_gmail internally

# Optional: .env support if you want GOOGLE_CREDENTIALS_FILE/GOOGLE_TOKEN_FILE
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

mcp = FastMCP("Gmail-Tools")

@mcp.tool()
async def gmail_send(to: str, subject: str, body: str, html: bool = False) -> dict:
    """
    Send an email via Gmail API.
    Args:
      to: recipient email address (single)
      subject: email subject
      body: email body (plain text unless html=True)
      html: set True if body is HTML
    Returns:
      { "id": "<messageId>" } or { "error": {...} }
    """
    # send_email is synchronous — run in thread
    return await asyncio.to_thread(send_email, to=to, subject=subject, body=body, html=html)

@mcp.tool()
async def gmail_search(query: str = "", limit: int = 10) -> dict:
    """
    Search emails via Gmail API.
    Args:
      query: Gmail search query (e.g., 'from:me is:unread newer_than:7d')
      limit: max results
    Returns:
      { "messages": [ {id, threadId, snippet, ...}, ... ] } or { "error": {...} }
    """
    return await asyncio.to_thread(search_emails, query=query, limit=limit)

if __name__ == "__main__":
    # Claude/clients will connect via stdio
    mcp.run(transport="stdio")

