"""Calendar service for interacting with the MCP server."""

import argparse
import datetime
from typing import Dict, Any
from fastmcp import FastMCP

from .sdk import CalendarSDK

mcp = FastMCP("Calendar Management Service")

calendar_sdk_ro = CalendarSDK(
    "credentials.json",
    "token_ro.json",
    scopes=["https://www.googleapis.com/auth/calendar.readonly"]
)

def parse_event(event: Dict[str, Any]) -> Dict[str, str]:
    return {
        "id": event.get("id", "No id."),
        "status": event.get("status", "No status."),
        "htmlLink": event.get("htmlLink", "No link."),
        "summary": event.get("summary", "No summary."),
        "description": event.get("description", "No description."),
        "start_time": event.get("start", {}).get("dateTime", "No start time."),
        "end_time": event.get("end", {}).get("dateTime", "No end time."),
    }

@mcp.resource(
    uri="events://future/{limit}",
    # mime_type="application/json"
)
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

    # TODO: Make a Pydantic model for events, and parse our events with it
    return [parse_event(event) for event in events]


@mcp.resource(uri="events://{start_time_str}/{end_time_str}")
async def get_events(start_time_str: str, end_time_str: str):
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

    return [parse_event(event) for event in events]


if __name__ == "__main__":
    mcp.run()
