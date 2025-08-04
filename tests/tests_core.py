import pytest
from datetime import datetime, timedelta

from src.models.person import Person, Role
from src.models.room import Room
from src.models.time_slot import TimeSlot
from src.models.defense import Defense
from src.models.session_parameters import SessionParameters
from src.algorithm.scheduler import SchedulingAlgorithm
from src.algorithm.scheduler import ScheduleSlot
from src.algorithm.scheduler import ConflictChecker

# ---------- MODELE ----------

def test_person_roles():
    p = Person("Alice", "alice@example.com", roles=[Role.CHAIRMAN])
    assert Role.CHAIRMAN in p.roles

def test_room_capacity():
    r = Room("Sala A", "001", 40)
    assert r.name == "Sala A"
    assert r.number == "001"
    assert r.capacity == 40

def test_defense_committee():
    supervisor = Person("Dr. A", "a@example.com", roles=[Role.SUPERVISOR])
    reviewer = Person("Dr. B", "b@example.com", roles=[Role.REVIEWER])
    d = Defense("Student X", "Topic", supervisor=supervisor, reviewer=reviewer)
    committee = d.get_committee()
    assert supervisor in committee
    assert reviewer in committee

def test_time_slot_overlap():
    now = datetime.now()
    ts1 = TimeSlot(start=now, end=now + timedelta(hours=1))
    ts2 = TimeSlot(start=now + timedelta(minutes=30), end=now + timedelta(hours=1, minutes=30))
    assert ts1.overlaps_with(ts2) is True

    ts3 = TimeSlot(start=now + timedelta(hours=2), end=now + timedelta(hours=3))
    assert ts1.overlaps_with(ts3) is False

def test_person_availability_simple():
    p = Person("Bob", "bob@example.com", roles=[Role.SUPERVISOR])
    now = datetime.now()
    slot = TimeSlot(now, now + timedelta(hours=1))
    other = TimeSlot(now + timedelta(hours=2), now + timedelta(hours=3))
    p.unavailable_slots = [slot]
    assert p.is_available_at(slot) is False
    assert p.is_available_at(other) is True

def test_schedule_slot_free_status():
    slot = ScheduleSlot(time_slot=TimeSlot(datetime.now(), datetime.now() + timedelta(hours=1)),
                        room=Room("Sala X", "X1", 20))
    assert slot.is_free() is True

    supervisor = Person("Dr. S", "s@example.com", roles=[Role.SUPERVISOR])
    reviewer = Person("Dr. R", "r@example.com", roles=[Role.REVIEWER])
    defense = Defense("Student Y", "Thesis", supervisor=supervisor, reviewer=reviewer)
    slot.defense = defense
    assert slot.is_free() is False

