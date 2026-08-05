"""Pure helpers for turning parsed timetable JSON into busy intervals."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, TypedDict


class BusyInterval(TypedDict):
    """A half-open interval, expressed as minutes since midnight."""

    start: int
    end: int


# No literal break codes occur in the supplied timetable. Keep this explicit so
# an institution can opt in to its own known codes without changing the parser.
DEFAULT_BREAK_MARKERS: frozenset[str] = frozenset()

# Examples in the supplied data: PKC, PWS, RF2, APC8, RKY, ANK, VJ, AG, VK,
# SAT. This deliberately excludes normal subject codes such as UES102L.
_MENTORING_CODE = re.compile(r"^[A-Z]{2,4}\d?$", re.IGNORECASE)
_TIME = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


def minutes_since_midnight(value: str) -> int:
    """Parse a strict ``HH:MM`` value into minutes since midnight.

    Raises ``ValueError`` for absent or malformed values rather than silently
    generating incorrect availability.
    """
    if not isinstance(value, str) or not _TIME.fullmatch(value):
        raise ValueError(f"Expected time in HH:MM format, got {value!r}")
    hour, minute = map(int, value.split(":"))
    return hour * 60 + minute


def buildBusyIntervals(
    timetable: Sequence[Mapping[str, Any]] | Mapping[str, Sequence[Mapping[str, Any]]],
    dayName: str | None = None,
    *,
    breakMarkers: Iterable[str] = DEFAULT_BREAK_MARKERS,
    treatMentoringSlotsAsFree: bool = False,
) -> list[BusyInterval]:
    """Return sorted, merged busy intervals for one section's day.

    ``timetable`` can be either the day array (the value of
    ``section[dayName]``) or the complete section schedule, in which case
    ``dayName`` selects the day. Adjacent intervals are merged as well as
    overlapping ones.

    A course is busy unless it is a true blank (empty code, room, and name), a
    configured break marker, or an opt-in mentoring slot. Entries with a room
    are always busy, even when their name is empty.
    """
    if isinstance(timetable, Mapping):
        if dayName is None:
            raise ValueError("dayName is required when timetable is a section schedule")
        day_entries = timetable.get(dayName, [])
    else:
        day_entries = timetable
    if not isinstance(day_entries, Sequence) or isinstance(day_entries, (str, bytes)):
        raise ValueError("A timetable day must be an array of entries")

    normalized_break_markers = {
        marker.strip().upper() for marker in breakMarkers if isinstance(marker, str)
    }
    intervals: list[BusyInterval] = []

    for slot in day_entries:
        if not isinstance(slot, Mapping):
            raise ValueError("Each timetable entry must be an object")
        courses = slot.get("courses", [])
        if not isinstance(courses, Sequence) or isinstance(courses, (str, bytes)):
            raise ValueError("Each timetable entry must contain a courses array")

        for course in courses:
            if not isinstance(course, Mapping):
                raise ValueError("Each course must be an object")
            if _is_non_busy(
                course,
                normalized_break_markers,
                treatMentoringSlotsAsFree,
            ):
                continue

            start = minutes_since_midnight(course.get("start_time"))
            end = minutes_since_midnight(course.get("end_time"))
            if end <= start:
                raise ValueError(
                    f"Course end_time must be after start_time: {course!r}"
                )
            intervals.append({"start": start, "end": end})

    intervals.sort(key=lambda interval: (interval["start"], interval["end"]))
    merged: list[BusyInterval] = []
    for interval in intervals:
        if merged and interval["start"] <= merged[-1]["end"]:
            merged[-1]["end"] = max(merged[-1]["end"], interval["end"])
        else:
            merged.append(interval.copy())
    return merged


def _is_non_busy(
    course: Mapping[str, Any],
    break_markers: set[str],
    treat_mentoring_slots_as_free: bool,
) -> bool:
    code = str(course.get("code") or "").strip()
    room = str(course.get("room") or "").strip()
    name = str(course.get("name") or "").strip()

    if not code and not room and not name:
        return True
    if code.upper() in break_markers:
        return True
    return (
        treat_mentoring_slots_as_free
        and not room
        and not name
        and bool(_MENTORING_CODE.fullmatch(code))
    )


# Snake-case alias for Python callers; retain the requested camel-case API.
build_busy_intervals = buildBusyIntervals
