# Technical Overview

## Layers
- **models/**
  - `Person` – roles, unavailability, `is_available_at(TimeSlot)`
  - `Defense` – student, topic, supervisor, reviewer, chairman (optional)
  - `Room` – name, number, capacity
  - `TimeSlot` – start/end, `overlaps_with`
  - `SessionParameters` – date, times, duration, room count, breaks
- **algorithm/**
  - `ScheduleSlot` – (TimeSlot, Room, optional Defense)
  - `Schedule` – list of slots, add/remove defenses
  - `ConflictChecker` – checks person availability + slot occupancy
  - `SchedulingAlgorithm` – generates time slots, creates empty schedule, checks placement
  - `SimpleGreedyScheduler`, `PriorityGreedyScheduler`
- **gui/**
  - `main_window.py` – menu, tabs, renders schedule
  - Dialogs: persons, defenses, availability, rooms, parameters, CSV import
- **utils/**
  - `csv_handler.py` – import/export Persons/Defenses
  - `validators.py` – basic validation (email, final schedule conflicts)

## Scheduling Flow
1. User sets `SessionParameters` and provides input data (persons, defenses).
2. Algorithm:
   - `generate_time_slots()` – slices the day into slots, skipping breaks.
   - `create_empty_schedule()` – multiplies slots by rooms.
   - For each defense:
     - `can_schedule_defense` → `ConflictChecker.check_defense_conflicts` (supervisor + reviewer) and chairman availability.
     - If ok → `Schedule.add_defense()`.
3. GUI displays result grouped by `TimeSlot`.

## Design Notes
- **Conflicts** are calculated only with `TimeSlot.overlaps_with`.
- **Chairman** assigned per-slot from available list (role + no conflict).
- **PriorityGreedy** – priority = shared people + unavailability count.

## Limitations
- Schedule export to CSV/JSON/PDF – to be implemented.
- Backtracking algorithm – not included in this release.
