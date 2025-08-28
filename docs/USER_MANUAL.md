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

**macOS / Linux**
```bash
source .venv/bin/activate
python main.py
```

💡 If using Docker, run the container according to the INSTALLATION.md instructions.

---

## 2. Main Window Overview

When the application starts, the Main Window will display:

**Menu Bar**
- **File** – Create a new schedule, open an existing one, save to JSON file.
- **Edit** – Manage faculty members, rooms, defenses, and session parameters.
- **View** – Switch between timetable view, statistics, and conflicts view.

**Toolbar**
- Quick actions: add defense, add faculty member, refresh schedule.

**Schedule Table**
- Displays time slots, rooms, and assigned defenses.
- Color coding for rooms and conflicts.

---

## 3. Adding a New Defense

- Open **Edit → Defenses**.
- Click **Add Defense**.
- Fill in:
  - Student name
  - Thesis title
  - Supervisor
  - Reviewer
- Save — the defense will appear in the scheduling list.

---

## 4. Managing Faculty Members

- Go to **Edit → Faculty Members**.
- Options:
  - **Add** – create a new member and assign roles (Supervisor, Reviewer, Chairman).
  - **Edit** – update name, email, or roles.
  - **Delete** – remove a member (if not assigned to a defense).

---

## 5. Managing Rooms

- Go to **Edit → Rooms**.
- Define:
  - Room name
  - Room number
  - Capacity
- Save changes.

---

## 6. Generating a Schedule

- Go to **File → New Schedule**.
- Set:
  - Session date
  - Start and end times
  - Defense duration
  - Breaks
  - Number of rooms
- Click **Generate Schedule**.  
The system will create empty schedule slots matching your parameters.

---

## 7. Assigning Defenses to Slots

- Drag and drop a defense into a free slot.
- The system will:
  - Prevent conflicts (person unavailable, overlapping times, chairman conflicts).
  - Highlight invalid assignments in red.

---

## 8. Viewing Conflicts

- Go to **View → Conflicts**.
- The table will list:
  - Person unavailable
  - Overlapping defenses
  - Room double-booking
  - Chairman without proper role

---

## 9. Saving and Loading Schedules

- **Save**: File → Save (JSON format).
- **Load**: File → Open (restore schedule from JSON).

---

## 10. Tips & Shortcuts

- **CTRL+S** – Save schedule
- **CTRL+O** – Open schedule
- **Double-click** on a slot – edit assignment
- **Refresh** button – recalculate conflicts
