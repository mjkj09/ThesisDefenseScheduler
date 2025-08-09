# User Manual – Thesis Defense Scheduler

This guide explains how to use the **Thesis Defense Scheduler** application to create, review, and manage defense schedules.

---

## 1. Starting the Application

From the project root, activate your virtual environment and run the app.

**Windows**
```bash
.venv\Scripts\activate
python main.py
```

macOS / Linux

```bash
source .venv/bin/activate
python main.py
```
💡 If using Docker, run the container according to the INSTALLATION.md instructions.

## 2. Main Window Overview
When the application starts, the Main Window will display:

**Menu Bar**
- File – Create a new schedule, load an existing one, save to file.

- Edit – Manage faculty members, rooms, and defenses.

- View – Switch between timetable view, statistics, and conflicts view.

**Toolbar**
- Quick actions: add defense, add faculty member, refresh schedule.

**Schedule Table**
- Displays time slots, rooms, and assigned defenses.
- Color coding for rooms, conflicts, and chairman assignments.

## 3. Adding a New Defense
* Open the Edit → Defenses dialog.
* Click Add Defense.
* Fill in:
    - Student name
    - Thesis title
    - Supervisor
    - Reviewer
* Save — the defense will appear in the scheduling list.

## 4. Managing Faculty Members
* Go to Edit → Faculty Members.
* Use:
    - Add – create a new member and assign roles (Supervisor, Reviewer, Chairman).
    - Edit – update name, email, or roles.
    - Delete – remove a member (if not assigned to a defense).