from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from src.models import Person, Defense, Room, TimeSlot, SessionParameters


@dataclass
class ScheduleSlot:
    time_slot: TimeSlot
    room: Room
    defense: Optional[Defense] = None

    def is_free(self) -> bool:
        return self.defense is None


@dataclass
class Schedule:
    slots: List[ScheduleSlot] = field(default_factory=list)

    def add_defense(self, defense: Defense, slot: ScheduleSlot, chairman: Person) -> None:
        defense.time_slot = slot.time_slot
        defense.room = slot.room
        defense.chairman = chairman
        slot.defense = defense

    def get_scheduled_defenses(self) -> List[Defense]:
        return [slot.defense for slot in self.slots if slot.defense]

    def get_free_slots(self) -> List[ScheduleSlot]:
        return [slot for slot in self.slots if slot.is_free()]

    def remove_defense(self, defense: Defense) -> None:
        for slot in self.slots:
            if slot.defense == defense:
                slot.defense = None
                defense.time_slot = None
                defense.room = None
                defense.chairman = None
                break


class SchedulingConflict:
    def __init__(self, message: str, defense: Optional[Defense] = None,
                 person: Optional[Person] = None, time_slot: Optional[TimeSlot] = None):
        self.message = message
        self.defense = defense
        self.person = person
        self.time_slot = time_slot

    def __str__(self):
        return self.message


class ConflictChecker:
    @staticmethod
    def _person_busy_at(person: Person, time_slot: TimeSlot,
                        scheduled_defenses: List[Defense]) -> Optional[Defense]:
        p_email = getattr(person, "email", None)
        if not p_email:
            return None
        for d in scheduled_defenses:
            if not d.time_slot or not d.time_slot.overlaps_with(time_slot):
                continue
            for member in d.get_committee():
                if getattr(member, "email", None) == p_email:
                    return d
        return None

    @staticmethod
    def check_person_availability(person: Person, time_slot: TimeSlot,
                                  scheduled_defenses: List[Defense]) -> Optional[SchedulingConflict]:
        if not person.is_available_at(time_slot):
            return SchedulingConflict(
                f"{person.name} is not available at {time_slot}",
                person=person, time_slot=time_slot
            )
        booked = ConflictChecker._person_busy_at(person, time_slot, scheduled_defenses)
        if booked:
            return SchedulingConflict(
                f"{person.name} is already scheduled for {booked.student_name}'s defense",
                defense=booked, person=person, time_slot=time_slot
            )
        return None

    @staticmethod
    def check_defense_conflicts(defense: Defense, time_slot: TimeSlot,
                                scheduled_defenses: List[Defense]) -> List[SchedulingConflict]:
        conflicts: List[SchedulingConflict] = []
        c = ConflictChecker.check_person_availability(defense.supervisor, time_slot, scheduled_defenses)
        if c: conflicts.append(c)
        c = ConflictChecker.check_person_availability(defense.reviewer, time_slot, scheduled_defenses)
        if c: conflicts.append(c)
        return conflicts


class SchedulingAlgorithm:
    def __init__(self, parameters: SessionParameters, rooms: List[Room],
                 available_chairmen: List[Person]):
        self.parameters = parameters
        self.rooms = rooms
        self.available_chairmen = available_chairmen
        self.conflict_checker = ConflictChecker()

    def generate_time_slots(self) -> List[TimeSlot]:
        slots: List[TimeSlot] = []
        sh, sm = map(int, self.parameters.start_time.split(':'))
        eh, em = map(int, self.parameters.end_time.split(':'))

        current_time = datetime.combine(
            self.parameters.session_date,
            datetime.min.time().replace(hour=sh, minute=sm)
        )
        end_time = datetime.combine(
            self.parameters.session_date,
            datetime.min.time().replace(hour=eh, minute=em)
        )
        step = timedelta(minutes=self.parameters.defense_duration)

        while current_time + step <= end_time:
            slot = TimeSlot(start=current_time, end=current_time + step)
            if not any(slot.overlaps_with(b) for b in (self.parameters.breaks or [])):
                slots.append(slot)
            current_time += step
        return slots

    def create_empty_schedule(self) -> Schedule:
        schedule = Schedule()
        for ts in self.generate_time_slots():
            for room in self.rooms[: self.parameters.room_count]:
                schedule.slots.append(ScheduleSlot(time_slot=ts, room=room))
        return schedule

    # --- chairman ---

    def _chairman_candidates(self, defense: Defense) -> List[Person]:
        """DOPUSZCZA promotora/recenzenta jako przewodniczącego, ale preferuje osoby spoza komisji."""
        sup_email = defense.supervisor.email
        rev_email = defense.reviewer.email
        cands = list(self.available_chairmen)
        # osoby spoza komisji najpierw (False < True)
        cands.sort(key=lambda p: (p.email in (sup_email, rev_email), p.email))
        return cands

    def find_available_chairman(self, defense: Defense, time_slot: TimeSlot,
                                scheduled_defenses: List[Defense]) -> Optional[Person]:
        for cand in self._chairman_candidates(defense):
            if self.conflict_checker.check_person_availability(cand, time_slot, scheduled_defenses) is None:
                return cand
        return None

    def can_schedule_defense(self, defense: Defense, slot: ScheduleSlot,
                             schedule: Schedule) -> Tuple[bool, List[SchedulingConflict]]:
        scheduled = schedule.get_scheduled_defenses()
        conflicts = self.conflict_checker.check_defense_conflicts(defense, slot.time_slot, scheduled)
        if conflicts:
            return False, conflicts
        chairman = self.find_available_chairman(defense, slot.time_slot, scheduled)
        if not chairman:
            return False, [SchedulingConflict(f"No chairman available for {slot.time_slot}", defense=defense)]
        return True, []
