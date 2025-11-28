"""Session management for Pomodoro Timer application."""
import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class PomodoroSession:
    """Represents a single Pomodoro session."""
    
    def __init__(self, session_type: str, duration: int, task_description: str = "") -> None:
        """Initialize a Pomodoro session.
        
        Args:
            session_type: Type of session ('work', 'short_break', 'long_break')
            duration: Duration in minutes
            task_description: Optional description of the task
        """
        self.session_id = generate_session_id()
        self.session_type = session_type
        self.duration_minutes = duration
        self.task_description = task_description
        self.start_time = datetime.now(timezone.utc)
        self.end_time: Optional[datetime] = None
        self.completed = False
        self.interruptions = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the session
        """
        return {
            'session_id': self.session_id,
            'session_type': self.session_type,
            'duration_minutes': self.duration_minutes,
            'task_description': self.task_description,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'completed': self.completed,
            'interruptions': self.interruptions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PomodoroSession':
        """Create session from dictionary.
        
        Args:
            data: Dictionary containing session data
            
        Returns:
            PomodoroSession instance
        """
        session = cls(
            session_type=data['session_type'],
            duration=data['duration_minutes'],
            task_description=data.get('task_description', '')
        )
        session.session_id = data['session_id']
        session.start_time = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            session.end_time = datetime.fromisoformat(data['end_time'])
        session.completed = data.get('completed', False)
        session.interruptions = data.get('interruptions', 0)
        return session
    
    def validate(self) -> bool:
        """Validate session data.
        
        Returns:
            True if session data is valid, False otherwise
        """
        if not validate_session_type(self.session_type):
            return False
        
        if self.duration_minutes <= 0:
            return False
            
        if self.interruptions < 0:
            return False
            
        return True
    
    def calculate_end_time(self) -> datetime:
        """Calculate expected end time based on duration.
        
        Returns:
            Expected end time
        """
        from datetime import timedelta
        return self.start_time + timedelta(minutes=self.duration_minutes)
    
    def complete_session(self) -> None:
        """Mark session as completed."""
        self.completed = True
        self.end_time = datetime.now(timezone.utc)
    
    def add_interruption(self) -> None:
        """Add an interruption to the session."""
        self.interruptions += 1


def generate_session_id() -> str:
    """Generate unique session ID.
    
    Returns:
        UUID string for session identification
    """
    return str(uuid.uuid4())


def validate_session_type(session_type: str) -> bool:
    """Validate session type.
    
    Args:
        session_type: Type to validate
        
    Returns:
        True if valid session type, False otherwise
    """
    valid_types = {'work', 'short_break', 'long_break'}
    return session_type in valid_types


def calculate_session_duration(session_type: str) -> int:
    """Calculate default duration for session type.
    
    Args:
        session_type: Type of session
        
    Returns:
        Duration in minutes
    """
    durations = {
        'work': 25,
        'short_break': 5,
        'long_break': 15
    }
    return durations.get(session_type, 25)