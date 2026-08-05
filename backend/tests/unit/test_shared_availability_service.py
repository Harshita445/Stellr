from app.services.shared_availability_service import getSharedAvailability


def test_adapter_uses_sections_and_preserves_phase_two_contract():
    users = [
        {"user_id": "u1", "display_name": "Ari", "section_code": "A"},
        {"user_id": "u2", "display_name": "Bea", "section_code": "B"},
    ]
    timetable = {
        "A": {"Monday": [{"courses": [{"code": "X", "name": "X", "room": "R", "start_time": "09:00", "end_time": "10:00"}]}]},
        "B": {"Monday": [{"courses": [{"code": "Y", "name": "Y", "room": "R", "start_time": "10:30", "end_time": "11:30"}]}]},
    }

    assert getSharedAvailability(users, timetable, "Monday", "10:00") == {
        "shared_windows": [
            {"start": "08:00", "end": "09:00"},
            {"start": "10:00", "end": "10:30"},
            {"start": "11:30", "end": "19:00"},
        ],
        "current_overlap": True,
        "next_slot": {"start": "11:30", "end": "19:00"},
        "longest_window": {"start": "11:30", "end": "19:00"},
        "member_availabilities": [
            {"user_id": "u1", "display_name": "Ari", "is_free_now": True},
            {"user_id": "u2", "display_name": "Bea", "is_free_now": True},
        ],
    }


def test_missing_sections_and_empty_days_are_free_within_the_day_bounds():
    users = [
        {"user_id": "u1", "display_name": "Ari", "section_code": "MISSING"},
        {"user_id": "u2", "display_name": "Bea", "section_code": "EMPTY"},
    ]
    timetable = {
        "EMPTY": {"Saturday": []},
        "OTHER": {"Saturday": [{"courses": [{"code": "X", "name": "X", "room": "R", "start_time": "09:00", "end_time": "10:00"}]}]},
    }

    result = getSharedAvailability(users, timetable, "Saturday", "09:30")
    assert result["shared_windows"] == [{"start": "08:00", "end": "19:00"}]
    assert result["current_overlap"] is True
    assert all(member["is_free_now"] for member in result["member_availabilities"])


def test_overlapping_lab_groups_are_merged_before_comparing_users():
    users = [
        {"user_id": "u1", "display_name": "Ari", "section_code": "LAB"},
        {"user_id": "u2", "display_name": "Bea", "section_code": "FREE"},
    ]
    timetable = {
        "LAB": {"Monday": [{"courses": [
            {"code": "L1", "name": "Lab", "room": "R1", "start_time": "09:00", "end_time": "10:00"},
            {"code": "L2", "name": "Lab", "room": "R2", "start_time": "09:30", "end_time": "10:30"},
        ]}]},
        "FREE": {"Monday": []},
    }

    result = getSharedAvailability(users, timetable, "Monday")
    assert result["shared_windows"] == [{"start": "08:00", "end": "09:00"}, {"start": "10:30", "end": "19:00"}]
    assert result["longest_window"] == {"start": "10:30", "end": "19:00"}


def test_midday_gap_is_preserved_as_shared_free_window():
    users = [
        {"user_id": "u1", "display_name": "Ari", "section_code": "A"},
        {"user_id": "u2", "display_name": "Bea", "section_code": "B"},
    ]
    timetable = {
        "A": {"Monday": [{"courses": [{"code": "A", "name": "A", "room": "R", "start_time": "08:00", "end_time": "12:10"}]}]},
        "B": {"Monday": [{"courses": [{"code": "B", "name": "B", "room": "R", "start_time": "15:30", "end_time": "18:00"}]}]},
    }

    result = getSharedAvailability(users, timetable, "Monday")

    assert result["shared_windows"] == [{"start": "12:10", "end": "15:30"}, {"start": "18:00", "end": "19:00"}]


def test_empty_day_entries_are_treated_as_free_all_day():
    users = [
        {"user_id": "u1", "display_name": "Ari", "section_code": "EMPTY"},
        {"user_id": "u2", "display_name": "Bea", "section_code": "BUSY"},
    ]
    timetable = {
        "EMPTY": {"Monday": []},
        "BUSY": {"Monday": [{"courses": [{"code": "X", "name": "X", "room": "R", "start_time": "09:00", "end_time": "10:00"}]}]},
    }

    result = getSharedAvailability(users, timetable, "Monday", "09:30")

    assert any(member["user_id"] == "u1" and member["is_free_now"] is True for member in result["member_availabilities"])
    assert any(member["user_id"] == "u2" and member["is_free_now"] is False for member in result["member_availabilities"])


def test_non_overlapping_free_time_yields_no_shared_windows():
    users = [
        {"user_id": "u1", "display_name": "Ari", "section_code": "A"},
        {"user_id": "u2", "display_name": "Bea", "section_code": "B"},
    ]
    timetable = {
        "A": {"Monday": [{"courses": [{"code": "A", "name": "A", "room": "R", "start_time": "08:00", "end_time": "09:00"}]}]},
        "B": {"Monday": [{"courses": [{"code": "B", "name": "B", "room": "R", "start_time": "09:00", "end_time": "10:00"}]}]},
    }

    result = getSharedAvailability(users, timetable, "Monday")

    assert result["shared_windows"] == [{"start": "10:00", "end": "19:00"}]
    assert result["current_overlap"] is False
    assert result["next_slot"] == {"start": "10:00", "end": "19:00"}
    assert result["longest_window"] == {"start": "10:00", "end": "19:00"}


def test_three_users_are_all_considered_in_the_union():
    users = [
        {"user_id": "u1", "display_name": "Ari", "section_code": "A"},
        {"user_id": "u2", "display_name": "Bea", "section_code": "B"},
        {"user_id": "u3", "display_name": "Cia", "section_code": "C"},
    ]
    timetable = {
        "A": {"Monday": [{"courses": [{"code": "A", "name": "A", "room": "R", "start_time": "09:00", "end_time": "10:00"}]}]},
        "B": {"Monday": [{"courses": [{"code": "B", "name": "B", "room": "R", "start_time": "11:00", "end_time": "12:00"}]}]},
        "C": {"Monday": [{"courses": [{"code": "C", "name": "C", "room": "R", "start_time": "13:00", "end_time": "14:00"}]}]},
    }

    result = getSharedAvailability(users, timetable, "Monday")

    assert result["shared_windows"] == [
        {"start": "08:00", "end": "09:00"},
        {"start": "10:00", "end": "11:00"},
        {"start": "12:00", "end": "13:00"},
        {"start": "14:00", "end": "19:00"},
    ]


def test_now_on_boundary_is_treated_as_free_when_window_starts_there():
    users = [
        {"user_id": "u1", "display_name": "Ari", "section_code": "A"},
        {"user_id": "u2", "display_name": "Bea", "section_code": "B"},
    ]
    timetable = {
        "A": {"Monday": [{"courses": [{"code": "A", "name": "A", "room": "R", "start_time": "09:00", "end_time": "10:00"}]}]},
        "B": {"Monday": [{"courses": [{"code": "B", "name": "B", "room": "R", "start_time": "11:00", "end_time": "12:00"}]}]},
    }

    result = getSharedAvailability(users, timetable, "Monday", "10:00")

    assert result["current_overlap"] is True


def test_now_after_last_shared_window_returns_no_next_slot():
    users = [
        {"user_id": "u1", "display_name": "Ari", "section_code": "A"},
        {"user_id": "u2", "display_name": "Bea", "section_code": "B"},
    ]
    timetable = {
        "A": {"Monday": [{"courses": [{"code": "A", "name": "A", "room": "R", "start_time": "09:00", "end_time": "10:00"}]}]},
        "B": {"Monday": [{"courses": [{"code": "B", "name": "B", "room": "R", "start_time": "11:00", "end_time": "12:00"}]}]},
    }

    result = getSharedAvailability(users, timetable, "Monday", "12:00")

    assert result["next_slot"] is None


def test_day_bounds_use_fixed_institution_window_for_pre_class_free_time():
    users = [
        {"user_id": "u1", "display_name": "Ari", "section_code": "A"},
        {"user_id": "u2", "display_name": "Bea", "section_code": "B"},
    ]
    timetable = {
        "A": {"Monday": [{"courses": [{"code": "A", "name": "A", "room": "R", "start_time": "10:30", "end_time": "11:30"}]}]},
        "B": {"Monday": [{"courses": [{"code": "B", "name": "B", "room": "R", "start_time": "11:00", "end_time": "12:00"}]}]},
    }

    result = getSharedAvailability(users, timetable, "Monday")

    assert result["shared_windows"] == [{"start": "08:00", "end": "10:30"}, {"start": "12:00", "end": "19:00"}]
