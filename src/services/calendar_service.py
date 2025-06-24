"""Calendar service for interacting with the MCP server."""

import os
import argparse
import datetime
from typing import Dict, List, Callable, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastmcp import FastMCP
from fastmcp.exceptions import ResourceError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

mcp = FastMCP("Calendar Management Service")


def authenticate():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


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
    service = build("calendar", "v3", credentials=authenticate())

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
    events = [
        {
            "id": event["id"],
            "status": event["status"],
            "htmlLink": event["htmlLink"],
            "summary": event["summary"],
            # "description": event["description"],
            "start_time": event["start"]["dateTime"],
            "end_time": event["end"]["dateTime"],
        }
        for event in events
    ]

    return events


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCP Server")
    parser.add_argument(
        "transport", choices=["stdio", "sse"], help="Transport mode (stdio or sse)"
    )
    args = parser.parse_args()

    mcp.run(transport=args.transport)
