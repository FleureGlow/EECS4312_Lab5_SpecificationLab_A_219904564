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
    Grid: 30 minutes
    """
    events = [{"start": "10:00", "end": "11:00"}]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-03")  # Tue

    assert "10:00" not in slots
    assert "10:30" not in slots
    assert "11:00" in slots


def test_event_outside_working_hours_is_ignored():
    """
    Constraint:
    Events completely outside working hours should not affect availability.
    """
    events = [{"start": "07:00", "end": "08:00"}]
    slots = suggest_slots(events, meeting_duration=60, day="2026-02-03")  # Tue

    assert "09:00" in slots
    assert "16:00" in slots


def test_unsorted_events_are_handled():
    """
    Constraint:
    Event order should not affect correctness.
    Grid: 30 minutes
    """
    events = [
        {"start": "13:00", "end": "14:00"},
        {"start": "09:30", "end": "10:00"},
        {"start": "11:00", "end": "12:00"},
    ]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-03")  # Tue

    # 09:30 should be blocked by the event 09:30-10:00
    assert "09:30" not in slots
    # Next possible start after that block (and respecting 30-min grid) is 10:00
    assert "10:00" in slots


def test_lunch_break_blocks_all_slots_during_lunch():
    """
    Constraint:
    No meeting may start during the lunch break (12:00–13:00).
    With 30-min grid, that means 12:00 and 12:30 must not appear.
    """
    events = []
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-03")  # Tue

    assert "12:00" not in slots
    assert "12:30" not in slots
    assert "11:30" in slots
    assert "13:00" in slots


# -----------------------------
# Additional tests (>= 5)
# -----------------------------

def test_no_events_monday_60min_slots_exclude_lunch():
    """
    Mon working hours 09:00–17:00, 30-min grid, lunch blocks 12:00–13:00.
    For 60 min meetings, last start is 16:00.
    Starts at 11:30 would overlap lunch (11
