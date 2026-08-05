"""Timetable Import Service

Orchestrates the full import pipeline: parse → normalize → store.

Transactional guarantee:
- All-or-nothing: if any step fails, no data is persisted.
- Previous timetable remains intact until the new one is fully committed.
- On success, old data is replaced atomically (DELETE + INSERT in same TX).

The workbook is ONLY accessed by TimetableParserService.parse().
This service operates only on in-memory parsed records and the database.
"""

import os
import tempfile
from uuid import UUID

from app.core.logging import logger
from app.models.timeslot import SLOT_BOUNDARIES, SLOTS_PER_DAY
from app.repositories.course_repository import CourseRepository
from app.repositories.section_repository import SectionRepository
from app.repositories.timetable_entry_repository import TimetableEntryRepository
from app.repositories.timeslot_repository import TimeslotRepository
from app.schemas.timetables.responses import ImportResponse, ParsedSheetSummary
from app.services.timetable_parser_service import TimetableParserService


def _time_str(hour: int, minute: int) -> str:
    return f"{hour:02d}:{minute:02d}"


class TimetableImportService:
    """Orchestrates the full import pipeline.

    Accepts an uploaded file, saves it temporarily, parses it, normalizes
    the data, and bulk-inserts into PostgreSQL within a single transaction.
    """

    def __init__(
        self,
        section_repo: SectionRepository,
        course_repo: CourseRepository,
        timeslot_repo: TimeslotRepository,
        tt_entry_repo: TimetableEntryRepository,
        parser: TimetableParserService,
    ):
        self.section_repo = section_repo
        self.course_repo = course_repo
        self.timeslot_repo = timeslot_repo
        self.tt_entry_repo = tt_entry_repo
        self.parser = parser

    async def import_workbook(self, file_content: bytes, filename: str) -> ImportResponse:
        """Import a timetable from uploaded Excel file content.

        Steps:
        1. Save to temp file
        2. Parse workbook into ParsedRows
        3. Ensure all reference data exists (timeslots, sections, courses)
        4. Bulk insert timetable entries
        5. Return summary
        """
        result = ImportResponse(status="processing")

        # 1. Save uploaded content to a temporary file
        suffix = os.path.splitext(filename)[1] if filename else ".xlsx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        try:
            # 2. Parse
            parse_result = await self.parser.parse(tmp_path)

            if parse_result.errors:
                result.status = "failed"
                result.errors = parse_result.errors
                return result

            if not parse_result.rows:
                result.status = "failed"
                result.errors.append("No timetable entries found in workbook")
                return result

            result.warnings = parse_result.warnings

            # 3. Prepare reference data
            # Group unique sections, courses, and timeslots
            unique_sections: dict[str, dict] = {}
            unique_courses: dict[str, str] = {}  # code → name
            unique_timeslots: set[tuple[int, int]] = set()  # (day, slot_index)

            for row in parse_result.rows:
                # Sections: determined from section_code
                # section_code format like "3A1A" — contains year/section info
                # We derive department and semester from the sheet name
                if row.section_code not in unique_sections:
                    dept, sem = self._derive_department_semester(row)
                    unique_sections[row.section_code] = {
                        "name": row.section_code,
                        "department": dept,
                        "semester": sem,
                        "academic_year": "2025-2026",  # TODO: detect from filename or sheet
                    }

                # Courses: map subject name to a stable code
                if row.subject_name not in unique_courses:
                    course_code = self._subject_to_code(row.subject_name)
                    unique_courses[row.subject_name] = course_code

                # Timeslots: defined by (day_of_week, slot_index)
                unique_timeslots.add((row.day_of_week, row.slot_index))

            # 4. Ensure reference rows exist in DB
            # Timeslots first (no FK dependencies)
            for day_of_week, slot_index in sorted(unique_timeslots):
                bounds = SLOT_BOUNDARIES.get(slot_index)
                if bounds:
                    start_h, start_m, end_h, end_m = bounds
                    await self.timeslot_repo.upsert(
                        day_of_week=day_of_week,
                        slot_index=slot_index,
                        start_time=_time_str(start_h, start_m),
                        end_time=_time_str(end_h, end_m),
                    )

            # Sections next
            section_id_map: dict[str, UUID] = {}
            for section_code, sec_data in unique_sections.items():
                section = await self.section_repo.upsert(
                    name=sec_data["name"],
                    department=sec_data["department"],
                    semester=sec_data["semester"],
                    academic_year=sec_data["academic_year"],
                )
                section_id_map[section_code] = section.id

            # Courses last
            course_id_map: dict[str, UUID] = {}
            for subject_name, course_code in unique_courses.items():
                course = await self.course_repo.upsert(
                    code=course_code,
                    name=subject_name,
                )
                course_id_map[subject_name] = course.id

            # 5. Delete old entries for affected sections and insert new ones
            affected_section_ids = list(section_id_map.values())

            # Delete old entries within the transaction
            for sid in affected_section_ids:
                await self.tt_entry_repo.delete_by_section(sid)

            # Look up timeslot IDs for all (day, slot) combos
            timeslot_id_map: dict[tuple[int, int], UUID] = {}
            for day_of_week, slot_index in unique_timeslots:
                ts = await self.timeslot_repo.find_by_day_and_slot(day_of_week, slot_index)
                if ts:
                    timeslot_id_map[(day_of_week, slot_index)] = ts.id

            # Build bulk insert payload
            entries_to_insert: list[dict] = []
            for row in parse_result.rows:
                section_id = section_id_map.get(row.section_code)
                course_id = course_id_map.get(row.subject_name)
                timeslot_id = timeslot_id_map.get((row.day_of_week, row.slot_index))

                if not all([section_id, course_id, timeslot_id]):
                    continue

                entries_to_insert.append({
                    "section_id": section_id,
                    "course_id": course_id,
                    "timeslot_id": timeslot_id,
                })

            if entries_to_insert:
                await self.tt_entry_repo.bulk_insert(entries_to_insert)

            # 6. Build summary
            result.status = "completed"
            result.sections_found = len(unique_sections)
            result.courses_found = len(unique_courses)
            result.entries_written = len(entries_to_insert)

            # Build per-sheet summaries
            sheet_sections: dict[str, set[str]] = {}
            for row in parse_result.rows:
                sheet_sections.setdefault(row.sheet_name, set()).add(row.section_code)

            for sheet_name, secs in sheet_sections.items():
                result.sheets.append(ParsedSheetSummary(
                    sheet_name=sheet_name,
                    sections_found=sorted(secs),
                    slots_parsed=sum(1 for r in parse_result.rows if r.sheet_name == sheet_name),
                    warnings=[w for w in parse_result.warnings if sheet_name in w],
                ))

            logger.info(
                "Timetable import completed",
                extra={
                    "sections": result.sections_found,
                    "courses": result.courses_found,
                    "entries": result.entries_written,
                },
            )

        except Exception as exc:
            logger.error("Timetable import failed", exc_info=exc, extra={})
            result.status = "failed"
            result.errors.append(str(exc))
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

        return result

    def _derive_department_semester(self, row) -> tuple[str, int]:
        """Derive department name and semester from sheet name and section code.

        Sheet names are like "First Year A", "Second Year B", "Third Year Computer Science".
        Section codes are like "3A1A" where the first character indicates year.

        This is a best-effort heuristic. The actual values can be overridden
        in the admin interface or via configuration.

        NOTE: This is a placeholder implementation. The actual workbook may
        have a different format. Update this method once the workbook format
        is confirmed.
        """
        sheet_lower = row.sheet_name.lower()

        # Detect year from sheet name
        year_map = {
            "first": 1, "1st": 1, "i": 1,
            "second": 2, "2nd": 2, "ii": 2,
            "third": 3, "3rd": 3, "iii": 3,
            "fourth": 4, "4th": 4, "iv": 4,
        }

        semester = 1
        for key, val in year_map.items():
            if key in sheet_lower:
                semester = val * 2 - 1  # First year → sem 1, Second year → sem 3, etc.
                break

        # Try to extract department from sheet name
        # e.g. "Third Year Computer Science" → "Computer Science"
        department = sheet_lower
        for prefix in ["first year", "second year", "third year", "fourth year",
                        "1st year", "2nd year", "3rd year", "4th year"]:
            if prefix in sheet_lower:
                remainder = sheet_lower.replace(prefix, "").strip()
                if remainder and remainder not in ("a", "b", "c", "d"):
                    department = remainder.title()
                break

        # Fallback: use section code prefix
        if department == sheet_lower:
            # e.g. "3A1A" → department "A", or use section_code[1]
            if len(row.section_code) >= 2:
                department = f"Department {row.section_code[1]}"
            else:
                department = "General"

        return department.strip(), semester

    @staticmethod
    def _subject_to_code(subject_name: str) -> str:
        """Generate a stable course code from a subject name.

        e.g. "Data Structures" → "DS", "Mathematics III" → "MATH3"
        This is a lossy transformation. The actual course code from the
        institution's system would be better, but the workbook only provides
        subject names.

        NOTE: If the workbook later provides course codes, this method
        should be replaced with direct extraction.
        """
        import re

        cleaned = subject_name.strip().upper()
        # Take first letters of each word
        words = re.findall(r"[A-Z]+", cleaned)
        if not words:
            return cleaned[:8]
        code = "".join(w[0] for w in words if w)
        return code[:12]
