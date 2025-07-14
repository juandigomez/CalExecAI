from pydantic import BaseModel
from typing import Any


class CalendarEvent(BaseModel):
    id: str
    status: str
    htmlLink: str
    summary: str
    description: str = ""
    start: dict[str, Any]
    end: dict[str, Any]
