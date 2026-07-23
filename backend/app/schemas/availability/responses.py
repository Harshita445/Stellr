from pydantic import BaseModel, Field


class SharedWindow(BaseModel):
    start: str = Field(..., description="Start time in HH:MM format")
    end: str = Field(..., description="End time in HH:MM format")


class AvailabilityResponse(BaseModel):
    shared_windows: list[SharedWindow] = Field(
        default_factory=list,
        description="Contiguous free time windows shared by all users today",
    )
    current_overlap: bool = Field(
        False,
        description="Are ALL users free right now?",
    )
    next_slot: SharedWindow | None = Field(
        None,
        description="Soonest upcoming slot where all users are free",
    )
    longest_window: SharedWindow | None = Field(
        None,
        description="Longest contiguous block where all users are free today",
    )
