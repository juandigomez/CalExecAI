from pydantic import BaseModel
from typing import Any


class CalendarEventBoundary(BaseModel):
    date: str = ""
    timeZone: str = ""
    dateTime: str = ""

class CalendarEvent(BaseModel):
    id: str = ""
    status: str = ""
    htmlLink: str = ""
    summary: str = ""
    description: str = ""
    start: CalendarEventBoundary
    end: CalendarEventBoundary
    endTimeUnspecified: bool = False
