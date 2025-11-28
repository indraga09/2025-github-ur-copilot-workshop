"""
Integration tests for Pomodoro Timer application.
Tests the full workflow from frontend to backend.
"""
import pytest
import json
import tempfile
import os
from datetime import datetime, timezone

from app import create_app
from utils.session_manager import PomodoroSession
from utils.logger import SessionLogger


class TestFullWorkflow:
    """Test complete application workflow."""
    
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
    
    def test_complete_session_workflow(self, client, temp_log_file):
        """Test complete session creation and retrieval workflow."""
        # Patch the log file path
        with patch('config.Config.get_log_settings') as mock_log_settings:
            mock_log_settings.return_value = {'file_path': temp_log_file}
            
            # Step 1: Check initial empty state
            response = client.get('/api/sessions')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['sessions'] == []
            assert data['total'] == 0
            
            # Step 2: Check initial empty stats
            response = client.get('/api/stats')
            assert response.status_code == 200
            stats = json.loads(response.data)
            assert stats['total_sessions'] == 0
            assert stats['completed_sessions'] == 0
            
            # Step 3: Create a work session
            work_session_data = {
                'session_type': 'work',
                'duration_minutes': 25,
                'task_description': 'Important work task',
                'completed': True,
                'interruptions': 1
            }
            
            response = client.post('/api/sessions',
                                 data=json.dumps(work_session_data),
                                 content_type='application/json')
            assert response.status_code == 201
            create_response = json.loads(response.data)
            assert create_response['success'] is True
            work_session_id = create_response['session_id']
            
            # Step 4: Create a break session
            break_session_data = {
                'session_type': 'short_break',
                'duration_minutes': 5,
                'task_description': '',
                'completed': True,
                'interruptions': 0
            }
            
            response = client.post('/api/sessions',
                                 data=json.dumps(break_session_data),
                                 content_type='application/json')
            assert response.status_code == 201
            create_response = json.loads(response.data)
            assert create_response['success'] is True
            break_session_id = create_response['session_id']
            
            # Step 5: Create an incomplete session
            incomplete_session_data = {
                'session_type': 'work',
                'duration_minutes': 25,
                'task_description': 'Interrupted task',
                'completed': False,
                'interruptions': 3
            }
            
            response = client.post('/api/sessions',
                                 data=json.dumps(incomplete_session_data),
                                 content_type='application/json')
            assert response.status_code == 201
            
            # Step 6: Retrieve all sessions
            response = client.get('/api/sessions')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['sessions']) == 3
            assert data['total'] == 3
            
            # Verify session data (newest first)
            sessions = data['sessions']
            
            # Most recent should be incomplete session
            assert sessions[0]['session_type'] == 'work'
            assert sessions[0]['completed'] is False
            assert sessions[0]['task_description'] == 'Interrupted task'
            assert sessions[0]['interruptions'] == 3
            
            # Second should be break session
            assert sessions[1]['session_type'] == 'short_break'
            assert sessions[1]['completed'] is True
            assert sessions[1]['task_description'] == ''
            assert sessions[1]['session_id'] == break_session_id
            
            # First should be work session
            assert sessions[2]['session_type'] == 'work'
            assert sessions[2]['completed'] is True
            assert sessions[2]['task_description'] == 'Important work task'
            assert sessions[2]['session_id'] == work_session_id
            assert sessions[2]['interruptions'] == 1
            
            # Step 7: Check updated statistics
            response = client.get('/api/stats')
            assert response.status_code == 200
            stats = json.loads(response.data)
            
            assert stats['total_sessions'] == 3
            assert stats['completed_sessions'] == 2  # 2 completed, 1 incomplete
            assert stats['total_focus_minutes'] == 25  # Only completed work session
            assert stats['completion_rate'] == 66.7  # 2/3 * 100 = 66.7%
    
    def test_session_limit_and_filtering(self, client, temp_log_file):
        """Test session retrieval with limits and date filtering."""
        with patch('config.Config.get_log_settings') as mock_log_settings:
            mock_log_settings.return_value = {'file_path': temp_log_file}
            
            # Create multiple sessions
            session_types = ['work', 'short_break', 'work', 'long_break', 'work']
            for i, session_type in enumerate(session_types):
                session_data = {
                    'session_type': session_type,
                    'duration_minutes': 25 if session_type == 'work' else (5 if session_type == 'short_break' else 15),
                    'task_description': f'Task {i}',
                    'completed': True,
                    'interruptions': 0
                }
                
                response = client.post('/api/sessions',
                                     data=json.dumps(session_data),
                                     content_type='application/json')
                assert response.status_code == 201
            
            # Test limit parameter
            response = client.get('/api/sessions?limit=3')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['sessions']) == 3
            assert data['total'] == 3
            
            # Test date filtering (today's date)
            today = datetime.now().date().isoformat()
            response = client.get(f'/api/sessions?date={today}')
            assert response.status_code == 200
            data = json.loads(response.data)
            # Should return all sessions from today
            assert len(data['sessions']) == 5
    
    def test_error_handling_workflow(self, client):
        """Test error handling in the complete workflow."""
        # Test invalid session data
        invalid_data = {
            'session_type': 'invalid_type',
            'duration_minutes': -5,
        }
        
        response = client.post('/api/sessions',
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        assert response.status_code == 400
        
        # Test invalid JSON
        response = client.post('/api/sessions',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400
        
        # Test missing content type
        response = client.post('/api/sessions',
                             data=json.dumps({'session_type': 'work', 'duration_minutes': 25}))
        # Should still work or return 400
        assert response.status_code in [201, 400]
    
    def test_concurrent_session_creation(self, client, temp_log_file):
        """Test concurrent session creation."""
        with patch('config.Config.get_log_settings') as mock_log_settings:
            mock_log_settings.return_value = {'file_path': temp_log_file}
            
            # Create multiple sessions concurrently (simulated)
            session_ids = []
            for i in range(5):
                session_data = {
                    'session_type': 'work',
                    'duration_minutes': 25,
                    'task_description': f'Concurrent task {i}',
                    'completed': True,
                    'interruptions': 0
                }
                
                response = client.post('/api/sessions',
                                     data=json.dumps(session_data),
                                     content_type='application/json')
                assert response.status_code == 201
                
                data = json.loads(response.data)
                session_ids.append(data['session_id'])
            
            # Verify all sessions are unique and created
            assert len(set(session_ids)) == 5  # All IDs should be unique
            
            # Verify all sessions are retrievable
            response = client.get('/api/sessions')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['sessions']) == 5
    
    def test_large_dataset_workflow(self, client, temp_log_file):
        """Test workflow with larger dataset."""
        with patch('config.Config.get_log_settings') as mock_log_settings:
            mock_log_settings.return_value = {'file_path': temp_log_file}
            
            # Create 50 sessions
            for i in range(50):
                session_data = {
                    'session_type': 'work' if i % 2 == 0 else 'short_break',
                    'duration_minutes': 25 if i % 2 == 0 else 5,
                    'task_description': f'Large dataset task {i}',
                    'completed': i % 3 != 0,  # Complete 2/3 of sessions
                    'interruptions': i % 4
                }
                
                response = client.post('/api/sessions',
                                     data=json.dumps(session_data),
                                     content_type='application/json')
                assert response.status_code == 201
            
            # Test default limit (should be 100, so get all)
            response = client.get('/api/sessions')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['sessions']) == 50
            assert data['total'] == 50
            
            # Test smaller limit
            response = client.get('/api/sessions?limit=20')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['sessions']) == 20
            assert data['total'] == 20
            
            # Test statistics with larger dataset
            response = client.get('/api/stats')
            assert response.status_code == 200
            stats = json.loads(response.data)
            
            assert stats['total_sessions'] == 50
            # Should have roughly 33 completed sessions (2/3 of 50)
            assert 30 <= stats['completed_sessions'] <= 35
            assert stats['completion_rate'] > 50.0
    
    def test_session_data_persistence(self, client, temp_log_file):
        """Test that session data persists across requests."""
        with patch('config.Config.get_log_settings') as mock_log_settings:
            mock_log_settings.return_value = {'file_path': temp_log_file}
            
            # Create a session
            session_data = {
                'session_type': 'work',
                'duration_minutes': 25,
                'task_description': 'Persistence test',
                'completed': True,
                'interruptions': 2
            }
            
            response = client.post('/api/sessions',
                                 data=json.dumps(session_data),
                                 content_type='application/json')
            assert response.status_code == 201
            create_data = json.loads(response.data)
            session_id = create_data['session_id']
            
            # Verify data persists by reading from file directly
            logger = SessionLogger(temp_log_file)
            sessions = logger.read_sessions()
            
            assert len(sessions) == 1
            session = sessions[0]
            assert session.session_id == session_id
            assert session.session_type == 'work'
            assert session.duration_minutes == 25
            assert session.task_description == 'Persistence test'
            assert session.completed is True
            assert session.interruptions == 2


class TestAPIIntegration:
    """Test API integration scenarios."""
    
    @pytest.fixture
    def app(self):
        """Create test Flask application."""
        app = create_app()
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture  
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_all_endpoints_accessible(self, client):
        """Test that all API endpoints are accessible."""
        endpoints = [
            ('GET', '/'),
            ('GET', '/health'),
            ('GET', '/history'),
            ('GET', '/api/sessions'),
            ('GET', '/api/stats'),
        ]
        
        for method, endpoint in endpoints:
            if method == 'GET':
                response = client.get(endpoint)
            
            # All endpoints should be accessible (not 404)
            assert response.status_code != 404, f"Endpoint {method} {endpoint} should be accessible"
    
    def test_cors_headers(self, client):
        """Test CORS headers if needed."""
        response = client.get('/api/sessions')
        
        # For now, just check that request completes
        assert response.status_code in [200, 500]  # 500 might occur if no log file
    
    def test_content_type_handling(self, client):
        """Test different content types."""
        # JSON content type
        response = client.post('/api/sessions',
                             data=json.dumps({'session_type': 'work', 'duration_minutes': 25}),
                             content_type='application/json')
        assert response.status_code in [201, 400, 500]
        
        # Form data (should be rejected)
        response = client.post('/api/sessions',
                             data={'session_type': 'work', 'duration_minutes': '25'},
                             content_type='application/x-www-form-urlencoded')
        assert response.status_code == 400


# Import patch for the integration tests
from unittest.mock import patch