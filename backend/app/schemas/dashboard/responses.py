from pydantic import BaseModel, Field


class ClassInfo(BaseModel):
    course_code: str
    course_name: str
    start_time: str
    end_time: str
    venue: str | None = None
    slot_index: int | None = None


class CurrentClassInfo(BaseModel):
    course_code: str
    course_name: str
    start_time: str
    end_time: str
    venue: str | None = None
    time_remaining_minutes: int


class NextClassInfo(BaseModel):
    course_code: str
    course_name: str
    start_time: str
    end_time: str
    venue: str | None = None
    slot_index: int | None = None


class FreeWindow(BaseModel):
    start_time: str
    end_time: str
    duration_minutes: int


class DashboardResponse(BaseModel):
    date: str = Field(..., description="ISO date string YYYY-MM-DD")
    day_name: str = Field(..., description="Full day name e.g. Monday")
    section_code: str | None = Field(None, description="Section code of the user")
    section_id: str | None = Field(None, description="Section UUID")
    today_schedule: list[ClassInfo] = Field(default_factory=list)
    current_class: CurrentClassInfo | None = None
    next_class: NextClassInfo | None = None
    time_until_next_minutes: int | None = None
    free_windows: list[FreeWindow] = Field(default_factory=list)
