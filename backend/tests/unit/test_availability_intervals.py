from app.utils.availability_intervals import (
    computeAvailability,
    invertToFree,
    mergeAdjacent,
    unionBusy,
)


def test_two_users_with_overlaps_and_gaps_produce_multiple_shared_windows():
    users = [
        [{"start": 540, "end": 600}, {"start": 730, "end": 780}],
        [{"start": 570, "end": 630}, {"start": 930, "end": 980}],
    ]

    assert unionBusy(users) == [
        {"start": 540, "end": 630}, {"start": 730, "end": 780}, {"start": 930, "end": 980}
    ]
    result = computeAvailability(users, dayStart="08:00", dayEnd="18:00")
    assert result["shared_windows"] == [
        {"start": "08:00", "end": "09:00"},
        {"start": "10:30", "end": "12:10"},
        {"start": "13:00", "end": "15:30"},
        {"start": "16:20", "end": "18:00"},
    ]


def test_zero_shared_free_time():
    result = computeAvailability(
        [[{"start": 480, "end": 720}], [{"start": 720, "end": 1080}]],
        dayStart="08:00",
        dayEnd="18:00",
    )
    assert result["shared_windows"] == []
    assert result["next_slot"] is None
    assert result["longest_window"] is None


def test_user_with_no_entries_is_free_all_day():
    result = computeAvailability([[], [{"start": 600, "end": 660}]], dayStart="08:00", dayEnd="12:00")
    assert result["shared_windows"] == [
        {"start": "08:00", "end": "10:00"}, {"start": "11:00", "end": "12:00"}
    ]


def test_current_overlap_next_slot_and_members_at_different_times():
    users = [[{"start": 600, "end": 660}], [{"start": 720, "end": 780}]]
    members = [{"user_id": "a", "display_name": "Ada"}, {"user_id": "b", "display_name": "Ben"}]

    at_0900 = computeAvailability(users, now="09:00", dayStart="08:00", dayEnd="14:00", members=members)
    assert at_0900["current_overlap"] is True
    assert at_0900["next_slot"] == {"start": "11:00", "end": "12:00"}
    assert at_0900["member_availabilities"] == [
        {"user_id": "a", "display_name": "Ada", "is_free_now": True},
        {"user_id": "b", "display_name": "Ben", "is_free_now": True},
    ]

    at_1030 = computeAvailability(users, now="10:30", dayStart="08:00", dayEnd="14:00", members=members)
    assert at_1030["current_overlap"] is False
    assert at_1030["next_slot"] == {"start": "11:00", "end": "12:00"}
    assert at_1030["member_availabilities"][0]["is_free_now"] is False
    assert at_1030["member_availabilities"][1]["is_free_now"] is True

    at_1300 = computeAvailability(users, now="13:00", dayStart="08:00", dayEnd="14:00")
    assert at_1300["current_overlap"] is True
    assert at_1300["next_slot"] is None


def test_genuine_mid_day_gap_remains_free_without_tolerance():
    busy = [{"start": 670, "end": 730}, {"start": 930, "end": 980}]
    free = invertToFree(busy, "08:00", "18:00")
    assert free[1] == {"start": 730, "end": 930}  # 12:10–15:30
    assert mergeAdjacent(free) == free
