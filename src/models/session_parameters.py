from dataclasses import dataclass, field
from typing import List
from datetime import timedelta, date
from .time_slot import TimeSlot

@dataclass
class SessionParameters:
    """Parameters for the defense session."""
    session_date: date
    start_time: str = "09:00"
    end_time: str = "17:00"
    defense_duration: int = 30
    room_count: int = 1
    breaks: List[TimeSlot] = field(default_factory=list)
    
    def __post_init__(self):
        if self.defense_duration <= 0:
            raise ValueError("Defense duration must be positive")
        if self.room_count <= 0:
            raise ValueError("Room count must be positive")
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")
    
    def get_defense_duration_delta(self) -> timedelta:
        """Get defense duration as timedelta."""
        return timedelta(minutes=self.defense_duration)