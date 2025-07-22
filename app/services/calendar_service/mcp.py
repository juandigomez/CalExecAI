"""Calendar service for interacting with the MCP server."""

import datetime
import logging

from fastmcp import FastMCP

from .sdk import CalendarSDK
from .models import CalendarEvent


logger = logging.getLogger(__name__)

mcp = FastMCP(name="Calendar Management Service")

calendar_sdk = CalendarSDK(
    "credentials.json",
    "token.json",
    scopes=[
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
)

@mcp.resource(uri="events://future/{limit}")
def get_upcoming_events(limit: int):
    """Retrieve upcoming events.

    Args:
        limit: Number of events to retrieve

    Returns:
        List of calendar events
    """

    service = calendar_sdk.resource

    # Call the Calendar API
    events = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
            maxResults=limit,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    ).get("items", [])
    logger.info(f"[MCP] - Getting Upcoming Events: {events}")
    return [CalendarEvent(**event).model_dump_json() for event in events]


@mcp.resource(uri="events://{start_time_str}/{end_time_str}")
def get_events_between_dates(start_time_str: str, end_time_str: str):
    """Retrieve events between two timestamps.

    Args:
        start_time_str: Start of the time range (Format = "%Y-%m-%dT%H%M%S")
        end_time_str: End of the time range (Format = "%Y-%m-%dT%H%M%S")

    Returns:
        List of calendar events
    """

    input_date_format = "%Y-%m-%dT%H%M%S"
    output_date_format = "%Y-%m-%dT%H:%M:%SZ"

    service = calendar_sdk.resource

    start_time = datetime.datetime.strptime(start_time_str, input_date_format)
    end_time = datetime.datetime.strptime(end_time_str, input_date_format)

    # Call the Calendar API
    events = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=datetime.datetime.strftime(start_time, output_date_format),
            timeMax=datetime.datetime.strftime(end_time, output_date_format),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    ).get("items", [])
    logger.info(f"[MCP] - Getting Events Between Dates: {start_time} - {end_time}")
    return [CalendarEvent(**event).model_dump_json() for event in events]

@mcp.tool
def get_current_datetime() -> str:
    """
    Returns the current date and time in the format "YYYY-MM-DD HH:MM:SS".
    """
    logger.info("[MCP] - Getting Current Datetime")
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S%z")

@mcp.tool
def create_event(event: CalendarEvent) -> CalendarEvent:
    """Create a new event.

    Args:
        event: Calendar event object

    Returns:
        Calendar event object
    """

    service = calendar_sdk.resource

    # Call the Calendar API
    created = service.events().insert(
        calendarId="primary", 
        body=event.model_dump(exclude_none=True, exclude_defaults=True)
    ).execute()
    logger.info(f"[MCP] - Creating Event: {event.summary}")
    return CalendarEvent(**created)

@mcp.tool
def delete_event(event_id: str) -> None:
    """Delete an event.

    Args:
        event_id: ID of the event to delete

    Returns:
        Calendar event object
    """

    service = calendar_sdk.resource

    # Call the Calendar API
    try:
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        logger.info(f"[MCP] - Deleted Event: {event_id}")
    except Exception as e:
        logger.error(f"[MCP] - Error deleting event: {event_id}")
        logger.error(f"[MCP] - {e}")
        raise e
    
@mcp.tool
def update_event(event_id: str,event: CalendarEvent) -> CalendarEvent:
    """Update an event.

    Args:
        event_id: ID of the event to update
        event: Calendar event object

    Returns:
        Calendar event object
    """

    service = calendar_sdk.resource

    try:
        # Call the Calendar API
        updated = service.events().update(
            calendarId="primary", 
            eventId=event_id, 
            body=event.model_dump(exclude_none=True, exclude_defaults=True)
        ).execute()
        logger.info(f"[MCP] - Updated Event: {event.summary}")
        return CalendarEvent(**updated)
    except Exception as e:
        logger.error(f"[MCP] - Error updating event: {event_id}")
        logger.error(f"[MCP] - {e}")
        raise e

if __name__ == "__main__":
    mcp.run()
