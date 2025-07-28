from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from src.models import Person, Defense, Room, TimeSlot, SessionParameters


@dataclass
class ScheduleSlot:
    """Represents a single slot in the schedule."""
    time_slot: TimeSlot
    room: Room
    defense: Optional[Defense] = None

    def is_free(self) -> bool:
        """Check if this slot is free."""
        return self.defense is None


@dataclass
class Schedule:
    """Represents complete schedule for defense session."""
    slots: List[ScheduleSlot] = field(default_factory=list)

    def add_defense(self, defense: Defense, slot: ScheduleSlot, chairman: Person) -> None:
        """Assign defense to a slot with chairman."""
        defense.time_slot = slot.time_slot
        defense.room = slot.room
        defense.chairman = chairman
        slot.defense = defense

    def get_scheduled_defenses(self) -> List[Defense]:
        """Get all scheduled defenses."""
        return [slot.defense for slot in self.slots if slot.defense]

    def get_free_slots(self) -> List[ScheduleSlot]:
        """Get all free slots."""
        return [slot for slot in self.slots if slot.is_free()]

    def remove_defense(self, defense: Defense) -> None:
        """Remove defense from schedule."""
        for slot in self.slots:
            if slot.defense == defense:
                slot.defense = None
                defense.time_slot = None
                defense.room = None
                defense.chairman = None
                break


class SchedulingConflict:
    """Represents a scheduling conflict."""

    def __init__(self, message: str, defense: Optional[Defense] = None,
                 person: Optional[Person] = None, time_slot: Optional[TimeSlot] = None):
        self.message = message
        self.defense = defense
        self.person = person
        self.time_slot = time_slot

    def __str__(self):
        return self.message


class ConflictChecker:
    """Checks for scheduling conflicts."""

    @staticmethod
    def check_person_availability(person: Person, time_slot: TimeSlot,
                                  scheduled_defenses: List[Defense]) -> Optional[SchedulingConflict]:
        """Check if person is available at given time."""
        # Check personal unavailability
        if not person.is_available_at(time_slot):
            return SchedulingConflict(
                f"{person.name} is not available at {time_slot}",
                person=person, time_slot=time_slot
            )

        # Check if person is already scheduled at this time
        for defense in scheduled_defenses:
            if defense.time_slot and defense.time_slot.overlaps_with(time_slot):
                if person in defense.get_committee():
                    return SchedulingConflict(
                        f"{person.name} is already scheduled for {defense.student_name}'s defense",
                        defense=defense, person=person, time_slot=time_slot
                    )

        return None

    @staticmethod
    def check_defense_conflicts(defense: Defense, time_slot: TimeSlot,
                                scheduled_defenses: List[Defense]) -> List[SchedulingConflict]:
        """Check all conflicts for scheduling a defense."""
        conflicts = []

        # Check supervisor availability
        conflict = ConflictChecker.check_person_availability(
            defense.supervisor, time_slot, scheduled_defenses
        )
        if conflict:
            conflicts.append(conflict)

        # Check reviewer availability
        conflict = ConflictChecker.check_person_availability(
            defense.reviewer, time_slot, scheduled_defenses
        )
        if conflict:
            conflicts.append(conflict)

        return conflicts


class SchedulingAlgorithm:
    """Base class for scheduling algorithms."""

    def __init__(self, parameters: SessionParameters, rooms: List[Room],
                 available_chairmen: List[Person]):
        self.parameters = parameters
        self.rooms = rooms
        self.available_chairmen = available_chairmen
        self.conflict_checker = ConflictChecker()

    def generate_time_slots(self) -> List[TimeSlot]:
        """Generate all possible time slots for the session."""
        slots = []
        current_date = self.parameters.session_date

        # Parse start and end times
        start_hour, start_min = map(int, self.parameters.start_time.split(':'))
        end_hour, end_min = map(int, self.parameters.end_time.split(':'))

        current_time = datetime.combine(current_date, datetime.min.time().replace(
            hour=start_hour, minute=start_min
        ))
        end_time = datetime.combine(current_date, datetime.min.time().replace(
            hour=end_hour, minute=end_min
        ))

        defense_duration = timedelta(minutes=self.parameters.defense_duration)

        while current_time + defense_duration <= end_time:
            # Check if this time is not during a break
            slot_end = current_time + defense_duration
            time_slot = TimeSlot(start=current_time, end=slot_end)

            # Skip if overlaps with break
            is_break = False
            for break_slot in self.parameters.breaks:
                if time_slot.overlaps_with(break_slot):
                    is_break = True
                    break

            if not is_break:
                slots.append(time_slot)

            current_time = slot_end

        return slots

    def create_empty_schedule(self) -> Schedule:
        """Create empty schedule with all available slots."""
        schedule = Schedule()
        time_slots = self.generate_time_slots()

        for time_slot in time_slots:
            for room in self.rooms[:self.parameters.room_count]:
                schedule.slots.append(ScheduleSlot(time_slot=time_slot, room=room))

        return schedule

    def find_available_chairman(self, time_slot: TimeSlot,
                                scheduled_defenses: List[Defense]) -> Optional[Person]:
        """Find available chairman for given time slot."""
        for chairman in self.available_chairmen:
            conflict = self.conflict_checker.check_person_availability(
                chairman, time_slot, scheduled_defenses
            )
            if not conflict:
                return chairman
        return None

    def can_schedule_defense(self, defense: Defense, slot: ScheduleSlot,
                             schedule: Schedule) -> Tuple[bool, List[SchedulingConflict]]:
        """Check if defense can be scheduled in given slot."""
        scheduled_defenses = schedule.get_scheduled_defenses()

        # Check for conflicts
        conflicts = self.conflict_checker.check_defense_conflicts(
            defense, slot.time_slot, scheduled_defenses
        )

        if conflicts:
            return False, conflicts

        # Check chairman availability
        chairman = self.find_available_chairman(slot.time_slot, scheduled_defenses)
        if not chairman:
            conflicts.append(SchedulingConflict(
                f"No chairman available for {slot.time_slot}",
                defense=defense, time_slot=slot.time_slot
            ))
            return False, conflicts

        return True, []

    def schedule(self, defenses: List[Defense]) -> Tuple[Schedule, List[SchedulingConflict]]:
        """
        Schedule defenses. To be implemented by specific algorithms.
        Returns tuple of (schedule, unresolved_conflicts).
        """
        raise NotImplementedError("Subclasses must implement schedule method")