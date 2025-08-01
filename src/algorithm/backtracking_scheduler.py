from typing import List, Tuple, Optional
from copy import deepcopy

from src.models import Defense, Person
from src.models.session_parameters import SessionParameters
from src.models.room import Room
from src.models.time_slot import TimeSlot
from src.algorithm.simple_scheduler import Schedule, SchedulingConflict, SchedulingAlgorithm


class BacktrackingScheduler(SchedulingAlgorithm):
    def schedule(self, defenses: List[Defense]) -> Tuple[Schedule, List[SchedulingConflict]]:
        defenses = sorted(defenses, key=self._defense_heuristic)
        self.schedule = self.create_empty_schedule()
        self.conflicts: List[SchedulingConflict] = []

        if self._backtrack(defenses, 0):
            return self.schedule, []
        else:
            return self.schedule, self.conflicts
