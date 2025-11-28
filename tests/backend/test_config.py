"""
Test cases for Pomodoro Timer configuration.
"""
import pytest
import os
from unittest.mock import patch

from config import Config


class TestConfig:
    """Test Config class functionality."""
    
    def test_config_initialization_defaults(self):
        """Test config initialization with default values."""
        config = Config()
        
        assert config.FLASK_ENV == 'development'
        assert config.FLASK_DEBUG is True
        assert config.SECRET_KEY == 'dev-secret-key-change-in-production'
        assert config.HOST == '127.0.0.1'
        assert config.PORT == 5000
    
    @patch.dict(os.environ, {
        'FLASK_ENV': 'production',
        'FLASK_DEBUG': 'False',
        'SECRET_KEY': 'production-secret',
        'HOST': '0.0.0.0',
        'PORT': '8080'
    })
    def test_config_initialization_from_env(self):
        """Test config initialization from environment variables."""
        config = Config()
        
        assert config.FLASK_ENV == 'production'
        assert config.FLASK_DEBUG is False
        assert config.SECRET_KEY == 'production-secret'
        assert config.HOST == '0.0.0.0'
        assert config.PORT == 8080
    
    @patch.dict(os.environ, {'FLASK_DEBUG': 'true'})
    def test_config_flask_debug_true_lowercase(self):
        """Test FLASK_DEBUG with lowercase 'true'."""
        config = Config()
        assert config.FLASK_DEBUG is True
    
    @patch.dict(os.environ, {'FLASK_DEBUG': 'TRUE'})
    def test_config_flask_debug_true_uppercase(self):
        """Test FLASK_DEBUG with uppercase 'TRUE'."""
        config = Config()
        assert config.FLASK_DEBUG is True
    
    @patch.dict(os.environ, {'FLASK_DEBUG': 'false'})
    def test_config_flask_debug_false(self):
        """Test FLASK_DEBUG with 'false'."""
        config = Config()
        assert config.FLASK_DEBUG is False
    
    @patch.dict(os.environ, {'FLASK_DEBUG': 'anything'})
    def test_config_flask_debug_invalid_value(self):
        """Test FLASK_DEBUG with invalid value."""
        config = Config()
        assert config.FLASK_DEBUG is False
    
    @patch.dict(os.environ, {'PORT': 'invalid'})
    def test_config_invalid_port_env(self):
        """Test config with invalid PORT environment variable."""
        with pytest.raises(ValueError):
            Config()
    
    def test_get_timer_defaults(self):
        """Test getting timer default values."""
        config = Config()
        defaults = config.get_timer_defaults()
        
        assert isinstance(defaults, dict)
        assert 'work_minutes' in defaults
        assert 'short_break_minutes' in defaults
        assert 'long_break_minutes' in defaults
        
        assert defaults['work_minutes'] == 25
        assert defaults['short_break_minutes'] == 5
        assert defaults['long_break_minutes'] == 15
    
    @patch.dict(os.environ, {
        'DEFAULT_WORK_MINUTES': '30',
        'DEFAULT_SHORT_BREAK_MINUTES': '10',
        'DEFAULT_LONG_BREAK_MINUTES': '20'
    })
    def test_get_timer_defaults_from_env(self):
        """Test getting timer defaults from environment variables."""
        config = Config()
        defaults = config.get_timer_defaults()
        
        assert defaults['work_minutes'] == 30
        assert defaults['short_break_minutes'] == 10
        assert defaults['long_break_minutes'] == 20
    
    @patch.dict(os.environ, {'DEFAULT_WORK_MINUTES': 'invalid'})
    def test_get_timer_defaults_invalid_env(self):
        """Test timer defaults with invalid environment variable."""
        with pytest.raises(ValueError):
            config = Config()
            config.get_timer_defaults()
    
    def test_get_log_settings(self):
        """Test getting log settings."""
        config = Config()
        settings = config.get_log_settings()
        
        assert isinstance(settings, dict)
        assert 'level' in settings
        assert 'file_path' in settings
        
        assert settings['level'] == 'INFO'
        assert settings['file_path'] == 'logs/pomodoro_sessions.log'
    
    @patch.dict(os.environ, {
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE_PATH': 'custom/path/sessions.log'
    })
    def test_get_log_settings_from_env(self):
        """Test getting log settings from environment variables."""
        config = Config()
        settings = config.get_log_settings()
        
        assert settings['level'] == 'DEBUG'
        assert settings['file_path'] == 'custom/path/sessions.log'
    
    def test_validate_config_valid(self):
        """Test config validation with valid values."""
        config = Config()
        assert config.validate_config() is True
    
    @patch.dict(os.environ, {'DEFAULT_WORK_MINUTES': '0'})
    def test_validate_config_invalid_work_minutes(self):
        """Test config validation with invalid work minutes."""
        config = Config()
        assert config.validate_config() is False
    
    @patch.dict(os.environ, {'DEFAULT_SHORT_BREAK_MINUTES': '-5'})
    def test_validate_config_invalid_short_break_minutes(self):
        """Test config validation with invalid short break minutes."""
        config = Config()
        assert config.validate_config() is False
    
    @patch.dict(os.environ, {'DEFAULT_LONG_BREAK_MINUTES': '0'})
    def test_validate_config_invalid_long_break_minutes(self):
        """Test config validation with invalid long break minutes."""
        config = Config()
        assert config.validate_config() is False
    
    @patch.dict(os.environ, {'PORT': '0'})
    def test_validate_config_invalid_port_zero(self):
        """Test config validation with port 0."""
        config = Config()
        assert config.validate_config() is False
    
    @patch.dict(os.environ, {'PORT': '70000'})
    def test_validate_config_invalid_port_too_high(self):
        """Test config validation with port too high."""
        config = Config()
        assert config.validate_config() is False
    
    @patch.dict(os.environ, {'PORT': '1'})
    def test_validate_config_valid_port_minimum(self):
        """Test config validation with minimum valid port."""
        config = Config()
        assert config.validate_config() is True
    
    @patch.dict(os.environ, {'PORT': '65535'})
    def test_validate_config_valid_port_maximum(self):
        """Test config validation with maximum valid port."""
        config = Config()
        assert config.validate_config() is True
    
    @patch.dict(os.environ, {
        'DEFAULT_WORK_MINUTES': '1',
        'DEFAULT_SHORT_BREAK_MINUTES': '1',
        'DEFAULT_LONG_BREAK_MINUTES': '1',
        'PORT': '8080'
    })
    def test_validate_config_edge_cases_valid(self):
        """Test config validation with edge case valid values."""
        config = Config()
        assert config.validate_config() is True
    
    def test_config_attributes_exist(self):
        """Test that all required config attributes exist."""
        config = Config()
        
        # Check all required attributes
        required_attrs = [
            'FLASK_ENV', 'FLASK_DEBUG', 'SECRET_KEY', 'HOST', 'PORT'
        ]
        
        for attr in required_attrs:
            assert hasattr(config, attr)
            assert getattr(config, attr) is not None
    
    def test_config_methods_exist(self):
        """Test that all required config methods exist."""
        config = Config()
        
        # Check all required methods
        required_methods = [
            'get_timer_defaults', 'get_log_settings', 'validate_config'
        ]
        
        for method in required_methods:
            assert hasattr(config, method)
            assert callable(getattr(config, method))
    
    def test_config_immutable_after_creation(self):
        """Test that config can be modified after creation."""
        config = Config()
        original_host = config.HOST
        
        # Config should be mutable (for testing purposes)
        config.HOST = '192.168.1.1'
        assert config.HOST == '192.168.1.1'
        assert config.HOST != original_host
    
    @patch.dict(os.environ, {}, clear=True)
    def test_config_with_empty_environment(self):
        """Test config creation with completely empty environment."""
        config = Config()
        
        # Should use all default values
        assert config.FLASK_ENV == 'development'
        assert config.FLASK_DEBUG is True
        assert config.SECRET_KEY == 'dev-secret-key-change-in-production'
        assert config.HOST == '127.0.0.1'
        assert config.PORT == 5000
    
    def test_config_timer_defaults_types(self):
        """Test that timer defaults return correct types."""
        config = Config()
        defaults = config.get_timer_defaults()
        
        for key, value in defaults.items():
            assert isinstance(value, int)
            assert value > 0
    
    def test_config_log_settings_types(self):
        """Test that log settings return correct types."""
        config = Config()
        settings = config.get_log_settings()
        
        assert isinstance(settings['level'], str)
        assert isinstance(settings['file_path'], str)
        assert len(settings['level']) > 0
        assert len(settings['file_path']) > 0
    
    def test_config_validation_returns_boolean(self):
        """Test that config validation returns boolean."""
        config = Config()
        result = config.validate_config()
        
        assert isinstance(result, bool)
    
    @patch.dict(os.environ, {
        'FLASK_ENV': '',
        'SECRET_KEY': '',
        'HOST': ''
    })
    def test_config_with_empty_string_env_vars(self):
        """Test config with empty string environment variables."""
        config = Config()
        
        # Empty strings should be treated as defaults
        assert config.FLASK_ENV == 'development'
        assert config.SECRET_KEY == 'dev-secret-key-change-in-production'
        assert config.HOST == '127.0.0.1'