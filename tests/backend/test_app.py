"""
Test cases for Pomodoro Timer Flask application.
"""
import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock

from app import create_app, configure_logging, validate_session_request
from config import Config
from utils.session_manager import PomodoroSession


class TestFlaskApp:
    """Test Flask application functionality."""
    
    @pytest.fixture
    def app(self):
        """Create test Flask application."""
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    @pytest.fixture
    def temp_log_file(self):
        """Create temporary log file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_app_creation(self, app):
        """Test Flask app creation."""
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'pomodoro-timer'
    
    def test_index_route(self, client):
        """Test main index route."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
        assert b'Pomodoro Timer' in response.data
    
    def test_history_route(self, client):
        """Test history route."""
        response = client.get('/history')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
        assert b'Session History' in response.data
    
    def test_api_sessions_post_valid_data(self, client, temp_log_file):
        """Test POST /api/sessions with valid data."""
        session_data = {
            'session_type': 'work',
            'duration_minutes': 25,
            'task_description': 'Test task',
            'completed': True,
            'interruptions': 0
        }
        
        with patch('config.Config.get_log_settings') as mock_log_settings:
            mock_log_settings.return_value = {'file_path': temp_log_file}
            
            response = client.post('/api/sessions',
                                 data=json.dumps(session_data),
                                 content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'session_id' in data
        assert data['message'] == 'Session logged successfully'
    
    def test_api_sessions_post_invalid_data(self, client):
        """Test POST /api/sessions with invalid data."""
        invalid_data = {
            'session_type': 'invalid_type',
            'duration_minutes': -5,
        }
        
        response = client.post('/api/sessions',
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_api_sessions_post_no_data(self, client):
        """Test POST /api/sessions with no data."""
        response = client.post('/api/sessions',
                             data='',
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_api_sessions_get_empty(self, client, temp_log_file):
        """Test GET /api/sessions with empty log file."""
        with patch('config.Config.get_log_settings') as mock_log_settings:
            mock_log_settings.return_value = {'file_path': temp_log_file}
            
            response = client.get('/api/sessions')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['sessions'] == []
        assert data['total'] == 0
    
    def test_api_sessions_get_with_data(self, client, temp_log_file):
        """Test GET /api/sessions with existing data."""
        # First, create some sessions
        session_data = {
            'session_type': 'work',
            'duration_minutes': 25,
            'task_description': 'Test task',
            'completed': True,
            'interruptions': 0
        }
        
        with patch('config.Config.get_log_settings') as mock_log_settings:
            mock_log_settings.return_value = {'file_path': temp_log_file}
            
            # Create a session
            client.post('/api/sessions',
                       data=json.dumps(session_data),
                       content_type='application/json')
            
            # Get sessions
            response = client.get('/api/sessions')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['sessions']) == 1
        assert data['total'] == 1
        assert data['sessions'][0]['session_type'] == 'work'
    
    def test_api_sessions_get_with_limit(self, client, temp_log_file):
        """Test GET /api/sessions with limit parameter."""
        with patch('config.Config.get_log_settings') as mock_log_settings:
            mock_log_settings.return_value = {'file_path': temp_log_file}
            
            response = client.get('/api/sessions?limit=50')
        
        assert response.status_code == 200
    
    def test_api_sessions_get_with_date_filter(self, client, temp_log_file):
        """Test GET /api/sessions with date filter."""
        with patch('config.Config.get_log_settings') as mock_log_settings:
            mock_log_settings.return_value = {'file_path': temp_log_file}
            
            response = client.get('/api/sessions?date=2025-11-28')
        
        assert response.status_code == 200
    
    def test_api_sessions_get_with_invalid_date(self, client, temp_log_file):
        """Test GET /api/sessions with invalid date filter."""
        with patch('config.Config.get_log_settings') as mock_log_settings:
            mock_log_settings.return_value = {'file_path': temp_log_file}
            
            response = client.get('/api/sessions?date=invalid-date')
        
        assert response.status_code == 200  # Should fallback to regular limit
    
    def test_api_stats_empty(self, client, temp_log_file):
        """Test GET /api/stats with no data."""
        with patch('config.Config.get_log_settings') as mock_log_settings:
            mock_log_settings.return_value = {'file_path': temp_log_file}
            
            response = client.get('/api/stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_sessions'] == 0
        assert data['completed_sessions'] == 0
        assert data['total_focus_minutes'] == 0
        assert data['completion_rate'] == 0
        assert data['today_sessions'] == 0
    
    def test_api_stats_with_data(self, client, temp_log_file):
        """Test GET /api/stats with existing data."""
        # Create some sessions first
        session_data = {
            'session_type': 'work',
            'duration_minutes': 25,
            'task_description': 'Test task',
            'completed': True,
            'interruptions': 0
        }
        
        with patch('config.Config.get_log_settings') as mock_log_settings:
            mock_log_settings.return_value = {'file_path': temp_log_file}
            
            # Create a session
            client.post('/api/sessions',
                       data=json.dumps(session_data),
                       content_type='application/json')
            
            # Get stats
            response = client.get('/api/stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_sessions'] >= 1
        assert data['completed_sessions'] >= 1
        assert data['total_focus_minutes'] >= 25
        assert data['completion_rate'] >= 0
    
    @patch('utils.logger.SessionLogger.log_session')
    def test_api_sessions_post_logging_failure(self, mock_log_session, client):
        """Test POST /api/sessions when logging fails."""
        mock_log_session.return_value = False  # Simulate logging failure
        
        session_data = {
            'session_type': 'work',
            'duration_minutes': 25,
            'task_description': 'Test task',
            'completed': True,
            'interruptions': 0
        }
        
        response = client.post('/api/sessions',
                             data=json.dumps(session_data),
                             content_type='application/json')
        
        assert response.status_code == 201  # Should still succeed
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'Failed to log session'
    
    def test_error_handling_500(self, client):
        """Test internal server error handling."""
        with patch('app.get_sessions', side_effect=Exception('Test error')):
            response = client.get('/api/sessions')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['error'] == 'Internal server error'


class TestConfigureLogging:
    """Test logging configuration."""
    
    def test_configure_logging(self):
        """Test logging configuration."""
        app = create_app()
        
        # Test that logging is configured
        assert app.logger is not None
        assert len(app.logger.handlers) > 0
    
    @patch('config.Config.get_log_settings')
    def test_configure_logging_with_custom_level(self, mock_log_settings):
        """Test logging configuration with custom level."""
        mock_log_settings.return_value = {'level': 'DEBUG'}
        
        app = create_app()
        configure_logging(app)
        
        # Verify logger configuration
        assert app.logger is not None


class TestSessionRequestValidation:
    """Test session request validation."""
    
    def test_validate_session_request_valid(self):
        """Test validation with valid request data."""
        valid_data = {
            'session_type': 'work',
            'duration_minutes': 25,
            'task_description': 'Test task',
            'completed': True,
            'interruptions': 0
        }
        
        result = validate_session_request(valid_data)
        assert result == valid_data
    
    def test_validate_session_request_missing_data(self):
        """Test validation with missing request data."""
        with pytest.raises(ValueError, match="Request data is required"):
            validate_session_request({})
        
        with pytest.raises(ValueError, match="Request data is required"):
            validate_session_request(None)
    
    def test_validate_session_request_invalid_session_type(self):
        """Test validation with invalid session type."""
        invalid_data = {
            'session_type': 'invalid_type',
            'duration_minutes': 25
        }
        
        with pytest.raises(ValueError, match="Invalid session type"):
            validate_session_request(invalid_data)
    
    def test_validate_session_request_missing_session_type(self):
        """Test validation with missing session type."""
        invalid_data = {
            'duration_minutes': 25
        }
        
        with pytest.raises(ValueError, match="Invalid session type"):
            validate_session_request(invalid_data)
    
    def test_validate_session_request_invalid_duration(self):
        """Test validation with invalid duration."""
        # Zero duration
        invalid_data = {
            'session_type': 'work',
            'duration_minutes': 0
        }
        
        with pytest.raises(ValueError, match="Invalid duration"):
            validate_session_request(invalid_data)
        
        # Negative duration
        invalid_data['duration_minutes'] = -5
        with pytest.raises(ValueError, match="Invalid duration"):
            validate_session_request(invalid_data)
        
        # Non-integer duration
        invalid_data['duration_minutes'] = 'invalid'
        with pytest.raises(ValueError, match="Invalid duration"):
            validate_session_request(invalid_data)
    
    def test_validate_session_request_missing_duration(self):
        """Test validation with missing duration."""
        invalid_data = {
            'session_type': 'work'
        }
        
        with pytest.raises(ValueError, match="Invalid duration"):
            validate_session_request(invalid_data)
    
    def test_validate_session_request_optional_fields(self):
        """Test validation with optional fields."""
        # Minimal valid data
        minimal_data = {
            'session_type': 'work',
            'duration_minutes': 25
        }
        
        result = validate_session_request(minimal_data)
        assert result == minimal_data
        
        # With optional fields
        full_data = {
            'session_type': 'short_break',
            'duration_minutes': 5,
            'task_description': 'Break time',
            'completed': False,
            'interruptions': 2
        }
        
        result = validate_session_request(full_data)
        assert result == full_data


class TestAppConfiguration:
    """Test application configuration."""
    
    def test_app_with_invalid_config(self):
        """Test app creation with invalid configuration."""
        with patch('config.Config.validate_config') as mock_validate:
            mock_validate.return_value = False
            
            # Should still create app but log warning
            app = create_app()
            assert app is not None
    
    def test_app_with_valid_config(self):
        """Test app creation with valid configuration."""
        with patch('config.Config.validate_config') as mock_validate:
            mock_validate.return_value = True
            
            app = create_app()
            assert app is not None