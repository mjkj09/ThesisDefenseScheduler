from dataclasses import dataclass, field
from typing import Set, List
from datetime import datetime
from .role import Role
from .time_slot import TimeSlot

@dataclass
class Person:
    """Represents a faculty member who can participate in defenses."""
    name: str
    email: str
    roles: Set[Role] = field(default_factory=set)
    unavailable_slots: List['TimeSlot'] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.email or '@' not in self.email:
            raise ValueError(f"Invalid email: {self.email}")
        if not self.name:
            raise ValueError("Name cannot be empty")
    
    def is_available_at(self, time_slot: 'TimeSlot') -> bool:
        """Check if person is available during given time slot."""
        for unavailable in self.unavailable_slots:
            if unavailable.overlaps_with(time_slot):
                return False
        return True
    
    def can_be_chairman(self) -> bool:
        """Check if person can serve as chairman."""
        return Role.CHAIRMAN in self.roles
    
    def __str__(self):
        return f"{self.name} ({self.email})"