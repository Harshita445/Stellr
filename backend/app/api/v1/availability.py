"""Availability (Alignment) API routes.

Computes shared free time windows between users.
Two comparison modes:
  - Friend: 2-person comparison between current user and a friend.
  - Group:  aggregate comparison across all group members.

Response always contains today's shared windows, current overlap status,
next common slot, and longest window — all returned as actual clock times
(HH:MM) so the frontend never needs to know slot math.

TODO (future scope):
  - Section-wide comparison: GET /api/v1/availability/section
"""

from datetime import date, datetime, time
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    get_availability_service,
    get_current_user,
)
from app.models.timeslot import DAYS_OF_WEEK
from app.schemas.availability.responses import (
    AvailabilityResponse,
    MemberAvailability,
    SharedWindow,
)
from app.services.availability_service import AvailabilityService

router = APIRouter(tags=["Availability"])


def _today_day_of_week() -> int:
    """Return the ISO day of week (0=Monday) for today."""
    return date.today().weekday()


def _now_time() -> time:
    return datetime.now().time()


def _to_response(result: dict) -> AvailabilityResponse:
    member_availabilities_raw = result.get("member_availabilities", [])
    member_availabilities = [
        MemberAvailability(**m) for m in member_availabilities_raw
    ]
    return AvailabilityResponse(
        shared_windows=[
            SharedWindow(start=w["start"], end=w["end"])
            for w in result["shared_windows"]
        ],
        current_overlap=result["current_overlap"],
        next_slot=(
            SharedWindow(
                start=result["next_slot"]["start"],
                end=result["next_slot"]["end"],
            )
            if result["next_slot"]
            else None
        ),
        longest_window=(
            SharedWindow(
                start=result["longest_window"]["start"],
                end=result["longest_window"]["end"],
            )
            if result["longest_window"]
            else None
        ),
        member_availabilities=member_availabilities,
    )


@router.get("/friend/{friend_id}", response_model=AvailabilityResponse)
async def compare_with_friend(
    friend_id: UUID,
    current_user: dict = Depends(get_current_user),
    availability_service: AvailabilityService = Depends(get_availability_service),
):
    result = await availability_service.compare_with_friend(
        user_id=current_user["user_id"],
        friend_id=friend_id,
        day_of_week=_today_day_of_week(),
        now_time=_now_time(),
    )
    return _to_response(result)


@router.get("/group/{group_id}", response_model=AvailabilityResponse)
async def compare_group(
    group_id: UUID,
    current_user: dict = Depends(get_current_user),
    availability_service: AvailabilityService = Depends(get_availability_service),
):
    result = await availability_service.get_group_overlap(
        group_id=group_id,
        day_of_week=_today_day_of_week(),
        now_time=_now_time(),
    )
    return _to_response(result)
