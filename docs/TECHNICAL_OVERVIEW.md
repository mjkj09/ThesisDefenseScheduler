# Technical Overview

## Layers

- **models/**
  - `Person` – name, email, roles (`SUPERVISOR`, `REVIEWER`, `CHAIRMAN`), unavailability slots, `is_available_at(TimeSlot)`, `can_be_chairman()`
  - `Defense` – student, thesis title, supervisor, reviewer, chairman (optional), assigned `TimeSlot` and `Room`
  - `Room` – name, number, capacity
  - `TimeSlot` – start/end, `duration`, `overlaps_with`
  - `SessionParameters` – session date, start/end time, defense duration, room count, breaks
  - `Role` – role enum (`SUPERVISOR`, `REVIEWER`, `CHAIRMAN`)

- **algorithm/**
  - `ScheduleSlot` – (TimeSlot, Room, optional Defense)
  - `Schedule` – list of slots, add/remove defenses
  - `ConflictChecker` – checks person availability and slot occupancy
  - `SchedulingAlgorithm` – generates time slots, creates empty schedule, finds available chairman
  - `BacktrackingScheduler` – advanced backtracking scheduling (not fully integrated)

- **gui/**
  - `main_window.py` – menu, tabs, renders schedule
  - Dialogs: persons, defenses, availability, rooms, parameters, CSV import

- **utils/**
  - `csv_handler.py` – import/export Persons/Defenses
  - `project_io.py` – save/load full project (JSON)
  - `schedule_exporter.py` – export schedule to CSV, JSON, PDF
  - `validators.py` – validation (email, conflicts, unavailability, chairman role)

---

## Scheduling Flow

1. User sets `SessionParameters` and provides input data (persons, defenses, rooms).
2. Algorithm:
   - `generate_time_slots()` – slices the day into slots, skipping breaks.
   - `create_empty_schedule()` – multiplies slots by rooms.
   - For each defense:
     - `can_schedule_defense` → `ConflictChecker.check_defense_conflicts` (supervisor + reviewer + chairman availability).
     - If ok → `Schedule.add_defense()`.
3. GUI displays result grouped by `TimeSlot`.

---

## Design Notes

- **Conflicts** are detected only with `TimeSlot.overlaps_with`.
- **Chairman** must have `CHAIRMAN` role and be available.
- **Backtracking** scheduling can be added later, core logic uses `SchedulingAlgorithm`.
