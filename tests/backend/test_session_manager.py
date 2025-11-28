"""
Test cases for Pomodoro Timer backend components.
"""
import json
from datetime import datetime, timezone
from utils.session_manager import PomodoroSession, generate_session_id, validate_session_type
from utils.logger import SessionLogger, create_log_entry, parse_log_entry
from utils.statistics import calculate_daily_stats, get_completion_rate


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
    
    def test_session_validation(self):
        """Test session validation."""
        # Valid session
        session = PomodoroSession('work', 25)
        assert session.validate()
        
        # Invalid session type
        session.session_type = 'invalid'
        assert not session.validate()
        
        # Invalid duration
        session.session_type = 'work'
        session.duration_minutes = 0
        assert not session.validate()
    
    def test_session_completion(self):
        """Test session completion."""
        session = PomodoroSession('work', 25)
        assert not session.completed
        assert session.end_time is None
        
        session.complete_session()
        assert session.completed
        assert session.end_time is not None
    
    def test_session_serialization(self):
        """Test JSON serialization."""
        session = PomodoroSession('work', 25, 'Test task')
        data = session.to_dict()
        
        assert data['session_type'] == 'work'
        assert data['duration_minutes'] == 25
        assert data['task_description'] == 'Test task'
        
        # Test deserialization
        new_session = PomodoroSession.from_dict(data)
        assert new_session.session_type == session.session_type
        assert new_session.duration_minutes == session.duration_minutes
        assert new_session.task_description == session.task_description


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_generate_session_id(self):
        """Test session ID generation."""
        id1 = generate_session_id()
        id2 = generate_session_id()
        
        assert id1 != id2
        assert len(id1) > 0
        assert len(id2) > 0
    
    def test_validate_session_type(self):
        """Test session type validation."""
        assert validate_session_type('work')
        assert validate_session_type('short_break')
        assert validate_session_type('long_break')
        assert not validate_session_type('invalid')
        assert not validate_session_type('')


class TestSessionLogger:
    """Test session logging functionality."""
    
    def test_log_entry_creation(self):
        """Test log entry creation."""
        session = PomodoroSession('work', 25, 'Test task')
        log_entry = create_log_entry(session)
        
        assert isinstance(log_entry, str)
        assert 'work' in log_entry
        assert '25' in log_entry
        
        # Test parsing
        parsed_session = parse_log_entry(log_entry)
        assert parsed_session is not None
        assert parsed_session.session_type == 'work'
        assert parsed_session.duration_minutes == 25


class TestStatistics:
    """Test statistics calculations."""
    
    def create_test_sessions(self):
        """Create test sessions for statistics."""
        sessions = []
        
        # Create completed work session
        session1 = PomodoroSession('work', 25, 'Task 1')
        session1.complete_session()
        sessions.append(session1)
        
        # Create incomplete session
        session2 = PomodoroSession('work', 25, 'Task 2')
        sessions.append(session2)
        
        # Create completed break session
        session3 = PomodoroSession('short_break', 5)
        session3.complete_session()
        sessions.append(session3)
        
        return sessions
    
    def test_completion_rate(self):
        """Test completion rate calculation."""
        sessions = self.create_test_sessions()
        rate = get_completion_rate(sessions)
        
        # 2 out of 3 sessions completed = 66.7%
        assert rate == 66.7
        
        # Test empty sessions
        assert get_completion_rate([]) == 0.0
    
    def test_daily_stats(self):
        """Test daily statistics calculation."""
        sessions = self.create_test_sessions()
        stats = calculate_daily_stats(sessions)
        
        assert 'total_sessions' in stats
        assert 'completed_sessions' in stats
        assert 'completion_rate' in stats
        assert stats['total_sessions'] >= 0


if __name__ == '__main__':
    # Run basic tests
    test_session = TestPomodoroSession()
    test_session.test_session_creation()
    test_session.test_session_validation()
    test_session.test_session_completion()
    test_session.test_session_serialization()
    
    test_utils = TestUtilityFunctions()
    test_utils.test_generate_session_id()
    test_utils.test_validate_session_type()
    
    test_logger = TestSessionLogger()
    test_logger.test_log_entry_creation()
    
    test_stats = TestStatistics()
    test_stats.test_completion_rate()
    test_stats.test_daily_stats()
    
    print("All tests passed!")