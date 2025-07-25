from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class TimeSlot:
    """Represents a time period."""
    start: datetime
    end: datetime
    
    def __post_init__(self):
        if self.start >= self.end:
            raise ValueError("Start time must be before end time")
    
    @property
    def duration(self) -> timedelta:
        """Get duration of the time slot."""
        return self.end - self.start
    
    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """Check if this time slot overlaps with another."""
        return not (self.end <= other.start or self.start >= other.end)
    
    def __str__(self):
        return f"{self.start.strftime('%Y-%m-%d %H:%M')} - {self.end.strftime('%H:%M')}"