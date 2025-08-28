import re
from typing import List, Dict
from src.models.defense import Defense
from src.models.role import Role


class Validator:
    """Validation utilities for the scheduling system."""

    # ---------- formaty / kompletność ----------
    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_defense_data(defenses: List[Defense]) -> List[str]:
        errors: List[str] = []
        for i, d in enumerate(defenses):
            if not d.student_name:
                errors.append(f"Defense {i+1}: Missing student name")
            if not d.thesis_title:
                errors.append(f"Defense {i+1}: Missing thesis title")
            if not d.supervisor:
                errors.append(f"Defense {i+1}: Missing supervisor")
            if not d.reviewer:
                errors.append(f"Defense {i+1}: Missing reviewer")
        return errors

    # ---------- konflikty czasu ----------
    @staticmethod
    def check_time_conflicts(defenses: List[Defense]) -> List[str]:
        """
        Sprawdza:
        - ta sama osoba (w dowolnej roli, w tym chairman) jednocześnie w 2 obronach,
        - podwójna rezerwacja sali.
        Porównujemy osoby po emailu (obiekty Person mogą być niehashowalne).
        """
        conflicts: List[str] = []

        for i, d1 in enumerate(defenses):
            if not d1.is_scheduled():
                continue

            for d2 in defenses[i + 1:]:
                if not d2.is_scheduled():
                    continue

                if not d1.time_slot.overlaps_with(d2.time_slot):
                    continue

                # mapy email -> Person (dla czytelnych komunikatów)
                comm1: Dict[str, object] = {getattr(p, "email", str(id(p))): p for p in d1.get_committee()}
                comm2: Dict[str, object] = {getattr(p, "email", str(id(p))): p for p in d2.get_committee()}

                common_emails = set(comm1.keys()) & set(comm2.keys())
                for em in common_emails:
                    person = comm1.get(em) or comm2.get(em)
                    name = getattr(person, "name", em)
                    conflicts.append(
                        f"{name} booked twice: "
                        f"'{d1.student_name}' and '{d2.student_name}' at {d1.time_slot}"
                    )

                if d1.room == d2.room:
                    conflicts.append(
                        f"Room {d1.room.name} double-booked: "
                        f"'{d1.student_name}' and '{d2.student_name}' at {d1.time_slot}"
                    )

        return conflicts

    # ---------- niedostępności ----------
    @staticmethod
    def check_person_unavailability(defenses: List[Defense]) -> List[str]:
        issues: List[str] = []
        for d in defenses:
            if not d.is_scheduled():
                continue
            for p in d.get_committee():
                for unav in getattr(p, "unavailable_slots", []) or []:
                    if unav.overlaps_with(d.time_slot):
                        issues.append(
                            f"{p.name} is marked unavailable for {d.student_name}'s defense at {d.time_slot}"
                        )
                        break
        return issues

    # ---------- poprawność roli przewodniczącego ----------
    @staticmethod
    def check_chairman_role(defenses: List[Defense]) -> List[str]:
        issues: List[str] = []
        for d in defenses:
            if not d.is_scheduled():
                continue
            if d.chairman and Role.CHAIRMAN not in d.chairman.roles:
                issues.append(
                    f"{d.chairman.name} assigned as chairman for {d.student_name} but lacks CHAIRMAN role"
                )
        return issues

    # ---------- agregat ----------
    @staticmethod
    def validate_schedule(defenses: List[Defense]) -> List[str]:
        """
        Agregacja reguł:
        - kompletność danych,
        - podwójne rezerwacje osób/sal,
        - niedostępności uczestników,
        - rola przewodniczącego.
        """
        messages: List[str] = []
        messages.extend(Validator.validate_defense_data(defenses))
        scheduled = [d for d in defenses if d.is_scheduled()]
        messages.extend(Validator.check_time_conflicts(scheduled))
        messages.extend(Validator.check_person_unavailability(scheduled))
        messages.extend(Validator.check_chairman_role(scheduled))

        # deduplikacja + stabilna kolejność
        return sorted(set(messages))
