# Testing

This project uses **pytest** for automated tests that cover the core domain logic (models, time slots, conflicts) and the base scheduling utilities.  
GUI code is **not** exercised in tests.

---

## Technical Overview of Tests

The tests focus on **deterministic business logic** and **core scheduling utilities**, avoiding GUI and long-running processes.

### What Is Tested

#### Models
- **Person**
  - Role assignment (`test_person_roles`)
  - Availability based on `unavailable_slots` (`test_person_availability_simple`)
- **Room**
  - Name, number, capacity (`test_room_capacity`)
- **Defense**
  - Committee members (supervisor + reviewer, optional chairman) (`test_defense_committee`)
- **TimeSlot**
  - Overlap logic (`test_time_slot_overlap`)
- **ScheduleSlot**
  - Free/busy state (`test_schedule_slot_free_status`)

#### Algorithm Core
- **SchedulingAlgorithm**
  - `generate_time_slots` excludes breaks (`test_generate_time_slots_excludes_breaks`)
  - `create_empty_schedule` produces room × times combinations (`test_create_empty_schedule_slots_match_rooms_times`)

#### Conflict Detection
- **ConflictChecker**
  - Person marked as unavailable triggers a conflict (`test_conflict_checker_person_unavailable`)
  - Overlapping defenses for the same person are detected (`test_conflict_checker_person_overlapping_defense`)

#### Utilities (planned tests)
- **CSVHandler** – import/export of Persons and Defenses
- **Project I/O** – save/load project state in JSON
- **ScheduleExporter** – export to CSV, JSON, PDF
- **Validator** – email validation, defense completeness, conflicts, unavailability, chairman role

> **Note:** Backtracking scheduling is intentionally **not** covered yet.

---

## How to Run

From the project root:

```bash
pytest -q
```

You should see output similar to:

```bash
tests/tests_core.py ..........
N passed in 0.4s
```

If you see “0 tests collected”, make sure you’re running from the repository root and the tests/ folder contains test files.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| **0 tests collected** | Wrong folder or naming | Run from repo root; ensure files named `test_*.py` or `tests_*.py` inside `tests/`. |
| **ImportError: No module named src...** | Python path not set | Run tests from repo root so `src/` is importable. |
| **Availability/overlap tests fail** | Logic mismatch in `Person.is_available_at` or `TimeSlot.overlaps_with` | Verify `unavailable_slots` is used correctly (unavailable means cannot attend) and overlap logic is symmetric. |
| **Tkinter errors during tests** | GUI got imported/executed | Keep GUI bootstrapping only in `main.py`; tests shouldn’t instantiate `Tk`. |
