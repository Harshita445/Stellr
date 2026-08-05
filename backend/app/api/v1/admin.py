"""Admin endpoints — timetable import and system management.

SECURITY: These endpoints are unprotected in the current phase.
Authentication + admin role check will be added in Phase 4 (auth module).
Do NOT deploy without auth in production.
"""

from fastapi import APIRouter, Depends, UploadFile, File

from app.api.deps import get_timetable_import_service, get_timetable_parser
from app.schemas.timetables.responses import ImportResponse
from app.services.timetable_import_service import TimetableImportService

router = APIRouter()


@router.post(
    "/import-timetable",
    response_model=ImportResponse,
    status_code=200,
    summary="Import semester timetable from Excel workbook",
    description=(
        "Accepts an .xlsx workbook, parses it, and stores normalized timetable "
        "data in PostgreSQL. Replaces all existing timetable data atomically. "
        "The workbook is parsed ONCE and never accessed during normal requests."
    ),
)
async def import_timetable(
    file: UploadFile = File(..., description="Semester timetable .xlsx workbook"),
    import_service: TimetableImportService = Depends(get_timetable_import_service),
) -> ImportResponse:
    if not file.filename or not file.filename.endswith((".xlsx", ".xlsm")):
        return ImportResponse(
            status="failed",
            errors=[f"Unsupported file format: {file.filename}. Expected .xlsx"],
        )

    content = await file.read()
    result = await import_service.import_workbook(content, file.filename)
    return result


@router.get(
    "/import-timetable/status",
    summary="Placeholder for async import status (future)",
)
async def import_status():
    """Future: poll the status of a running import task."""
    return {"status": "not_implemented"}
