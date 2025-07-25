from dataclasses import dataclass

@dataclass
class Room:
    """Represents a room where defenses can be held."""
    name: str
    number: str
    capacity: int = 20
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Room name cannot be empty")
        if self.capacity <= 0:
            raise ValueError("Room capacity must be positive")
    
    def __str__(self):
        return f"{self.name} ({self.number})"