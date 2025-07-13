"""Calendar service for interacting with the MCP server."""

import datetime

from fastmcp import FastMCP

from .sdk import CalendarSDK
from .models import CalendarEvent, CalendarEventBoundary

mcp = FastMCP(name="Calendar Management Service")

calendar_sdk_ro = CalendarSDK(
    "credentials.json",
    "token_ro.json",
    scopes=["https://www.googleapis.com/auth/calendar.readonly"]
)

calendar_sdk_rw = CalendarSDK(
    "credentials.json",
    "token_rw.json",
    scopes=["https://www.googleapis.com/auth/calendar.events"]
)

@mcp.resource(uri="events://future/{limit}")
def get_upcoming_events(limit: int):
    """Retrieve upcoming events.

    Args:
        limit: Number of events to retrieve

    Returns:
        List of calendar events
    """

    service = calendar_sdk_ro.resource

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

    service = calendar_sdk_ro.resource

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
    return [CalendarEvent(**event).model_dump_json() for event in events]

@mcp.tool
def get_current_datetime() -> str:
    """
    Returns the current date and time in the format "YYYY-MM-DD HH:MM:SS".
    """
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S%z")

# TODO: Get timezone from the user's calendar

@mcp.tool
def create_event(event: CalendarEvent) -> CalendarEvent:
    """Create a new event.

    Args:
        event: Calendar event object

    Returns:
        Calendar event object
    """

    service = calendar_sdk_rw.resource

    # Call the Calendar API
    created = service.events().insert(
        calendarId="primary", 
        body=event.model_dump(exclude_none=True, exclude_defaults=True)
    ).execute()
    return CalendarEvent(**created)


if __name__ == "__main__":
    mcp.run()
