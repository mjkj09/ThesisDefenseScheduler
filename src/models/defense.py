from dataclasses import dataclass
from typing import Optional
from .person import Person
from .time_slot import TimeSlot
from .room import Room
from typing import List, Optional

@dataclass
class Defense:
    """Represents a thesis defense."""
    student_name: str
    thesis_title: str
    supervisor: Person
    reviewer: Person
    time_slot: Optional[TimeSlot] = None
    room: Optional[Room] = None
    chairman: Optional[Person] = None
    
    def __post_init__(self):
        if not self.student_name:
            raise ValueError("Student name cannot be empty")
        if not self.thesis_title:
            raise ValueError("Thesis title cannot be empty")
        if self.supervisor == self.reviewer:
            raise ValueError("Supervisor and reviewer must be different people")
    
    def is_scheduled(self) -> bool:
        """Check if defense has been scheduled."""
        return all([self.time_slot, self.room, self.chairman])
    
    def get_committee(self) -> List[Person]:
        """Get all committee members."""
        committee = [self.supervisor, self.reviewer]
        if self.chairman:
            committee.append(self.chairman)
        return committee
    
    def __str__(self):
        return f"{self.student_name}: {self.thesis_title}"