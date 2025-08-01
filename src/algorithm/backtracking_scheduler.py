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

    def _backtrack(self, defenses: List[Defense], index: int) -> bool:
        if index == len(defenses):
            return True

        defense = defenses[index]

        for slot in self.schedule.get_free_slots():
            can_schedule, conflicts = self.can_schedule_defense(defense, slot, self.schedule)

            if can_schedule:
                chairman = self.find_available_chairman(slot.time_slot, self.schedule.get_scheduled_defenses())
                if not chairman:
                    continue  # try next slot

                self.schedule.add_defense(defense, slot, chairman)

                if self._backtrack(defenses, index + 1):
                    return True

                self.schedule.remove_defense(defense)

        # Failed to assign current defense – record conflict
        self.conflicts.append(SchedulingConflict(
            f"Could not schedule defense for {defense.student_name}", defense=defense
        ))
        return False
