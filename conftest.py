"""
Shared test fixtures and configuration for pytest.
"""
import pytest
import tempfile
import os
from datetime import datetime, timezone

from utils.session_manager import PomodoroSession


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def sample_session():
    """Create a sample Pomodoro session for testing."""
    session = PomodoroSession('work', 25, 'Sample test task')
    session.complete_session()
    return session


@pytest.fixture
def sample_sessions():
    """Create multiple sample sessions for testing."""
    sessions = []
    
    # Work session
    work_session = PomodoroSession('work', 25, 'Work task 1')
    work_session.complete_session()
    sessions.append(work_session)
    
    # Short break session
    short_break = PomodoroSession('short_break', 5)
    short_break.complete_session()
    sessions.append(short_break)
    
    # Incomplete work session
    incomplete_work = PomodoroSession('work', 25, 'Incomplete task')
    incomplete_work.add_interruption()
    sessions.append(incomplete_work)
    
    # Long break session
    long_break = PomodoroSession('long_break', 15)
    long_break.complete_session()
    sessions.append(long_break)
    
    return sessions


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent testing."""
    return datetime(2025, 11, 28, 10, 0, 0, tzinfo=timezone.utc)


@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings."""
    return {
        'work_minutes': 25,
        'short_break_minutes': 5,
        'long_break_minutes': 15,
        'log_file': 'test_sessions.log'
    }


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    original_env = os.environ.copy()
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests" 
    )
    config.addinivalue_line(
        "markers", "frontend: marks tests as frontend tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Mark tests based on file location
        if "test_app.py" in item.nodeid or "test_config.py" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "frontend" in item.nodeid:
            item.add_marker(pytest.mark.frontend)
        
        # Mark slow tests
        if "large_dataset" in item.name or "concurrent" in item.name:
            item.add_marker(pytest.mark.slow)