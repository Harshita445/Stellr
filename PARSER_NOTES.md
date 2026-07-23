# Parser Notes — Timetable Workbook Structure

## Source

This document describes the expected structure of the semester timetable
workbook (.xlsx) and the assumptions made during parser implementation.

---

## Sheet Naming Convention (Expected)

Sheets are named per year/department combination, e.g.:

| Sheet Name | Content |
|-----------|---------|
| `First Year A` | First-year students, Section A (all departments) |
| `First Year B` | First-year students, Section B |
| `Second Year A` | Second-year students, Section A |
| `Second Year Computer Science` | Second-year Computer Science department |
| `Third Year A` | Third-year students, Section A |

**Assumption**: Sheet names start with a year indicator ("First", "Second",
"Third", "Fourth" or "1st", "2nd", "3rd", "4th"). The remainder is used to
derive the department name.

**If the actual sheet names differ**, the `_derive_department_semester()`
method in `timetable_import_service.py` must be updated.

---

## Section Code Format (Expected)

Section codes are short alphanumeric strings in column headers, e.g.:

| Code | Meaning |
|------|---------|
| `3A1A` | Year 3, Department A, Section 1, Group A |
| `3A1B` | Year 3, Department A, Section 1, Group B |
| `2CSE1` | Year 2, Computer Science, Section 1 |

**Assumption**: Section codes are 3–6 characters, alphanumeric, uppercase.

---

## Row Structure

| Column | Content |
|--------|---------|
| Column A (0) | Day name or row label |
| Column B+ (1+) | One column per section, header is the section code |

**Day groups**: Rows are grouped by day. A day header row contains the day
name (e.g. "Monday") in column A. Subsequent rows under it contain slot data.

**Slots**: Each row within a day group represents one academic period (slot).
Slot 0 is the first row under the day header, Slot 1 is the next, etc.

**Empty cells**: An empty cell means the section is free during that slot.

**Non-empty cells**: A cell containing text means the section has a class.
The cell value is the subject name.

**Non-academic entries**: Cells containing "CLUB", "BREAK", "LUNCH", etc.
are treated as free time (not imported).

---

## Slot Boundaries

The parser uses fixed slot boundaries (hardcoded for now). These must match
the institution's actual timetable structure:

| Slot | Start | End | Duration |
|------|-------|-----|----------|
| 0 | 09:00 | 09:50 | 50 min |
| 1 | 09:50 | 10:40 | 50 min |
| 2 | 11:00 | 11:50 | 50 min |
| 3 | 11:50 | 12:40 | 50 min |
| 4 | 13:30 | 14:20 | 50 min |
| 5 | 14:20 | 15:10 | 50 min |
| 6 | 15:20 | 16:10 | 50 min |
| 7 | 16:10 | 17:00 | 50 min |
| 8 | 17:00 | 17:50 | 50 min |

**Assumption**: These times correspond to the institution's standard academic
periods. If different, update `SLOT_BOUNDARIES` in `models/timeslot.py`.

**Assumption**: There are 9 slots per day (some days may have fewer rows).
Defined as `SLOTS_PER_DAY = 9`.

---

## Days of the Week

Expected day names (case-insensitive, as they appear in the workbook):

| Workbook Label | Day Index |
|----------------|-----------|
| Monday | 0 |
| Tuesday | 1 |
| Wednesday | 2 |
| Thursday | 3 |
| Friday | 4 |
| Saturday | 5 |

**Assumption**: Sunday is either absent or present but without data.

---

## Manual Assumptions Requiring Verification

1. **Department/Semester derivation**: The parser guesses department and
   semester from the sheet name and section code. These are stored in the
   `sections` table. **Verify that the derived values are correct**.

2. **Course code generation**: Subject names are converted to course codes
   using an acronym heuristic (`_subject_to_code`). The actual course
   catalogue codes would be more reliable. **Check the generated codes in
   the `courses` table after import**.

3. **Academic year**: Currently hardcoded to `"2025-2026"`. Either detect
   this from the filename, the sheet content, or make it configurable in
   the admin import UI.

4. **Slot boundaries**: The 9-slot schedule above assumes a typical
   engineering college timetable. **Confirm with the actual workbook**.

5. **Day detection**: The parser looks for day names in column A.
   If the workbook uses a different convention (e.g. row headers like
   "Period 1", "Period 2" with day names elsewhere), the parser will fail
   to detect days and import nothing.

6. **Merged cells**: openpyxl reads merged cells as `None` in all cells
   except the top-left. If day names span merged rows, only one row will
   have the day label. The parser handles this by maintaining a
   `current_day_name` state.

7. **Subject name normalization**: All subject names are stored as-is
   (whitespace stripped). If the workbook uses abbreviations or codes
   inconsistently across sheets, a normalization pass may be needed.

---

## Import Safety

- Re-importing the same workbook is safe: existing entries for affected
  sections are deleted and replaced within a single transaction.
- If the import fails mid-way, the entire transaction is rolled back.
  The previous timetable remains intact.
- The workbook file is never stored permanently. It is saved to a temp
  file, parsed, and deleted.
