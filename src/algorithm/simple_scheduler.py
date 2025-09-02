from typing import List, Tuple
from src.algorithm.scheduler import SchedulingAlgorithm, Schedule, SchedulingConflict
from src.models import Defense


class SimpleGreedyScheduler(SchedulingAlgorithm):
    """Schedules in given order using the first feasible slot."""

    def schedule(self, defenses: List[Defense]) -> Tuple[Schedule, List[SchedulingConflict]]:
        schedule = self.create_empty_schedule()
        unresolved: List[SchedulingConflict] = []

        for defense in defenses:
            placed = False
            for slot in schedule.get_free_slots():
                ok, _ = self.can_schedule_defense(defense, slot, schedule)
                if not ok:
                    continue

                # we know a chairman exists because can_schedule_defense() checked it
                chairman = self.find_available_chairman(
                    defense, slot.time_slot, schedule.get_scheduled_defenses()
                )
                if not chairman:
                    continue

                schedule.add_defense(defense, slot, chairman)
                placed = True
                break

            if not placed:
                unresolved.append(SchedulingConflict(f"Could not schedule defense for {defense.student_name}", defense))
        return schedule, unresolved


class PriorityGreedyScheduler(SimpleGreedyScheduler):
    """Greedy with simple priority (more constrained first)."""

    def _priority(self, defense: Defense, all_defenses: List[Defense]) -> float:
        # more shared people -> schedule earlier
        shared_sup = sum(1 for d in all_defenses if d is not defense and d.supervisor.email == defense.supervisor.email)
        shared_rev = sum(1 for d in all_defenses if d is not defense and d.reviewer.email == defense.reviewer.email)

        # number of declared unavailabilities
        sup_unav = len(defense.supervisor.unavailable_slots)
        rev_unav = len(defense.reviewer.unavailable_slots)

        return shared_sup * 2 + shared_rev * 2 + 0.5 * (sup_unav + rev_unav)

    def schedule(self, defenses: List[Defense]) -> Tuple[Schedule, List[SchedulingConflict]]:
        ordered = sorted(defenses, key=lambda d: self._priority(d, defenses), reverse=True)
        return super().schedule(ordered)
