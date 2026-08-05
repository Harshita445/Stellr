"""Pure continuous-time availability operations for parsed timetables."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, TypedDict

from app.utils.timetable_intervals import BusyInterval, minutes_since_midnight


class TimeWindow(TypedDict):
    start: str
    end: str


class MemberAvailability(TypedDict):
    user_id: str
    display_name: str
    is_free_now: bool


def unionBusy(intervalsPerUser: Sequence[Sequence[Mapping[str, int]]]) -> list[BusyInterval]:
    """Merge every user's busy intervals into a continuous-time OR."""
    all_intervals = [
        {"start": interval["start"], "end": interval["end"]}
        for user_intervals in intervalsPerUser
        for interval in user_intervals
    ]
    return _merge_intervals(all_intervals)


def invertToFree(
    combinedBusy: Sequence[Mapping[str, int]], dayStart: int | str, dayEnd: int | str
) -> list[BusyInterval]:
    """Subtract busy time from the inclusive day window's half-open interval."""
    start, end = _normalize_bounds(dayStart, dayEnd)
    clipped_busy = _merge_intervals([
        {"start": max(start, interval["start"]), "end": min(end, interval["end"])}
        for interval in combinedBusy
        if interval["end"] > start and interval["start"] < end
    ])

    free: list[BusyInterval] = []
    cursor = start
    for interval in clipped_busy:
        if cursor < interval["start"]:
            free.append({"start": cursor, "end": interval["start"]})
        cursor = max(cursor, interval["end"])
    if cursor < end:
        free.append({"start": cursor, "end": end})
    return free


def mergeAdjacent(
    freeIntervals: Sequence[Mapping[str, int]], gapToleranceMinutes: int = 0
) -> list[BusyInterval]:
    """Merge free windows separated by no more than ``gapToleranceMinutes``."""
    if gapToleranceMinutes < 0:
        raise ValueError("gapToleranceMinutes must be non-negative")
    merged = _merge_intervals(freeIntervals)
    result: list[BusyInterval] = []
    for interval in merged:
        if result and interval["start"] - result[-1]["end"] <= gapToleranceMinutes:
            result[-1]["end"] = interval["end"]
        else:
            result.append(interval.copy())
    return result


def computeAvailability(
    intervalsPerUser: Sequence[Sequence[Mapping[str, int]]],
    now: str | None = None,
    dayStart: int | str = "08:00",
    dayEnd: int | str = "19:00",
    *,
    gapToleranceMinutes: int = 0,
    members: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compute shared availability without assuming fixed institutional slots.

    ``dayStart`` and ``dayEnd`` are required conceptually for an all-free user;
    defaults provide a practical 08:00–19:00 window. Pass minute values or
    strict ``HH:MM`` strings. ``members`` optionally supplies ``user_id`` and
    ``display_name`` for the contract's member data; positional defaults are
    used when it is omitted.
    """
    day_start, day_end = _normalize_bounds(dayStart, dayEnd)
    if members is not None and len(members) != len(intervalsPerUser):
        raise ValueError("members must have one entry for each user")
    now_minutes = minutes_since_midnight(now) if now is not None else None

    combined_busy = unionBusy(intervalsPerUser)
    free_intervals = mergeAdjacent(
        invertToFree(combined_busy, day_start, day_end), gapToleranceMinutes
    )
    shared_windows = [_window(interval) for interval in free_intervals]

    current_overlap = bool(
        now_minutes is not None
        and _is_free_at(free_intervals, now_minutes)
    )
    # A current window is not "upcoming"; return the first window that starts
    # strictly after now. With no now supplied, return the day's first window.
    upcoming = next(
        (
            interval
            for interval in free_intervals
            if now_minutes is None or interval["start"] > now_minutes
        ),
        None,
    )
    longest = max(
        free_intervals,
        key=lambda interval: interval["end"] - interval["start"],
        default=None,
    )

    member_availabilities: list[MemberAvailability] = []
    for index, user_intervals in enumerate(intervalsPerUser):
        member = members[index] if members is not None else {}
        member_availabilities.append({
            "user_id": str(member.get("user_id", index)),
            "display_name": str(member.get("display_name", f"User {index + 1}")),
            "is_free_now": bool(
                now_minutes is not None
                and day_start <= now_minutes < day_end
                and not _is_busy_at(user_intervals, now_minutes)
            ),
        })

    return {
        "shared_windows": shared_windows,
        "current_overlap": current_overlap,
        "next_slot": _window(upcoming) if upcoming else None,
        "longest_window": _window(longest) if longest else None,
        "member_availabilities": member_availabilities,
    }


def _merge_intervals(intervals: Sequence[Mapping[str, int]]) -> list[BusyInterval]:
    valid: list[BusyInterval] = []
    for interval in intervals:
        start, end = interval["start"], interval["end"]
        if not isinstance(start, int) or not isinstance(end, int) or end <= start:
            raise ValueError(f"Invalid interval: {interval!r}")
        valid.append({"start": start, "end": end})
    valid.sort(key=lambda interval: (interval["start"], interval["end"]))
    result: list[BusyInterval] = []
    for interval in valid:
        if result and interval["start"] <= result[-1]["end"]:
            result[-1]["end"] = max(result[-1]["end"], interval["end"])
        else:
            result.append(interval)
    return result


def _normalize_bounds(day_start: int | str, day_end: int | str) -> tuple[int, int]:
    start = minutes_since_midnight(day_start) if isinstance(day_start, str) else day_start
    end = minutes_since_midnight(day_end) if isinstance(day_end, str) else day_end
    if not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end <= 1440:
        raise ValueError("dayStart and dayEnd must be valid increasing minute bounds")
    return start, end


def _is_busy_at(intervals: Sequence[Mapping[str, int]], moment: int) -> bool:
    return any(interval["start"] <= moment < interval["end"] for interval in intervals)


def _is_free_at(intervals: Sequence[Mapping[str, int]], moment: int) -> bool:
    return any(interval["start"] <= moment < interval["end"] for interval in intervals)


def _window(interval: Mapping[str, int]) -> TimeWindow:
    return {"start": _format_time(interval["start"]), "end": _format_time(interval["end"])}


def _format_time(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


# PEP 8 aliases for backend callers; camel-case names match the phase contract.
union_busy = unionBusy
invert_to_free = invertToFree
merge_adjacent = mergeAdjacent
compute_availability = computeAvailability
