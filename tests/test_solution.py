## Student Name:Dieng Fatoumata 
## Student ID: 219904564

"""
Public test suite for the meeting slot suggestion exercise.

Students can run these tests locally to check basic correctness of their implementation.
The hidden test suite used for grading contains additional edge cases and will not be
available to students.
"""
import pytest
from solution import suggest_slots


def test_single_event_blocks_overlapping_slots():
    """
    Functional requirement:
    Slots overlapping an event must not be suggested.
    """
    events = [{"start": "10:00", "end": "11:00"}]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    assert "10:00" not in slots
    assert "10:30" not in slots
    assert "11:15" in slots

def test_event_outside_working_hours_is_ignored():
    """
    Constraint:
    Events completely outside working hours should not affect availability.
    """
    events = [{"start": "07:00", "end": "08:00"}]
    slots = suggest_slots(events, meeting_duration=60, day="2026-02-01")

    assert "09:00" in slots
    assert "16:00" in slots

def test_unsorted_events_are_handled():
    """
    Constraint:
    Event order should not affect correctness.
    """
    events = [
        {"start": "13:00", "end": "14:00"},
        {"start": "09:30", "end": "10:00"},
        {"start": "11:00", "end": "12:00"},
    ]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    assert  slots[1] == "10:15"
    assert "09:30" not in slots

def test_lunch_break_blocks_all_slots_during_lunch():
    """
    Constraint:
    No meeting may start during the lunch break (12:00–13:00).
    """
    events = []
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    assert "12:00" not in slots
    assert "12:15" not in slots
    assert "12:30" not in slots
    assert "12:45" not in slots

"""TODO: Add at least 5 additional test cases to test your implementation."""

def test_no_events_monday_60min_all_slots():
    events = []
    slots = suggest_slots(events, meeting_duration=60, day="Mon")
    assert slots == [
        "09:00","09:30","10:00","10:30","11:00","11:30",
        "12:00","12:30","13:00","13:30","14:00","14:30",
        "15:00","15:30","16:00"
    ]

def test_single_event_blocks_overlapping_starts():
    # Busy 10:00-11:00 should block starts that overlap it
    events = [{"start": "10:00", "end": "11:00"}]
    slots = suggest_slots(events, meeting_duration=60, day="Mon")
    # allowed: 09:00 ends exactly at 10:00 -> OK
    # blocked: 09:30, 10:00, 10:30 (all overlap 10-11)
    # allowed again: 11:00 onward
    assert slots == [
        "09:00",
        "11:00","11:30","12:00","12:30","13:00","13:30",
        "14:00","14:30","15:00","15:30","16:00"
    ]

def test_overlapping_events_are_merged():
    # Overlapping busy blocks effectively become 10:00-12:00
    events = [
        {"start": "10:00", "end": "11:30"},
        {"start": "11:00", "end": "12:00"},
    ]
    slots = suggest_slots(events, meeting_duration=60, day="Mon")
    # 09:00 OK (ends at 10:00)
    # 09:30 overlaps (ends 10:30) -> blocked
    # any start from 10:00 to 11:30 overlaps merged block -> blocked
    # 12:00 OK onward
    assert slots == [
        "09:00",
        "12:00","12:30","13:00","13:30","14:00","14:30",
        "15:00","15:30","16:00"
    ]

def test_meeting_exactly_fits_gap():
    # Gap: 11:00-12:00, meeting 60 fits only starting at 11:00
    events = [
        {"start": "09:00", "end": "11:00"},
        {"start": "12:00", "end": "17:00"},
    ]
    slots = suggest_slots(events, meeting_duration=60, day="Mon")
    assert slots == ["11:00"]

def test_meeting_too_long_for_day_returns_empty():
    # Mon work window is 8h = 480 minutes, 500 can never fit
    events = []
    slots = suggest_slots(events, meeting_duration=500, day="Mon")
    assert slots == []

def test_events_outside_work_hours_are_clamped():
    # Event before work hours should not block anything.
    # Event partially after work hours clamps to 16:30-17:00.
    events = [
        {"start": "07:00", "end": "08:30"},
        {"start": "16:30", "end": "18:00"},
    ]
    slots = suggest_slots(events, meeting_duration=30, day="Mon")
    # With 30 min duration, normally last start is 16:30.
    # But event blocks 16:30-17:00, so 16:30 should be removed.
    assert slots[-3:] == ["15:30", "16:00"]  # last valid should be 16:00
    assert "16:30" not in slots

def test_friday_shorter_hours_last_start_14_for_60min():
    events = []
    slots = suggest_slots(events, meeting_duration=60, day="Fri")
    # Fri is 09:00-15:00 so last start for 60 minutes is 14:00
    assert slots[0] == "09:00"
    assert slots[-1] == "14:00"
    assert "14:30" not in slots
