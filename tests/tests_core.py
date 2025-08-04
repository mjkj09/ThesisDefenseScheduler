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

