from typing import List, Tuple
from src.models import Defense
from src.algorithm.scheduler import Schedule, SchedulingConflict, SchedulingAlgorithm


class BacktrackingScheduler(SchedulingAlgorithm):
    def _feasible_slots(self, defense: Defense, schedule: Schedule):
        for slot in schedule.get_free_slots():
            ok, _ = self.can_schedule_defense(defense, slot, schedule)
            if ok:
                yield slot

    def _domain_size(self, defense: Defense, schedule: Schedule) -> int:
        return sum(1 for _ in self._feasible_slots(defense, schedule)) or 10_000

    def schedule(self, defenses: List[Defense]) -> Tuple[Schedule, List[SchedulingConflict]]:
        schedule = self.create_empty_schedule()
        conflicts: List[SchedulingConflict] = []

        remaining = list(defenses)
        remaining.sort(key=lambda d: self._domain_size(d, schedule))

        if self._bt(schedule, remaining, conflicts):
            return schedule, []
        return schedule, conflicts

    def _bt(self, schedule: Schedule, remaining: List[Defense],
            conflicts: List[SchedulingConflict]) -> bool:
        if not remaining:
            return True

        defense = remaining[0]
        for slot in self._feasible_slots(defense, schedule):
            chairman = self.find_available_chairman(defense, slot.time_slot, schedule.get_scheduled_defenses())
            if not chairman:
                continue
            schedule.add_defense(defense, slot, chairman)
            if self._bt(schedule, remaining[1:], conflicts):
                return True
            schedule.remove_defense(defense)

        conflicts.append(SchedulingConflict(f"Could not schedule defense for {defense.student_name}", defense))
        return False
