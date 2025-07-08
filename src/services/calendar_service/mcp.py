"""Calendar service for interacting with the MCP server."""

import argparse
import datetime
from typing import Dict, Any
from fastmcp import FastMCP

from .sdk import CalendarSDK
from .models import CalendarEvent

mcp = FastMCP("Calendar Management Service")

calendar_sdk_ro = CalendarSDK(
    "credentials.json",
    "token_ro.json",
    scopes=["https://www.googleapis.com/auth/calendar.readonly"]
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
async def get_events_between_dates(start_time_str: str, end_time_str: str):
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


if __name__ == "__main__":
    mcp.run()
