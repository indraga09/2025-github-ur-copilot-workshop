"""Configuration settings for Pomodoro Timer application."""
import os
from typing import Dict, Any


class Config:
    """Configuration class for application settings."""
    
    def __init__(self) -> None:
        """Initialize configuration with environment variables."""
        self.FLASK_ENV = os.getenv('FLASK_ENV', 'development') or 'development'
        self.FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ['true', '1']
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production') or 'dev-secret-key-change-in-production'
        self.HOST = os.getenv('HOST', '127.0.0.1') or '127.0.0.1'
        self.PORT = int(os.getenv('PORT', '5000'))
    
    def get_timer_defaults(self) -> Dict[str, int]:
        """Get default timer durations in minutes.
        
        Returns:
            Dictionary with timer default values
        """
        return {
            'work_minutes': int(os.getenv('DEFAULT_WORK_MINUTES', '25')),
            'short_break_minutes': int(os.getenv('DEFAULT_SHORT_BREAK_MINUTES', '5')),
            'long_break_minutes': int(os.getenv('DEFAULT_LONG_BREAK_MINUTES', '15'))
        }
    
    def get_log_settings(self) -> Dict[str, Any]:
        """Get logging configuration settings.
        
        Returns:
            Dictionary with logging settings
        """
        return {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'file_path': os.getenv('LOG_FILE_PATH', 'logs/pomodoro_sessions.log')
        }
    
    def validate_config(self) -> bool:
        """Validate configuration values.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        timer_defaults = self.get_timer_defaults()
        
        # Check timer values are positive
        for key, value in timer_defaults.items():
            if value <= 0:
                return False
        
        # Check port is valid
        if not (1 <= self.PORT <= 65535):
            return False
            
        return True