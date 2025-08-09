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
  - Committee members (supervisor + reviewer) (`test_defense_committee`)
- **TimeSlot**
  - Overlap logic (`test_time_slot_overlap`)
- **ScheduleSlot**
  - Free/busy state (`test_schedule_slot_free_status`)

#### Algorithm Core
- **SchedulingAlgorithm**
  - `generate_time_slots` excludes breaks (`test_generate_time_slots_excludes_breaks`)
  - `create_empty_schedule` produces room×times combinations (`test_create_empty_schedule_slots_match_rooms_times`)

#### Conflict Detection
- **ConflictChecker**
  - Person marked as unavailable triggers a conflict (`test_conflict_checker_person_unavailable`)
  - Overlapping defenses for the same person are detected (`test_conflict_checker_person_overlapping_defense`)

> **Note:** Backtracking scheduling is intentionally **not** covered yet.

---

## How to Run

From the project root:

```bash
# (optional) activate your venv first
# Windows:
#   .venv\Scripts\activate
# macOS/Linux:
#   source .venv/bin/activate

pytest -q
