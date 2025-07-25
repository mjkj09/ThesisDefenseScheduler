import re
from typing import List, Set
from src.models.defense import Defense
from src.models.person import Person
from src.models.time_slot import TimeSlot

class Validator:
    """Validation utilities for the scheduling system."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def check_time_conflicts(defenses: List[Defense]) -> List[str]:
        """Check for time conflicts in scheduled defenses."""
        conflicts = []
        
        for i, def1 in enumerate(defenses):
            if not def1.is_scheduled():
                continue
                
            for j, def2 in enumerate(defenses[i+1:], i+1):
                if not def2.is_scheduled():
                    continue
                committee1 = set(def1.get_committee())
                committee2 = set(def2.get_committee())
                common_members = committee1 & committee2
                
                if common_members and def1.time_slot.overlaps_with(def2.time_slot):
                    for person in common_members:
                        conflicts.append(
                            f"{person.name} has conflicting defenses: "
                            f"'{def1.student_name}' and '{def2.student_name}' "
                            f"at {def1.time_slot}"
                        )
                if (def1.room == def2.room and 
                    def1.time_slot.overlaps_with(def2.time_slot)):
                    conflicts.append(
                        f"Room {def1.room.name} double-booked: "
                        f"'{def1.student_name}' and '{def2.student_name}' "
                        f"at {def1.time_slot}"
                    )
        
        return conflicts
    
    @staticmethod
    def validate_defense_data(defenses: List[Defense]) -> List[str]:
        """Validate completeness of defense data."""
        errors = []
        
        for i, defense in enumerate(defenses):
            if not defense.student_name:
                errors.append(f"Defense {i+1}: Missing student name")
            if not defense.thesis_title:
                errors.append(f"Defense {i+1}: Missing thesis title")
            if not defense.supervisor:
                errors.append(f"Defense {i+1}: Missing supervisor")
            if not defense.reviewer:
                errors.append(f"Defense {i+1}: Missing reviewer")
        
        return errors