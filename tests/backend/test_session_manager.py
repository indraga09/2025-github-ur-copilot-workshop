"""
Test cases for Pomodoro Timer session management.
"""
import pytest
import json
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from utils.session_manager import (
    PomodoroSession, 
    generate_session_id, 
    validate_session_type,
    calculate_session_duration
)


class TestPomodoroSession:
    """Test PomodoroSession class."""
    
    def test_session_creation(self):
        """Test basic session creation."""
        session = PomodoroSession('work', 25, 'Test task')
        
        assert session.session_type == 'work'
        assert session.duration_minutes == 25
        assert session.task_description == 'Test task'
        assert not session.completed
        assert session.interruptions == 0
        assert session.session_id is not None
        assert isinstance(session.start_time, datetime)
        assert session.end_time is None
    
    def test_session_creation_without_task(self):
        """Test session creation without task description."""
        session = PomodoroSession('short_break', 5)
        
        assert session.session_type == 'short_break'
        assert session.duration_minutes == 5
        assert session.task_description == ''
    
    def test_session_validation_valid(self):
        """Test session validation with valid data."""
        session = PomodoroSession('work', 25)
        assert session.validate() is True
        
        session = PomodoroSession('short_break', 5)
        assert session.validate() is True
        
        session = PomodoroSession('long_break', 15)
        assert session.validate() is True
    
    def test_session_validation_invalid_type(self):
        """Test session validation with invalid session type."""
        session = PomodoroSession('work', 25)
        session.session_type = 'invalid'
        assert session.validate() is False
        
        session.session_type = ''
        assert session.validate() is False
        
        session.session_type = None
        assert session.validate() is False
    
    def test_session_validation_invalid_duration(self):
        """Test session validation with invalid duration."""
        session = PomodoroSession('work', 25)
        
        session.duration_minutes = 0
        assert session.validate() is False
        
        session.duration_minutes = -5
        assert session.validate() is False
    
    def test_session_validation_invalid_interruptions(self):
        """Test session validation with invalid interruptions."""
        session = PomodoroSession('work', 25)
        session.interruptions = -1
        assert session.validate() is False
    
    def test_session_completion(self):
        """Test session completion."""
        session = PomodoroSession('work', 25)
        assert not session.completed
        assert session.end_time is None
        
        session.complete_session()
        assert session.completed
        assert session.end_time is not None
        assert isinstance(session.end_time, datetime)
    
    def test_add_interruption(self):
        """Test adding interruptions to session."""
        session = PomodoroSession('work', 25)
        assert session.interruptions == 0
        
        session.add_interruption()
        assert session.interruptions == 1
        
        session.add_interruption()
        session.add_interruption()
        assert session.interruptions == 3
    
    def test_calculate_end_time(self):
        """Test end time calculation."""
        session = PomodoroSession('work', 25)
        expected_end = session.start_time + timedelta(minutes=25)
        calculated_end = session.calculate_end_time()
        
        # Allow for small time difference due to processing delay
        time_diff = abs((calculated_end - expected_end).total_seconds())
        assert time_diff < 1  # Less than 1 second difference
    
    def test_session_serialization(self):
        """Test JSON serialization and deserialization."""
        session = PomodoroSession('work', 25, 'Test task')
        session.interruptions = 2
        session.complete_session()
        
        # Test serialization
        data = session.to_dict()
        
        assert data['session_type'] == 'work'
        assert data['duration_minutes'] == 25
        assert data['task_description'] == 'Test task'
        assert data['completed'] is True
        assert data['interruptions'] == 2
        assert data['session_id'] == session.session_id
        assert data['start_time'] is not None
        assert data['end_time'] is not None
        
        # Test deserialization
        new_session = PomodoroSession.from_dict(data)
        assert new_session.session_type == session.session_type
        assert new_session.duration_minutes == session.duration_minutes
        assert new_session.task_description == session.task_description
        assert new_session.completed == session.completed
        assert new_session.interruptions == session.interruptions
        assert new_session.session_id == session.session_id
    
    def test_session_serialization_incomplete(self):
        """Test serialization of incomplete session."""
        session = PomodoroSession('short_break', 5)
        data = session.to_dict()
        
        assert data['completed'] is False
        assert data['end_time'] is None
        
        # Test deserialization
        new_session = PomodoroSession.from_dict(data)
        assert new_session.completed is False
        assert new_session.end_time is None


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_generate_session_id(self):
        """Test session ID generation."""
        id1 = generate_session_id()
        id2 = generate_session_id()
        
        assert id1 != id2
        assert len(id1) > 0
        assert len(id2) > 0
        
        # Test that IDs are valid UUIDs
        assert uuid.UUID(id1)
        assert uuid.UUID(id2)
    
    def test_generate_session_id_uniqueness(self):
        """Test that session IDs are unique."""
        ids = [generate_session_id() for _ in range(100)]
        assert len(set(ids)) == 100  # All unique
    
    def test_validate_session_type_valid(self):
        """Test session type validation with valid types."""
        assert validate_session_type('work') is True
        assert validate_session_type('short_break') is True
        assert validate_session_type('long_break') is True
    
    def test_validate_session_type_invalid(self):
        """Test session type validation with invalid types."""
        assert validate_session_type('invalid') is False
        assert validate_session_type('') is False
        assert validate_session_type('break') is False
        assert validate_session_type('WORK') is False  # Case sensitive
        assert validate_session_type(None) is False
        assert validate_session_type(123) is False
    
    def test_calculate_session_duration(self):
        """Test session duration calculation."""
        assert calculate_session_duration('work') == 25
        assert calculate_session_duration('short_break') == 5
        assert calculate_session_duration('long_break') == 15
        assert calculate_session_duration('invalid') == 25  # Default to work
        assert calculate_session_duration('') == 25
        assert calculate_session_duration(None) == 25


class TestPomodoroSessionEdgeCases:
    """Test edge cases for PomodoroSession."""
    
    def test_session_with_extreme_duration(self):
        """Test session with extreme duration values."""
        # Very short duration
        session = PomodoroSession('work', 1)
        assert session.duration_minutes == 1
        assert session.validate() is True
        
        # Very long duration
        session = PomodoroSession('work', 120)
        assert session.duration_minutes == 120
        assert session.validate() is True
    
    def test_session_with_special_characters_in_task(self):
        """Test session with special characters in task description."""
        special_task = "Testing with émojis 🍅 and spëcial chars!"
        session = PomodoroSession('work', 25, special_task)
        
        assert session.task_description == special_task
        
        # Test serialization/deserialization with special chars
        data = session.to_dict()
        new_session = PomodoroSession.from_dict(data)
        assert new_session.task_description == special_task
    
    def test_session_with_very_long_task_description(self):
        """Test session with very long task description."""
        long_task = "A" * 1000  # 1000 character task
        session = PomodoroSession('work', 25, long_task)
        
        assert session.task_description == long_task
        assert len(session.task_description) == 1000
    
    @patch('utils.session_manager.datetime')
    def test_session_with_mocked_time(self, mock_datetime):
        """Test session creation with mocked time."""
        fixed_time = datetime(2025, 11, 28, 10, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_time
        
        session = PomodoroSession('work', 25)
        assert session.start_time == fixed_time
        
        # Test completion with different time
        completion_time = datetime(2025, 11, 28, 10, 25, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = completion_time
        
        session.complete_session()
        assert session.end_time == completion_time
    
    def test_session_from_dict_missing_fields(self):
        """Test creating session from dictionary with missing fields."""
        minimal_data = {
            'session_type': 'work',
            'duration_minutes': 25,
            'session_id': str(uuid.uuid4()),
            'start_time': datetime.now(timezone.utc).isoformat()
        }
        
        session = PomodoroSession.from_dict(minimal_data)
        assert session.session_type == 'work'
        assert session.duration_minutes == 25
        assert session.task_description == ''  # Default
        assert session.completed is False  # Default
        assert session.interruptions == 0  # Default
        assert session.end_time is None
    
    def test_session_from_dict_with_invalid_datetime(self):
        """Test creating session from dict with invalid datetime."""
        invalid_data = {
            'session_type': 'work',
            'duration_minutes': 25,
            'session_id': str(uuid.uuid4()),
            'start_time': 'invalid-datetime',
            'task_description': ''
        }
        
        with pytest.raises(ValueError):
            PomodoroSession.from_dict(invalid_data)