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


