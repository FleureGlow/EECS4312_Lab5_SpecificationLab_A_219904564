## Student Name: Fatoumata Dieng
## Student ID: 219904564

"""
Stub file for the meeting slot suggestion exercise.

Implement the function `suggest_slots` to return a list of valid meeting start times
on a given day, taking into account working hours, and possible specific constraints.
See the lab handout for full requirements.
"""
from typing import List, Dict
import datetime


def suggest_slots(
    events: List[Dict[str, str]],
    meeting_duration: int,
    day: str
) -> List[str]:
    """
    Suggest possible meeting start times for a given day.

    Rules implemented:
      - Working hours depend on weekday:
          Mon–Thu: 09:00–17:00
          Fri:     09:00–15:00
      - Lunch break is blocked: 12:00–13:00 (no meetings may overlap it)
      - Meetings can start on a fixed grid (every 30 minutes).
      - An event blocks time in [start, end) (end time is free).
      - Events may overlap / be unsorted.
      - `day` can be either:
          * a weekday abbreviation: "Mon", "Tue", ... "Fri"
          * a date string: "YYYY-MM-DD" (converted to weekday)

    Args:
        events: List of dicts with keys {"start": "HH:MM", "end": "HH:MM"}
        meeting_duration: Desired meeting length in minutes
        day: "Mon".."Fri" OR "YYYY-MM-DD"

    Returns:
        List of valid start times as "HH:MM" sorted ascending
    """

    # --- helpers ---
    def to_minutes(hhmm: str) -> int:
        hh, mm = hhmm.split(":")
        return int(hh) * 60 + int(mm)

    def to_hhmm(total_minutes: int) -> str:
        h = total_minutes // 60
        m = total_minutes % 60
        return f"{h:02d}:{m:02d}"

    def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
        if not intervals:
            return []
        intervals.sort(key=lambda x: x[0])
        merged = [intervals[0]]
        for s, e in intervals[1:]:
            last_e = merged[-1][1]
            if s <= last_e:  # overlap or touch
                merged[-1][1] = max(last_e, e)
            else:
                merged.append([s, e])
        return merged

    # --- basic validation ---
    if meeting_duration <= 0:
        return []

    # --- working hours ---
    WORK_HOURS = {
        "Mon": ("09:00", "17:00"),
        "Tue": ("09:00", "17:00"),
        "Wed": ("09:00", "17:00"),
        "Thu": ("09:00", "17:00"),
        "Fri": ("09:00", "15:00"),
    }

    # Allow day as either "Mon".."Fri" or "YYYY-MM-DD"
    if day not in WORK_HOURS:
        try:
            d = datetime.datetime.strptime(day, "%Y-%m-%d").date()
            day = d.strftime("%a")  # "Mon", "Tue", ...
        except ValueError:
            return []

    if day not in WORK_HOURS:
        return []

    work_start = to_minutes(WORK_HOURS[day][0])
    work_end = to_minutes(WORK_HOURS[day][1])

    # If meeting can't even fit in the day, early exit
    if work_start + meeting_duration > work_end:
        return []

    # --- build busy intervals (events + lunch), clamped to working hours ---
    busy: List[List[int]] = []

    # Add events
    for ev in events:
        try:
            s = to_minutes(ev["start"])
            e = to_minutes(ev["end"])
        except (KeyError, ValueError):
            continue

        if e <= s:
            continue

        # Clamp to working hours
        s = max(s, work_start)
        e = min(e, work_end)

        if e > s:
            busy.append([s, e])

    # Add lunch break (12:00–13:00), clamped to working hours
    lunch_start = to_minutes("12:00")
    lunch_end = to_minutes("13:00")
    ls = max(lunch_start, work_start)
    le = min(lunch_end, work_end)
    if le > ls:
        busy.append([ls, le])

    # Merge overlaps
    busy = merge_intervals(busy)

    # --- generate candidate start times on a grid ---
    SLOT_STEP = 30  # minutes (adjust if your handout says 15, 10, etc.)

    # Align first candidate to the step grid at/after work_start
    first = work_start
    rem = first % SLOT_STEP
    if rem != 0:
        first += (SLOT_STEP - rem)

    results: List[str] = []
    i = 0  # pointer into busy intervals

    t = first
    latest_start = work_end - meeting_duration
    while t <= latest_start:
        meeting_end = t + meeting_duration

        # Advance pointer past intervals that end before this start
        while i < len(busy) and busy[i][1] <= t:
            i += 1

        overlaps = False
        if i < len(busy):
            bs, be = busy[i]
            # Overlap if meeting starts before busy ends AND meeting ends after busy starts
            if t < be and meeting_end > bs:
                overlaps = True

        if not overlaps:
            results.append(to_hhmm(t))

        t += SLOT_STEP

    return results
