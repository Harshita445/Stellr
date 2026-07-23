from datetime import date, datetime, time, timedelta
from uuid import UUID

from app.core.exceptions import UserNotFoundError
from app.repositories.timetable_entry_repository import TimetableEntryRepository
from app.repositories.timeslot_repository import TimeslotRepository
from app.repositories.user_repository import UserRepository


START_OF_DAY = time(9, 0)
END_OF_DAY = time(17, 50)

DAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]


class DashboardService:

    def __init__(
        self,
        user_repo: UserRepository,
        tt_entry_repo: TimetableEntryRepository,
        timeslot_repo: TimeslotRepository,
    ):
        self.user_repo = user_repo
        self.tt_entry_repo = tt_entry_repo
        self.timeslot_repo = timeslot_repo

    async def get_dashboard(self, user_id: UUID) -> dict:
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        today = date.today()
        day_of_week = today.weekday()
        day_name = DAY_NAMES[day_of_week]

        entries = await self.tt_entry_repo.get_by_section(
            user.section_id, day_of_week
        )

        classes = []
        for entry in entries:
            ts = entry.timeslot
            classes.append({
                "course_code": entry.course.code,
                "course_name": entry.course.name,
                "start_time": ts.start_time,
                "end_time": ts.end_time,
                "venue": ts.venue,
                "slot_index": ts.slot_index,
            })

        classes.sort(key=lambda c: c["start_time"])

        now = datetime.now().time()
        current_class = None
        next_class = None

        for c in classes:
            start = _parse_time(c["start_time"])
            end = _parse_time(c["end_time"])
            if start and end and start <= now <= end:
                remaining = _minutes_between(now, end)
                current_class = {
                    "course_code": c["course_code"],
                    "course_name": c["course_name"],
                    "start_time": c["start_time"],
                    "end_time": c["end_time"],
                    "venue": c["venue"],
                    "time_remaining_minutes": remaining,
                }
            elif start and start > now:
                if next_class is None:
                    next_class = {
                        "course_code": c["course_code"],
                        "course_name": c["course_name"],
                        "start_time": c["start_time"],
                        "end_time": c["end_time"],
                        "venue": c["venue"],
                        "slot_index": c["slot_index"],
                    }

        time_until_next = None
        if next_class:
            start = _parse_time(next_class["start_time"])
            now_dt = datetime.now()
            next_dt = datetime(
                now_dt.year, now_dt.month, now_dt.day,
                start.hour, start.minute,
            )
            diff = next_dt - now_dt
            time_until_next = max(0, int(diff.total_seconds() / 60))

        free_windows = _compute_free_windows(classes)

        return {
            "date": today.isoformat(),
            "day_name": day_name,
            "section_code": user.section.name if user.section else None,
            "section_id": str(user.section_id) if user.section_id else None,
            "today_schedule": classes,
            "current_class": current_class,
            "next_class": next_class,
            "time_until_next_minutes": time_until_next,
            "free_windows": free_windows,
        }


def _parse_time(t: str) -> time | None:
    if not t:
        return None
    parts = t.split(":")
    return time(int(parts[0]), int(parts[1]))


def _minutes_between(start: time, end: time) -> int:
    return (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)


def _compute_free_windows(classes: list[dict]) -> list[dict]:
    if not classes:
        return [{
            "start_time": "09:00",
            "end_time": "17:50",
            "duration_minutes": 530,
        }]

    windows = []

    first = classes[0]
    first_start = _parse_time(first["start_time"])
    if first_start and first_start > START_OF_DAY:
        duration = _minutes_between(START_OF_DAY, first_start)
        windows.append({
            "start_time": "09:00",
            "end_time": first["start_time"],
            "duration_minutes": duration,
        })

    for i in range(len(classes) - 1):
        current = classes[i]
        next_c = classes[i + 1]
        cur_end = _parse_time(current["end_time"])
        next_start = _parse_time(next_c["start_time"])
        if cur_end and next_start and cur_end < next_start:
            duration = _minutes_between(cur_end, next_start)
            windows.append({
                "start_time": current["end_time"],
                "end_time": next_c["start_time"],
                "duration_minutes": duration,
            })

    last = classes[-1]
    last_end = _parse_time(last["end_time"])
    if last_end and last_end < END_OF_DAY:
        duration = _minutes_between(last_end, END_OF_DAY)
        windows.append({
            "start_time": last["end_time"],
            "end_time": "17:50",
            "duration_minutes": duration,
        })

    return windows
