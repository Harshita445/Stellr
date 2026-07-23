"""Time utility functions for slot intersection and availability computation.

This module is the heart of the availability engine. It operates purely on
data structures — no database access, no HTTP. Pure functions only, trivially
testable without any fixtures.

Slot model:
- A day is divided into SLOTS_PER_DAY (9) fixed-length academic periods.
- Each slot has a predefined (start_hour, start_minute, end_hour, end_minute)
  boundary from SLOT_BOUNDARIES (defined in models/timeslot.py).
- A user's day is represented as a bit array (list[int]) of length 9 where
  1 = busy (has a class), 0 = free.
- To find shared free time across N users: OR all busy arrays, invert, get
  the free bits, then merge adjacent free bits into contiguous windows.

Complexity: O(N * S) where N = number of users, S = SLOTS_PER_DAY (9).
In practice S is constant, so this is O(N). All operations are single-pass.
"""

import datetime
from typing import assert_never

from app.models.timeslot import SLOTS_PER_DAY, SLOT_BOUNDARIES

# Re-export constants so callers don't need to import the model module directly
__all__ = [
    "SLOTS_PER_DAY",
    "SLOT_BOUNDARIES",
    "slots_to_busy_array",
    "or_all",
    "invert",
    "merge_free_windows",
    "current_slot_index",
    "compute_availability",
]


def slots_to_busy_array(
    busy_slot_indices: set[int],
    slots_per_day: int = SLOTS_PER_DAY,
) -> list[int]:
    """Convert a set of busy slot indices into a 0/1 bit array.

    Input:  {0, 3, 7}  (slots 0, 3, and 7 are busy)
    Output: [1, 0, 0, 1, 0, 0, 0, 1, 0]
    """
    return [1 if i in busy_slot_indices else 0 for i in range(slots_per_day)]


def or_all(arrays: list[list[int]]) -> list[int]:
    """OR together multiple bit arrays of equal length.

    Input:  [[1,0,0,1,0], [0,1,0,0,1]]
    Output: [1,1,0,1,1]   (busy if ANY user is busy)
    """
    if not arrays:
        return [0] * SLOTS_PER_DAY
    return [int(any(bits)) for bits in zip(*arrays)]


def invert(arr: list[int]) -> list[int]:
    """Invert a bit array: 1→0, 0→1.

    Input:  [1, 0, 1, 0]
    Output: [0, 1, 0, 1]
    """
    return [0 if b else 1 for b in arr]


def _slot_to_time(slot_idx: int, slot_boundaries: dict) -> tuple[str, str]:
    """Convert a slot index to (start_time, end_time) as 'HH:MM' strings."""
    h1, m1, h2, m2 = slot_boundaries[slot_idx]
    return f"{h1:02d}:{m1:02d}", f"{h2:02d}:{m2:02d}"


def merge_free_windows(
    free_bits: list[int],
    slot_boundaries: dict[int, tuple[int, int, int, int]] = SLOT_BOUNDARIES,
) -> list[dict]:
    """Merge adjacent free bits into contiguous time windows.

    Single-pass O(S) where S = SLOTS_PER_DAY (9). Adjacent free slots are
    merged end-to-end (the end of slot N is the start of slot N+1, so if
    both are free, the merged window spans from slot N start to slot N+1 end).

    Returns a list of dicts, each with:
        "start": "HH:MM"   (start time of the window)
        "end":   "HH:MM"   (end time of the window)

    Example:
        free_bits = [0,1,1,0,0,1,0,1,1]
        Returns: [
            {"start": "09:50", "end": "10:40"},   # slot 1 only (slot 0 is busy)
            {"start": "14:20", "end": "15:10"},   # slot 5 only
            {"start": "16:10", "end": "17:50"},   # slots 7-8 merged
        ]
    """
    windows: list[dict] = []
    i = 0
    while i < len(free_bits):
        if free_bits[i] == 1:
            start_slot = i
            while i < len(free_bits) and free_bits[i] == 1:
                i += 1
            end_slot = i - 1
            start_time, _ = _slot_to_time(start_slot, slot_boundaries)
            _, end_time = _slot_to_time(end_slot, slot_boundaries)
            windows.append({"start": start_time, "end": end_time})
        else:
            i += 1
    return windows


def current_slot_index(
    now: datetime.time,
    slot_boundaries: dict[int, tuple[int, int, int, int]] = SLOT_BOUNDARIES,
) -> int | None:
    """Return the slot index that contains 'now', or None if now is between slots
    (i.e. in a break period like 10:40–11:00 or 12:40–13:30)."""
    now_minutes = now.hour * 60 + now.minute
    for idx, (h1, m1, h2, m2) in slot_boundaries.items():
        start = h1 * 60 + m1
        end = h2 * 60 + m2
        if start <= now_minutes < end:
            return idx
    return None


def compute_availability(
    busy_arrays: list[list[int]],
    now: datetime.time | None = None,
    slot_boundaries: dict[int, tuple[int, int, int, int]] = SLOT_BOUNDARIES,
) -> dict:
    """Main algorithm: given N user busy arrays, compute shared free windows.

    This is the core function called by both the friend and group endpoints.

    Args:
        busy_arrays: List of bit arrays, one per user. Each array length must
                     equal SLOTS_PER_DAY (9).
        now:         Current time (optional). If provided, current_overlap and
                     next_slot are computed relative to this time.
        slot_boundaries: Slot boundary definitions (from models/timeslot).

    Returns:
        dict with:
            "shared_windows": list[{"start": "HH:MM", "end": "HH:MM"}]
            "next_slot":      {"start": "HH:MM", "end": "HH:MM"} | None
            "current_overlap": bool
            "longest_window":  {"start": "HH:MM", "end": "HH:MM"} | None

    Algorithm steps (O(N)):
        1. OR all busy arrays → combined_busy (1 if ANY user is busy)
        2. Invert → shared_free (1 if ALL users are free)
        3. Merge adjacent free bits → shared_windows
        4. If now is provided, determine current_overlap and next_slot
        5. Find the longest contiguous window
    """
    combined_busy = or_all(busy_arrays)
    shared_free = invert(combined_busy)

    windows = merge_free_windows(shared_free, slot_boundaries)

    longest = max(windows, key=lambda w: _window_minutes(w, slot_boundaries)) if windows else None

    current_overlap = False
    next_slot = None
    if now is not None:
        now_idx = current_slot_index(now, slot_boundaries)
        if now_idx is not None and shared_free[now_idx] == 1:
            current_overlap = True

        for idx in range(SLOTS_PER_DAY):
            s1, _ = _slot_to_time(idx, slot_boundaries)
            if (now_idx is None or idx > now_idx) and shared_free[idx] == 1:
                _, e1 = _slot_to_time(idx, slot_boundaries)
                next_slot = {"start": s1, "end": e1}
                break

    return {
        "shared_windows": windows,
        "next_slot": next_slot,
        "current_overlap": current_overlap,
        "longest_window": longest,
    }


def _window_minutes(
    window: dict,
    slot_boundaries: dict[int, tuple[int, int, int, int]] = SLOT_BOUNDARIES,
) -> int:
    """Return the duration in minutes of a time window dict (approximate)."""
    start_parts = window["start"].split(":")
    end_parts = window["end"].split(":")
    start_mins = int(start_parts[0]) * 60 + int(start_parts[1])
    end_mins = int(end_parts[0]) * 60 + int(end_parts[1])
    return end_mins - start_mins
