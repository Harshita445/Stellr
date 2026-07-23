from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    q: str = Field(..., min_length=3, description="Search query (minimum 3 characters)")
