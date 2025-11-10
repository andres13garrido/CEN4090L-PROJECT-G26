import os
import json
import asyncio
from mcp.server.fastmcp import FastMCP

# Your modules
# Keep these imports exactly matching your structure
from gmailapi import send_email, search_emails, gmail_delete, gmail_list_unread, gmail_reply
from calendarapi import list_upcoming_events, create_event, delete_event
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

@mcp.tool()
async def gmail_delete_tool(message_id: str, permanent: bool = True) -> dict:
    """
    Delete a Gmail message.
    - permanent=True → permanently delete
    - permanent=False → move to Trash
    """
    return await asyncio.to_thread(gmail_delete, message_id, permanent)

@mcp.tool()
async def gmail_list_unread_tool(limit: int = 10, in_inbox: bool = True) -> dict:
    """
    List unread messages (optionally restricted to inbox).
    Returns message ID, thread ID, snippet, and headers (From, Subject, Date).
    """
    return await asyncio.to_thread(gmail_list_unread, limit, in_inbox)

@mcp.tool()
async def gmail_reply_tool(thread_id: str, body: str, html: bool = False, reply_all: bool = False) -> dict:
    """
    Reply to the latest message in a Gmail thread.
    - thread_id: ID of the conversation to reply to
    - body: reply text
    - html: set True for HTML body
    - reply_all: include original To/Cc recipients
    """
    return await asyncio.to_thread(gmail_reply, thread_id, body, html, reply_all)

@mcp.tool()
async def calendar_list_tool(limit: int = 10) -> dict:
    """
    List upcoming Google Calendar events.
    Args:
      limit: maximum number of events to retrieve (default 10)
    Returns:
      { "events": [ {id, summary, start, end, htmlLink, ...}, ... ] }
    """
    return await asyncio.to_thread(list_upcoming_events, limit)

@mcp.tool()
async def calendar_create_tool(summary: str, start_time: str, duration_minutes: int = 60,
                               description: str = None, location: str = None) -> dict:
    """
    Create a new calendar event.
    Args:
      summary: event title
      start_time: ISO 8601 start time (e.g. '2025-11-10T15:00:00')
      duration_minutes: length of the event in minutes
      description: optional event description
      location: optional event location
    Returns:
      { "event": {id, htmlLink, ...} }
    """
    return await asyncio.to_thread(
        create_event,
        summary,
        start_time,
        duration_minutes,
        description,
        location
    )

@mcp.tool()
async def calendar_delete_tool(event_id: str) -> dict:
    """
    Delete a Google Calendar event by ID.
    Args:
      event_id: the ID of the event to delete
    Returns:
      { "status": "deleted" } or { "error": {...} }
    """
    return await asyncio.to_thread(delete_event, event_id)

if __name__ == "__main__":
    # Claude/clients will connect via stdio
    mcp.run(transport="stdio")

