# Testing

This project uses **pytest** for automated tests that cover the core domain logic (models, time slots, conflicts) and the base scheduling utilities. GUI code is **not** exercised in tests.

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

You should see output similar to:

bash
Kopiuj
Edytuj
tests/tests_core.py ..........
N passed in 0.4s
If you see “0 tests collected”, make sure you’re running from the repository root and the tests/ folder contains tests_core.py.

What Is Tested
All tests live in tests/tests_core.py and currently verify:

Models
Person

Role assignment (test_person_roles)

Availability based on unavailable_slots (test_person_availability_simple)

Room

Name, number, capacity (test_room_capacity)

Defense

Committee members (supervisor + reviewer) (test_defense_committee)

TimeSlot

Overlap logic (test_time_slot_overlap)

ScheduleSlot

Free/busy state (test_schedule_slot_free_status)

Algorithm Core
SchedulingAlgorithm

generate_time_slots excludes breaks (test_generate_time_slots_excludes_breaks)

create_empty_schedule produces room×times combinations (test_create_empty_schedule_slots_match_rooms_times)

Conflict Detection
ConflictChecker

Person marked as unavailable triggers a conflict (test_conflict_checker_person_unavailable)

Overlapping defenses for the same person are detected (test_conflict_checker_person_overlapping_defense)

Note: Backtracking scheduling is intentionally not covered yet.


Running a Subset
Run only tests matching a keyword:

bash
Kopiuj
Edytuj
pytest -q -k conflict_checker
Run with verbose names:

bash
Kopiuj
Edytuj
pytest -v
Stop on first failure:

bash
Kopiuj
Edytuj
pytest -x


Adding Tests
Open tests/tests_core.py (or add a new file like tests/test_something.py).

Follow the Given–When–Then pattern:

python
Kopiuj
Edytuj
def test_example():
    # Given
    obj = SomeClass()

    # When
    result = obj.method()

    # Then
    assert result == expected
Run pytest -q.

Troubleshooting
Symptom	Likely Cause	Fix
0 tests collected	Wrong folder or naming	Run from repo root; ensure files named test_*.py or tests_*.py inside tests/.
ImportError: No module named src...	Python path not set	Run tests from repo root so src/ is importable.
Availability/overlap tests fail	Logic mismatch in Person.is_available_at or TimeSlot.overlaps_with	Verify unavailable_slots is used (unavailable means cannot attend) and overlap logic is symmetric.
Tkinter errors during tests	GUI got imported/executed	Keep GUI bootstrapping only in main.py; tests shouldn’t instantiate Tk.

Scope & Philosophy
✅ Focus on deterministic business rules (models, time math, conflict checks, core slot generation).

❌ Skip GUI rendering and long-running integrations.

🧪 Keep tests fast and self-contained.

If you later introduce new algorithms (e.g., backtracking), add a dedicated test file (e.g., tests/test_backtracking.py) with small deterministic scenarios that don’t rely on the GUI.