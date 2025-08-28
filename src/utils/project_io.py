import json
from dataclasses import asdict
from datetime import datetime, date
from typing import List, Tuple, Optional, Dict

from src.models import Person, Defense, Room, TimeSlot, SessionParameters, Role
from src.algorithm.scheduler import Schedule, ScheduleSlot, SchedulingAlgorithm


# ---------- helpers for datetime ----------

def _dt_to_str(dt: datetime) -> str:
    return dt.isoformat(timespec="minutes")


def _dt_from_str(s: str) -> datetime:
    # akceptuj pełne ISO albo bez sekund
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return datetime.strptime(s, "%Y-%m-%d %H:%M")


def _serialize_timeslot(ts: TimeSlot) -> dict:
    return {"start": _dt_to_str(ts.start), "end": _dt_to_str(ts.end)}


def _deserialize_timeslot(d: dict) -> TimeSlot:
    return TimeSlot(start=_dt_from_str(d["start"]), end=_dt_from_str(d["end"]))


# ---------- SAVE ----------

def save_project(
        filepath: str,
        persons: List[Person],
        defenses: List[Defense],
        rooms: List[Room],
        session_parameters: Optional[SessionParameters],
) -> None:
    """Zapisuje pełny stan projektu do JSON."""
    if not session_parameters:
        raise ValueError("Session parameters are required to save a project")

    data = {
        "version": 1,
        "session_parameters": {
            "session_date": session_parameters.session_date.isoformat(),
            "start_time": session_parameters.start_time,
            "end_time": session_parameters.end_time,
            "defense_duration": session_parameters.defense_duration,
            "room_count": session_parameters.room_count,
            "breaks": [_serialize_timeslot(b) for b in (session_parameters.breaks or [])],
        },
        "rooms": [
            {"name": r.name, "number": r.number, "capacity": r.capacity} for r in rooms
        ],
        "persons": [
            {
                "name": p.name,
                "email": p.email,
                "roles": [role.value for role in p.roles],
                "unavailable": [_serialize_timeslot(ts) for ts in (p.unavailable_slots or [])],
            }
            for p in persons
        ],
        "defenses": [],
    }

    for d in defenses:
        item = {
            "student_name": d.student_name,
            "thesis_title": d.thesis_title,
            "supervisor_email": d.supervisor.email,
            "reviewer_email": d.reviewer.email,
        }
        if d.time_slot and d.room:
            item["scheduled"] = {
                "time_slot": _serialize_timeslot(d.time_slot),
                "room_number": d.room.number,
                "chairman_email": d.chairman.email if d.chairman else None,
            }
        else:
            item["scheduled"] = None
        data["defenses"].append(item)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------- LOAD ----------

def load_project(filepath: str) -> Tuple[List[Person], List[Defense], List[Room], SessionParameters, Schedule]:
    """Wczytuje projekt z JSON i odtwarza pełny Schedule (siatka slotów + przydziały)."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    sp = data["session_parameters"]
    params = SessionParameters(
        session_date=date.fromisoformat(sp["session_date"]),
        start_time=sp["start_time"],
        end_time=sp["end_time"],
        defense_duration=int(sp["defense_duration"]),
        room_count=int(sp["room_count"]),
        breaks=[_deserialize_timeslot(b) for b in (sp.get("breaks") or [])],
    )

    rooms = [Room(r["name"], r["number"], int(r.get("capacity", 20))) for r in data["rooms"]]

    # persons
    persons: List[Person] = []
    for p in data["persons"]:
        roles = {Role(role_str) for role_str in (p.get("roles") or [])}
        person = Person(name=p["name"], email=p["email"], roles=roles)
        person.unavailable_slots = [_deserialize_timeslot(ts) for ts in (p.get("unavailable") or [])]
        persons.append(person)
    person_by_email: Dict[str, Person] = {p.email: p for p in persons}

    # defenses
    defenses: List[Defense] = []
    for d in data["defenses"]:
        sup = person_by_email[d["supervisor_email"]]
        rev = person_by_email[d["reviewer_email"]]
        df = Defense(student_name=d["student_name"], thesis_title=d["thesis_title"], supervisor=sup, reviewer=rev)

        sch = d.get("scheduled")
        if sch:
            # przypniemy dopiero po zbudowaniu siatki slotów
            df.time_slot = _deserialize_timeslot(sch["time_slot"])
            df.room = next((r for r in rooms if r.number == sch["room_number"]), None)
            ch_email = sch.get("chairman_email")
            df.chairman = person_by_email.get(ch_email) if ch_email else None
        defenses.append(df)

    # zbuduj pusty schedule (pełna siatka)
    available_chairmen = [p for p in persons if p.can_be_chairman()]
    helper = SchedulingAlgorithm(parameters=params, rooms=rooms, available_chairmen=available_chairmen)
    schedule = helper.create_empty_schedule()

    # wstaw obrony do odpowiadających slotów (po start/end i numerze sali)
    slots_by_key: Dict[tuple, ScheduleSlot] = {
        (s.time_slot.start, s.time_slot.end, s.room.number): s for s in schedule.slots
    }

    for d in defenses:
        if d.time_slot and d.room:
            key = (d.time_slot.start, d.time_slot.end, d.room.number)
            slot = slots_by_key.get(key)
            if slot:
                # jeśli nie ma przewodniczącego w pliku, spróbuj dobrać dostępnego
                chairman = d.chairman
                if chairman is None:
                    chairman = helper.find_available_chairman(slot.time_slot, schedule.get_scheduled_defenses())
                schedule.add_defense(d, slot, chairman if chairman else available_chairmen[0] if available_chairmen else None)

    return persons, defenses, rooms, params, schedule
