from typing import List, Tuple
from src.algorithm.scheduler import SchedulingAlgorithm, Schedule, SchedulingConflict
from src.models import Defense


class SimpleGreedyScheduler(SchedulingAlgorithm):
    """Simple greedy scheduling algorithm - schedules defenses in order."""

    def schedule(self, defenses: List[Defense]) -> Tuple[Schedule, List[SchedulingConflict]]:
        """
        Schedule defenses using simple greedy approach.
        Try to place each defense in the first available slot.
        """
        schedule = self.create_empty_schedule()
        unscheduled_defenses = []
        all_conflicts = []

        for defense in defenses:
            scheduled = False
            defense_conflicts = []

            # Try each free slot
            for slot in schedule.get_free_slots():
                can_schedule, conflicts = self.can_schedule_defense(defense, slot, schedule)

                if can_schedule:
                    # Find chairman (we know one exists from can_schedule check)
                    chairman = self.find_available_chairman(
                        slot.time_slot,
                        schedule.get_scheduled_defenses()
                    )

                    # Schedule the defense
                    schedule.add_defense(defense, slot, chairman)
                    scheduled = True
                    break
                else:
                    defense_conflicts.extend(conflicts)

            if not scheduled:
                unscheduled_defenses.append(defense)
                all_conflicts.append(SchedulingConflict(
                    f"Could not schedule defense for {defense.student_name}",
                    defense=defense
                ))
                all_conflicts.extend(defense_conflicts[:1])  # Add first conflict as example

        return schedule, all_conflicts


class PriorityGreedyScheduler(SchedulingAlgorithm):
    """Greedy scheduler with priority ordering."""

    def calculate_defense_priority(self, defense: Defense, all_defenses: List[Defense]) -> float:
        """
        Calculate priority score for defense.
        Higher score = should be scheduled earlier.
        """
        score = 0.0

        # Count how many other defenses share committee members
        shared_supervisor = sum(1 for d in all_defenses
                                if d != defense and d.supervisor == defense.supervisor)
        shared_reviewer = sum(1 for d in all_defenses
                              if d != defense and d.reviewer == defense.reviewer)

        # More constraints = higher priority
        score += shared_supervisor * 2
        score += shared_reviewer * 2

        # Check availability constraints
        supervisor_unavailable = len(defense.supervisor.unavailable_slots)
        reviewer_unavailable = len(defense.reviewer.unavailable_slots)

        score += supervisor_unavailable * 0.5
        score += reviewer_unavailable * 0.5

        return score

    def schedule(self, defenses: List[Defense]) -> Tuple[Schedule, List[SchedulingConflict]]:
        """Schedule defenses with priority ordering."""
        # Sort defenses by priority (highest first)
        sorted_defenses = sorted(
            defenses,
            key=lambda d: self.calculate_defense_priority(d, defenses),
            reverse=True
        )

        # Use simple greedy with sorted list
        return super().schedule(sorted_defenses)