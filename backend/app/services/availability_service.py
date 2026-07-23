"""AvailabilityService — core business logic for schedule comparison.

This is the most algorithmically important service in the application.
It computes shared free time windows across sets of users (friends, groups)
using bit-array operations on the timetable slot model.

Design:
- Read-only: no mutations, safe to call repeatedly.
- Pure algorithm + DB reads: no side effects.
- Cache-friendly (future): results can be cached by (section_ids, date).

Algorithm (for a set of users):
    1. Resolve each user → their section_id.
    2. Fetch all timetable entries for those sections on today's day_of_week.
    3. Build a SLOTS_PER_DAY (9) bit array per user: 1=busy, 0=free.
    4. OR all arrays together → combined_busy (1 if ANY user is busy).
    5. Invert → shared_free (1 if ALL users are simultaneously free).
    6. Merge adjacent free bits → contiguous time windows.
    7. Compute: current_overlap, next_slot, longest_window.

Complexity: O(N + M) where N = number of users, M = total timetable entries.
Each user contributes 1 bit array of constant size (9 slots), so the OR
operation is O(N * 9) = O(N). The merge is O(9) = O(1).
"""

from uuid import UUID

from app.models.timeslot import SLOTS_PER_DAY
from app.repositories.group_member_repository import GroupMemberRepository
from app.repositories.timetable_entry_repository import TimetableEntryRepository
from app.repositories.user_repository import UserRepository
from app.utils.time_utils import (
    compute_availability,
    slots_to_busy_array,
)


class AvailabilityService:

    def __init__(
        self,
        user_repo: UserRepository,
        tt_entry_repo: TimetableEntryRepository,
        group_member_repo: GroupMemberRepository,
    ):
        self.user_repo = user_repo
        self.tt_entry_repo = tt_entry_repo
        self.group_member_repo = group_member_repo

    async def compare_with_friend(
        self,
        user_id: UUID,
        friend_id: UUID,
        day_of_week: int,
        now_time = None,
    ) -> dict:
        """2-person availability comparison.

        Returns shared free windows for today.
        """
        return await self._compare_users([user_id, friend_id], day_of_week, now_time)

    async def get_group_overlap(
        self,
        group_id: UUID,
        day_of_week: int,
        now_time = None,
    ) -> dict:
        """Group availability comparison.

        Fetches all group members and computes shared free windows.
        """
        members = await self.group_member_repo.list_by_group(group_id)
        user_ids = [m.user_id for m in members]
        return await self._compare_users(user_ids, day_of_week, now_time)

    async def _compare_users(
        self,
        user_ids: list[UUID],
        day_of_week: int,
        now_time = None,
    ) -> dict:
        """Core internal method: compute shared availability for a set of users."""
        user_ids = list(set(user_ids))
        if len(user_ids) < 2:
            return {
                "shared_windows": [],
                "current_overlap": False,
                "next_slot": None,
                "longest_window": None,
            }

        users = []
        for uid in user_ids:
            u = await self.user_repo.find_by_id(uid)
            if u and u.section_id:
                users.append(u)

        if len(users) < 2:
            return {
                "shared_windows": [],
                "current_overlap": False,
                "next_slot": None,
                "longest_window": None,
            }

        # Fetch timetable entries for all sections in one query
        section_ids = list({u.section_id for u in users if u.section_id})
        by_section = await self.tt_entry_repo.get_by_sections(section_ids, day_of_week)

        # Map user → section → busy slot indices → bit array
        user_to_section: dict[UUID, UUID] = {}
        for u in users:
            if u.section_id:
                user_to_section[u.id] = u.section_id

        busy_arrays: list[list[int]] = []
        for uid in user_ids:
            section_id = user_to_section.get(uid)
            if section_id is None:
                busy_arrays.append([0] * SLOTS_PER_DAY)
                continue
            entries = by_section.get(section_id, [])
            busy_indices = {
                e.timeslot.slot_index
                for e in entries
                if e.timeslot is not None
            }
            busy_arrays.append(slots_to_busy_array(busy_indices))

        return compute_availability(busy_arrays, now=now_time)

    async def _stub_section_availability(self) -> None:
        """TODO (future scope): implement entire-section comparison.

        This would compare all members of a section (not just friends/groups).
        Skipped for MVP — see PROJECT_SPEC.md future scope.
        """
        raise NotImplementedError("Section-wide comparison is future scope")
