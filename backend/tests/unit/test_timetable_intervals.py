import pytest

from app.utils.timetable_intervals import buildBusyIntervals, minutes_since_midnight


def test_build_busy_intervals_sorts_and_merges_overlaps_and_adjacency():
    day = [
        {"courses": [{"code": "B", "name": "Class", "room": "R", "start_time": "10:00", "end_time": "11:00"}]},
        {"courses": [{"code": "A", "name": "Class", "room": "R", "start_time": "09:00", "end_time": "10:30"}]},
        {"courses": [{"code": "C", "name": "Class", "room": "R", "start_time": "11:00", "end_time": "11:30"}]},
    ]

    assert buildBusyIntervals(day, "Monday") == [{"start": 540, "end": 690}]
    assert buildBusyIntervals({"Monday": day}, "Monday") == [{"start": 540, "end": 690}]


def test_true_blank_and_configured_break_are_not_busy():
    day = [
        {"courses": [{"code": "", "name": "", "room": "", "start_time": "09:00", "end_time": "09:50"}]},
        {"courses": [{"code": "LUNCH", "name": "Lunch", "room": "Hall", "start_time": "10:00", "end_time": "10:50"}]},
    ]

    assert buildBusyIntervals(day, breakMarkers={"lunch"}) == []


def test_empty_name_with_a_room_is_always_busy():
    day = [{"courses": [{"code": "LAB-3", "name": "", "room": "APC8", "start_time": "08:50", "end_time": "09:40"}]}]

    assert buildBusyIntervals(day, treatMentoringSlotsAsFree=True) == [{"start": 530, "end": 580}]


def test_lab_style_entry_with_room_is_busy_even_when_name_is_empty():
    day = [{"courses": [{"code": "LAB-1", "name": "", "room": "C1", "start_time": "08:50", "end_time": "09:40"}]}]

    assert buildBusyIntervals(day, treatMentoringSlotsAsFree=True) == [{"start": 530, "end": 580}]


def test_mentoring_slots_are_busy_by_default_and_configurable():
    day = [{"courses": [{"code": "PKC", "name": "", "room": "", "start_time": "12:10", "end_time": "13:00"}]}]

    assert buildBusyIntervals(day) == [{"start": 730, "end": 780}]
    assert buildBusyIntervals(day, treatMentoringSlotsAsFree=True) == []


def test_invalid_times_fail_loudly():
    with pytest.raises(ValueError, match="HH:MM"):
        minutes_since_midnight("9:00")
