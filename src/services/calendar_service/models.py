from pydantic import BaseModel, Field
from typing import Optional


class CalendarEventBoundary(BaseModel):
    """
    The start or end of an event.
    If date is specified, then datetime and timezone should be empty.
    If datetime is specified, then date should be empty.
    Timezone should only be specified if datetime does not include a timezone offset.
    Prefer to set the offset in the datetime field.
    Determine the desired timezoned by getting today's datetime with your tools and getting the timezone from it.
    """

    date: Optional[str] = Field(
        description="The date, in the format 'yyyy-mm-dd', if this is an all-day event.",
        default=None
    )
    timeZone: Optional[str] = Field(
        description="""
        The time, as a combined date-time value (formatted according to RFC3339).
        A time zone offset is required unless a time zone is explicitly specified in timeZone.
        """,
        default=None
    )
    dateTime: Optional[str] = Field(
        description="""
        The time zone in which the time is specified.
        (Formatted as an IANA Time Zone Database name, e.g. "Europe/Zurich".)
        For recurring events this field is required and specifies the time zone in which the recurrence is expanded.
        For single events this field is optional and indicates a custom time zone for the event start/end.
        """,
        default=None
    )


class CalendarEvent(BaseModel):
    id: Optional[str] = None
    status: Optional[str] = None
    htmlLink: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    start: CalendarEventBoundary
    end: CalendarEventBoundary
