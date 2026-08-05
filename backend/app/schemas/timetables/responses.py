from pydantic import BaseModel, Field


class ParsedSheetSummary(BaseModel):
    sheet_name: str
    sections_found: list[str]
    slots_parsed: int
    warnings: list[str]


class ImportResponse(BaseModel):
    status: str = Field(..., description="'processing', 'completed', or 'failed'")
    sections_found: int = 0
    courses_found: int = 0
    entries_written: int = 0
    sheets: list[ParsedSheetSummary] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ImportStatusResponse(BaseModel):
    task_id: str
    status: str
