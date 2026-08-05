"""Adapter from section-based timetable JSON to the availability contract."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from app.utils.availability_intervals import computeAvailability
from app.utils.timetable_intervals import buildBusyIntervals


DEFAULT_DAY_START = "08:00"
DEFAULT_DAY_END = "19:00"


def getSharedAvailability(
    users: Sequence[Mapping[str, Any]],
    timetableJson: Mapping[str, Mapping[str, Sequence[Mapping[str, Any]]]],
    dayName: str,
    now: str | None = None,
) -> dict[str, Any]:
    """Return the Phase 2 availability contract for users on one day.

    A missing section or a missing/empty day has no busy intervals, so that
    user is free for the entire fixed institution day window. Per-user busy
    intervals are built only for the requested users, while the day bounds are
    taken from the institution-level default window.
    """
    if not isinstance(dayName, str) or not dayName.strip():
        raise ValueError("dayName must be a non-empty string")

    intervals_per_user = []
    members = []
    for user in users:
        if not isinstance(user, Mapping):
            raise ValueError("Each user must be an object")
        if "user_id" not in user or "display_name" not in user or "section_code" not in user:
            raise ValueError("Each user requires user_id, display_name, and section_code")

        section_code = str(user["section_code"])
        section = timetableJson.get(section_code, {})
        if not isinstance(section, Mapping):
            raise ValueError(f"Section {section_code!r} must be an object")
        day_entries = section.get(dayName, [])
        user_intervals = buildBusyIntervals(day_entries, dayName)
        intervals_per_user.append(user_intervals)
        members.append({
            "user_id": user["user_id"],
            "display_name": user["display_name"],
        })

    day_start, day_end = _derive_day_bounds(timetableJson, dayName)
    return computeAvailability(
        intervals_per_user,
        now=now,
        dayStart=day_start,
        dayEnd=day_end,
        members=members,
    )


def _derive_day_bounds(
    timetable_json: Mapping[str, Mapping[str, Sequence[Mapping[str, Any]]]],
    day_name: str,
) -> tuple[int | str, int | str]:
    """Return the fixed institution-level day window for shared availability."""
    del timetable_json, day_name
    return DEFAULT_DAY_START, DEFAULT_DAY_END


# PEP 8 alias for backend callers; camel-case name mirrors the requested API.
get_shared_availability = getSharedAvailability
