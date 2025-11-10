from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from auth import auth_calendar


def get_calendar_service():
    """Initialize and return a Google Calendar API service."""
    return auth_calendar()


def list_upcoming_events(max_results=10):
    """List the next N upcoming events from the primary calendar."""
    try:
        service = get_calendar_service()
        now = datetime.utcnow().isoformat() + "Z"
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return []

        return events

    except HttpError as error:
        return {"error": str(error)}


def create_event(summary, start_time, duration_minutes=60, description=None, location=None):
    """Create a calendar event with the given details."""
    try:
        service = get_calendar_service()
        start_dt = datetime.fromisoformat(start_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)

        event = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()
        # Return the event without printing (avoids encoding issues)
        return {"event": created_event}

    except HttpError as error:
        return {"error": str(error)}


def delete_event(event_id):
    """Delete an event from the primary calendar by its event ID."""
    try:
        service = get_calendar_service()
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return {"status": "deleted"}
    except HttpError as error:
        return {"error": str(error)}