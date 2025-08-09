# User Manual – Thesis Defense Scheduler

This guide explains how to use the **Thesis Defense Scheduler** application to create, review, and manage defense schedules.

---

## 1. Starting the Application

From the project root, activate your virtual environment and run the app:

**Windows**
```bash
.venv\Scripts\activate
python main.py
macOS / Linux

bash
Kopiuj
Edytuj
source .venv/bin/activate
python main.py
💡 If using Docker, run the container according to the INSTALLATION.md instructions.

2. Main Window Overview
When the application starts, the Main Window will display:

Menu Bar

File – create a new schedule, load an existing one, save to file.

Edit – manage faculty members, rooms, and defenses.

View – switch between timetable view, statistics, and conflicts view.

Toolbar

Quick actions: add defense, add faculty member, refresh schedule.

Schedule Table

Displays time slots, rooms, and assigned defenses.

Color coding for rooms, conflicts, and chairman assignments.

3. Adding Data
3.1 Adding Faculty Members
Go to Edit → Faculty Members → Add.

Fill in:

Name

Email

Role(s) – Chairman, Supervisor, Reviewer.

Availability – select time slots when the person is available.

Click Save.

3.2 Adding Rooms
Go to Edit → Rooms → Add.

Fill in:

Name

Number

Capacity

Click Save.

3.3 Adding Defenses
Go to Edit → Defenses → Add.

Fill in:

Student Name

Thesis Title

Supervisor (must be different from Reviewer)

Reviewer

Chairman (optional – can be auto-assigned later)

Click Save.

4. Generating a Schedule
Go to File → Generate Schedule.

Choose:

Date

Start/End time

Defense duration

Breaks (optional)

Click Generate.

The Backtracking Scheduler will try to create an optimal schedule that:

Avoids conflicts

Respects availability

Assigns chairmen automatically

5. Viewing Conflicts
Go to View → Conflicts.

The system will display:

Room conflicts

Faculty availability conflicts

Overlapping defenses

6. Summary Statistics
Go to View → Statistics.

You will see:

Room utilization – how much each room is used.

Faculty workload distribution.

Number of defenses per day/time slot.

7. Saving & Loading Schedules
Save – File → Save As will store the current schedule to a .json file.

Load – File → Open will import a saved schedule.

8. Shortcuts
Action	Shortcut
New Schedule	Ctrl+N
Save Schedule	Ctrl+S
Open Schedule	Ctrl+O
Add Faculty Member	Ctrl+Shift+F
Add Defense	Ctrl+Shift+D

9. Tips
Always set availability for faculty members to avoid unnecessary conflicts.

Use color-coded view to quickly identify conflicts.

The statistics view can help balance workload before finalizing the schedule.

10. Troubleshooting
Problem	Likely Cause	Solution
Schedule generation fails	Not enough available faculty/rooms	Adjust availability, add more resources
Faculty assigned to multiple defenses at same time	Incorrect availability or overlapping slots	Verify availability in Faculty Editor
GUI doesn't start	Python/Tkinter not installed	Install Tkinter (pip install tk) or check Python installation
0 tests collected when running pytest	Wrong folder or file naming	Run from repo root; ensure files start with test_ and are inside tests/
ImportError: No module named src...	Python path not set	Run tests from repo root so src/ is importable
Availability/overlap tests fail	Logic mismatch in Person.is_available_at or TimeSlot.overlaps_with	Ensure unavailable_slots is used correctly and overlap logic is symmetric
Tkinter errors during tests	GUI code got imported in tests	Keep GUI bootstrapping in main.py only; do not instantiate Tk in tests