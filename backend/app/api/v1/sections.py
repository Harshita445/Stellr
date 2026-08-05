"""Sections API routes.

Public endpoint listing all available sections for the onboarding dropdown.
"""

from fastapi import APIRouter, Depends

from app.api.deps import get_section_repo
from app.repositories.section_repository import SectionRepository
from pydantic import BaseModel

router = APIRouter(tags=["Sections"])


class SectionItem(BaseModel):
    name: str
    department: str
    semester: int


class SectionListResponse(BaseModel):
    sections: list[SectionItem]


@router.get("/", response_model=SectionListResponse)
async def list_sections(
    section_repo: SectionRepository = Depends(get_section_repo),
):
    sections = await section_repo.list(order_by="name")
    return SectionListResponse(
        sections=[
            SectionItem(
                name=s.name,
                department=s.department,
                semester=s.semester,
            )
            for s in sections
        ]
    )
