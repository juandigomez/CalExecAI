import pytest
from fastmcp import Client

from app.services.calendar_service.mcp import mcp
from app.services.calendar_service.models import CalendarEvent


@pytest.mark.asyncio
async def test_create_event():
    event = {
        "summary": "A test event",
        "start": {
            "date": "2025-07-08"
        },
        "end": {
            "date": "2025-07-10",
        }
    }
    async with Client(mcp) as tools:
        created_event = await tools.call_tool("create_event", arguments={"event": event})
        print(created_event)
    assert True
