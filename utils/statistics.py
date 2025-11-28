"""Statistics calculation for Pomodoro Timer sessions."""
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from utils.session_manager import PomodoroSession


def calculate_daily_stats(sessions: List[PomodoroSession]) -> Dict[str, Any]:
    """Calculate daily session statistics.
    
    Args:
        sessions: List of PomodoroSession objects
        
    Returns:
        Dictionary with daily statistics
    """
    if not sessions:
        return create_empty_stats()
    
    today = date.today()
    today_sessions = [s for s in sessions if s.start_time.date() == today]
    
    total_sessions = len(today_sessions)
    completed_sessions = sum(1 for s in today_sessions if s.completed)
    work_sessions = [s for s in today_sessions if s.session_type == 'work' and s.completed]
    
    total_focus_time = sum(s.duration_minutes for s in work_sessions)
    completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    return {
        'date': today.isoformat(),
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'total_focus_minutes': total_focus_time,
        'completion_rate': round(completion_rate, 1),
        'work_sessions': len(work_sessions),
        'break_sessions': len([s for s in today_sessions if s.session_type != 'work'])
    }


def calculate_weekly_stats(sessions: List[PomodoroSession]) -> Dict[str, Any]:
    """Calculate weekly session statistics.
    
    Args:
        sessions: List of PomodoroSession objects
        
    Returns:
        Dictionary with weekly statistics
    """
    if not sessions:
        return create_empty_stats()
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_sessions = [s for s in sessions 
                    if week_start <= s.start_time.date() <= today]
    
    total_sessions = len(week_sessions)
    completed_sessions = sum(1 for s in week_sessions if s.completed)
    work_sessions = [s for s in week_sessions if s.session_type == 'work' and s.completed]
    
    total_focus_time = sum(s.duration_minutes for s in work_sessions)
    completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    # Daily breakdown
    daily_breakdown = {}
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_sessions = [s for s in week_sessions if s.start_time.date() == day]
        daily_breakdown[day.strftime('%A')] = {
            'sessions': len(day_sessions),
            'completed': sum(1 for s in day_sessions if s.completed)
        }
    
    return {
        'week_start': week_start.isoformat(),
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'total_focus_minutes': total_focus_time,
        'completion_rate': round(completion_rate, 1),
        'daily_breakdown': daily_breakdown
    }


def get_completion_rate(sessions: List[PomodoroSession]) -> float:
    """Calculate overall completion rate.
    
    Args:
        sessions: List of PomodoroSession objects
        
    Returns:
        Completion rate as percentage (0-100)
    """
    if not sessions:
        return 0.0
    
    completed = sum(1 for s in sessions if s.completed)
    total = len(sessions)
    return round((completed / total * 100), 1) if total > 0 else 0.0


def get_average_session_time(sessions: List[PomodoroSession]) -> float:
    """Calculate average session time for completed sessions.
    
    Args:
        sessions: List of PomodoroSession objects
        
    Returns:
        Average session time in minutes
    """
    completed_sessions = [s for s in sessions if s.completed]
    if not completed_sessions:
        return 0.0
    
    total_minutes = sum(s.duration_minutes for s in completed_sessions)
    return round(total_minutes / len(completed_sessions), 1)


def get_productivity_trends(sessions: List[PomodoroSession]) -> Dict[str, Any]:
    """Analyze productivity trends over time.
    
    Args:
        sessions: List of PomodoroSession objects
        
    Returns:
        Dictionary with trend analysis
    """
    if not sessions:
        return {'trend': 'stable', 'change': 0.0, 'description': 'No data available'}
    
    # Get last 14 days of data
    today = date.today()
    two_weeks_ago = today - timedelta(days=14)
    recent_sessions = [s for s in sessions 
                      if s.start_time.date() >= two_weeks_ago]
    
    if len(recent_sessions) < 2:
        return {'trend': 'stable', 'change': 0.0, 'description': 'Insufficient data'}
    
    # Split into two weeks
    one_week_ago = today - timedelta(days=7)
    last_week = [s for s in recent_sessions 
                if s.start_time.date() < one_week_ago]
    this_week = [s for s in recent_sessions 
                if s.start_time.date() >= one_week_ago]
    
    last_week_completed = sum(1 for s in last_week if s.completed)
    this_week_completed = sum(1 for s in this_week if s.completed)
    
    if last_week_completed == 0:
        if this_week_completed > 0:
            return {'trend': 'improving', 'change': 100.0, 'description': 'Started completing sessions'}
        else:
            return {'trend': 'stable', 'change': 0.0, 'description': 'No completed sessions'}
    
    change_percent = ((this_week_completed - last_week_completed) / last_week_completed) * 100
    
    if change_percent > 10:
        trend = 'improving'
        description = f'Completed sessions increased by {change_percent:.1f}%'
    elif change_percent < -10:
        trend = 'declining'
        description = f'Completed sessions decreased by {abs(change_percent):.1f}%'
    else:
        trend = 'stable'
        description = 'Completion rate is stable'
    
    return {
        'trend': trend,
        'change': round(change_percent, 1),
        'description': description
    }


def filter_sessions_by_date_range(sessions: List[PomodoroSession], 
                                 start_date: date, 
                                 end_date: date) -> List[PomodoroSession]:
    """Filter sessions by date range.
    
    Args:
        sessions: List of PomodoroSession objects
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        
    Returns:
        Filtered list of sessions
    """
    return [s for s in sessions 
            if start_date <= s.start_time.date() <= end_date]


def get_session_type_distribution(sessions: List[PomodoroSession]) -> Dict[str, int]:
    """Get distribution of session types.
    
    Args:
        sessions: List of PomodoroSession objects
        
    Returns:
        Dictionary with session type counts
    """
    distribution = {
        'work': 0,
        'short_break': 0,
        'long_break': 0
    }
    
    for session in sessions:
        if session.session_type in distribution:
            distribution[session.session_type] += 1
    
    return distribution


def get_peak_productivity_hours(sessions: List[PomodoroSession]) -> Dict[str, Any]:
    """Analyze peak productivity hours.
    
    Args:
        sessions: List of PomodoroSession objects
        
    Returns:
        Dictionary with peak hours analysis
    """
    if not sessions:
        return {'peak_hour': None, 'sessions_count': 0}
    
    # Count completed work sessions by hour
    hourly_counts = {}
    for session in sessions:
        if session.session_type == 'work' and session.completed:
            hour = session.start_time.hour
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
    
    if not hourly_counts:
        return {'peak_hour': None, 'sessions_count': 0}
    
    peak_hour = max(hourly_counts, key=hourly_counts.get)
    sessions_count = hourly_counts[peak_hour]
    
    return {
        'peak_hour': peak_hour,
        'sessions_count': sessions_count,
        'hourly_distribution': hourly_counts
    }


def create_empty_stats() -> Dict[str, Any]:
    """Create empty statistics structure.
    
    Returns:
        Dictionary with zero values for all statistics
    """
    return {
        'total_sessions': 0,
        'completed_sessions': 0,
        'total_focus_minutes': 0,
        'completion_rate': 0.0
    }