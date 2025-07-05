"""Calendar service for interacting with the MCP server."""

import os
import argparse
import datetime
from typing import Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastmcp import FastMCP
from fastmcp.exceptions import ResourceError

mcp = FastMCP("Calendar Management Service")

class CalendarSDK():

    def __init__(self, pk_file_path: str, token_file_path: str, scopes: list[str]) -> None:
        self.pk_file_path = pk_file_path
        self.token_file_path = token_file_path
        self.scopes = scopes

    def authenticate(self):
        creds = None
        
        if os.path.exists(self.token_file_path):
            creds = self.get_creds_from_token()

        if not creds:
            creds = self.get_creds_from_pk()
            self.cache_creds_as_token(creds)
        elif creds and creds.expired and creds.refresh_token:
            # Refresh silently
            creds.refresh(Request())
            self.cache_creds_as_token(creds)
        elif not creds.valid:
            # Fallback: must re-authenticate
            creds = self.get_creds_from_pk()
            self.cache_creds_as_token(creds)
            
        return creds
    
    def get_creds_from_token(self):
        return Credentials.from_authorized_user_file(self.token_file_path, self.scopes)

    def get_creds_from_pk(self):
        flow = InstalledAppFlow.from_client_secrets_file(self.pk_file_path, self.scopes)
        creds = flow.run_local_server(port=0)
        return creds

    def cache_creds_as_token(self, creds: Any):
        with open(self.token_file_path, "w") as token:
            token.write(creds.to_json())

    @property
    def credentials(self):
        if not hasattr(self, "_credentials"):
            self._credentials = self.authenticate()
        return self._credentials

    @property
    def resource(self):
        if not hasattr(self, "_resource"):
            self._resource = build("calendar", "v3", credentials=self.credentials)
        return self._resource
    

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
    parser = argparse.ArgumentParser(description="MCP Server")
    parser.add_argument(
        "transport", choices=["stdio", "sse"], help="Transport mode (stdio or sse)"
    )
    args = parser.parse_args()

    mcp.run(transport=args.transport)
