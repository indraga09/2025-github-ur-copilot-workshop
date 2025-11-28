"""Logging system for Pomodoro Timer sessions."""
import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional
from utils.session_manager import PomodoroSession


class SessionLogger:
    """Handles logging of Pomodoro sessions to file."""
    
    def __init__(self, log_file_path: str) -> None:
        """Initialize session logger.
        
        Args:
            log_file_path: Path to log file
        """
        self.log_file_path = Path(log_file_path)
        self.ensure_log_directory()
    
    def log_session(self, session: PomodoroSession) -> bool:
        """Log a completed session to file.
        
        Args:
            session: PomodoroSession to log
            
        Returns:
            True if logged successfully, False otherwise
        """
        try:
            log_entry = create_log_entry(session)
            
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
            
            return True
        except Exception as e:
            print(f"Failed to log session: {e}")
            return False
    
    def read_sessions(self, limit: int = 100) -> List[PomodoroSession]:
        """Read recent sessions from log file.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of PomodoroSession objects
        """
        sessions = []
        
        if not self.log_file_path.exists():
            return sessions
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Get last 'limit' lines
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            
            for line in reversed(recent_lines):
                line = line.strip()
                if line:
                    session = parse_log_entry(line)
                    if session:
                        sessions.append(session)
            
            return sessions
        except Exception as e:
            print(f"Failed to read sessions: {e}")
            return []
    
    def read_sessions_by_date(self, target_date: date) -> List[PomodoroSession]:
        """Read sessions for a specific date.
        
        Args:
            target_date: Date to filter sessions
            
        Returns:
            List of sessions for the specified date
        """
        all_sessions = self.read_sessions(limit=1000)  # Read more for date filtering
        
        filtered_sessions = []
        for session in all_sessions:
            if session.start_time.date() == target_date:
                filtered_sessions.append(session)
        
        return filtered_sessions
    
    def ensure_log_directory(self) -> bool:
        """Ensure log directory exists.
        
        Returns:
            True if directory exists or was created successfully
        """
        try:
            self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Failed to create log directory: {e}")
            return False
    
    def rotate_log_if_needed(self) -> bool:
        """Rotate log file if it gets too large.
        
        Returns:
            True if rotation was successful or not needed
        """
        if not self.log_file_path.exists():
            return True
        
        try:
            file_size = self.log_file_path.stat().st_size
            # Rotate if file is larger than 10MB
            if file_size > 10 * 1024 * 1024:
                backup_path = self.log_file_path.with_suffix('.log.old')
                self.log_file_path.rename(backup_path)
            
            return True
        except Exception as e:
            print(f"Failed to rotate log file: {e}")
            return False


def create_log_entry(session: PomodoroSession) -> str:
    """Create log entry string from session.
    
    Args:
        session: PomodoroSession to convert
        
    Returns:
        JSON string representing the session
    """
    return json.dumps(session.to_dict(), separators=(',', ':'))


def parse_log_entry(log_line: str) -> Optional[PomodoroSession]:
    """Parse log entry string to session object.
    
    Args:
        log_line: JSON string from log file
        
    Returns:
        PomodoroSession object or None if parsing fails
    """
    try:
        data = json.loads(log_line)
        return PomodoroSession.from_dict(data)
    except Exception as e:
        print(f"Failed to parse log entry: {e}")
        return None


def validate_log_file(file_path: str) -> bool:
    """Validate log file format and accessibility.
    
    Args:
        file_path: Path to log file
        
    Returns:
        True if file is valid or doesn't exist, False otherwise
    """
    path = Path(file_path)
    
    if not path.exists():
        return True  # File doesn't exist yet, which is fine
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        json.loads(line)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON at line {line_num}: {line}")
                        return False
        
        return True
    except Exception as e:
        print(f"Failed to validate log file: {e}")
        return False