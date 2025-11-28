"""
Test cases for Pomodoro Timer statistics.
"""
import pytest
from datetime import datetime, timezone, date, timedelta
from unittest.mock import patch

from utils.statistics import (
    calculate_daily_stats,
    calculate_weekly_stats,
    get_completion_rate,
    get_average_session_time,
    get_productivity_trends,
    filter_sessions_by_date_range,
    get_session_type_distribution,
    get_peak_productivity_hours,
    create_empty_stats
)
from utils.session_manager import PomodoroSession


class TestStatisticsCalculation:
    """Test statistics calculation functions."""
    
    @pytest.fixture
    def sample_sessions(self):
        """Create sample sessions for testing."""
        sessions = []
        
        # Create sessions for different dates and times
        base_time = datetime(2025, 11, 28, 9, 0, 0, tzinfo=timezone.utc)
        
        for i in range(5):
            # Work sessions
            with patch('utils.session_manager.datetime') as mock_dt:
                session_time = base_time + timedelta(hours=i*2)
                mock_dt.now.return_value = session_time
                
                work_session = PomodoroSession('work', 25, f'Work task {i}')
                if i < 4:  # Complete 4 out of 5 work sessions
                    work_session.complete_session()
                sessions.append(work_session)
                
                # Add some break sessions
                if i < 3:
                    break_session = PomodoroSession('short_break', 5)
                    break_session.complete_session()
                    sessions.append(break_session)
        
        return sessions
    
    @pytest.fixture
    def weekly_sessions(self):
        """Create sessions spanning a week."""
        sessions = []
        
        # Create sessions for the last 7 days
        today = datetime(2025, 11, 28, 10, 0, 0, tzinfo=timezone.utc)
        
        for day_offset in range(7):
            session_date = today - timedelta(days=day_offset)
            
            with patch('utils.session_manager.datetime') as mock_dt:
                mock_dt.now.return_value = session_date
                
                # 2-3 sessions per day
                for hour in [9, 11, 14]:
                    if day_offset < 3 or hour != 14:  # Skip some sessions
                        session_time = session_date.replace(hour=hour)
                        mock_dt.now.return_value = session_time
                        
                        session = PomodoroSession('work', 25, f'Task day {day_offset}')
                        if day_offset < 5:  # Complete most sessions
                            session.complete_session()
                        sessions.append(session)
        
        return sessions
    
    def test_calculate_daily_stats_empty(self):
        """Test daily stats calculation with empty sessions."""
        stats = calculate_daily_stats([])
        
        assert stats['total_sessions'] == 0
        assert stats['completed_sessions'] == 0
        assert stats['total_focus_minutes'] == 0
        assert stats['completion_rate'] == 0.0
    
    @patch('utils.statistics.date')
    def test_calculate_daily_stats_success(self, mock_date, sample_sessions):
        """Test successful daily stats calculation."""
        # Mock today's date
        mock_date.today.return_value = date(2025, 11, 28)
        
        stats = calculate_daily_stats(sample_sessions)
        
        assert 'date' in stats
        assert 'total_sessions' in stats
        assert 'completed_sessions' in stats
        assert 'total_focus_minutes' in stats
        assert 'completion_rate' in stats
        assert 'work_sessions' in stats
        assert 'break_sessions' in stats
        
        # Should only count today's sessions
        assert stats['date'] == '2025-11-28'
        assert stats['total_sessions'] >= 0
        assert stats['completed_sessions'] <= stats['total_sessions']
        assert 0.0 <= stats['completion_rate'] <= 100.0
    
    def test_calculate_weekly_stats_empty(self):
        """Test weekly stats calculation with empty sessions."""
        stats = calculate_weekly_stats([])
        
        assert stats['total_sessions'] == 0
        assert stats['completed_sessions'] == 0
        assert stats['total_focus_minutes'] == 0
        assert stats['completion_rate'] == 0.0
    
    @patch('utils.statistics.date')
    def test_calculate_weekly_stats_success(self, mock_date, weekly_sessions):
        """Test successful weekly stats calculation."""
        # Mock today's date
        mock_date.today.return_value = date(2025, 11, 28)
        
        stats = calculate_weekly_stats(weekly_sessions)
        
        assert 'week_start' in stats
        assert 'total_sessions' in stats
        assert 'completed_sessions' in stats
        assert 'total_focus_minutes' in stats
        assert 'completion_rate' in stats
        assert 'daily_breakdown' in stats
        
        assert stats['total_sessions'] >= 0
        assert stats['completed_sessions'] <= stats['total_sessions']
        assert 0.0 <= stats['completion_rate'] <= 100.0
        
        # Check daily breakdown
        assert isinstance(stats['daily_breakdown'], dict)
        assert len(stats['daily_breakdown']) == 7
        
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in weekdays:
            assert day in stats['daily_breakdown']
            assert 'sessions' in stats['daily_breakdown'][day]
            assert 'completed' in stats['daily_breakdown'][day]
    
    def test_get_completion_rate_empty(self):
        """Test completion rate with empty sessions."""
        rate = get_completion_rate([])
        assert rate == 0.0
    
    def test_get_completion_rate_all_completed(self, sample_sessions):
        """Test completion rate with all completed sessions."""
        # Complete all sessions
        for session in sample_sessions:
            session.completed = True
        
        rate = get_completion_rate(sample_sessions)
        assert rate == 100.0
    
    def test_get_completion_rate_none_completed(self, sample_sessions):
        """Test completion rate with no completed sessions."""
        # Mark all sessions as incomplete
        for session in sample_sessions:
            session.completed = False
        
        rate = get_completion_rate(sample_sessions)
        assert rate == 0.0
    
    def test_get_completion_rate_partial(self, sample_sessions):
        """Test completion rate with partially completed sessions."""
        # Complete half of the sessions
        for i, session in enumerate(sample_sessions):
            session.completed = i < len(sample_sessions) // 2
        
        rate = get_completion_rate(sample_sessions)
        expected_rate = (len(sample_sessions) // 2) / len(sample_sessions) * 100
        assert abs(rate - expected_rate) < 0.1  # Allow for rounding
    
    def test_get_average_session_time_empty(self):
        """Test average session time with empty sessions."""
        avg_time = get_average_session_time([])
        assert avg_time == 0.0
    
    def test_get_average_session_time_no_completed(self, sample_sessions):
        """Test average session time with no completed sessions."""
        # Mark all sessions as incomplete
        for session in sample_sessions:
            session.completed = False
        
        avg_time = get_average_session_time(sample_sessions)
        assert avg_time == 0.0
    
    def test_get_average_session_time_success(self):
        """Test successful average session time calculation."""
        sessions = []
        durations = [20, 25, 30, 25]  # Should average to 25
        
        for duration in durations:
            session = PomodoroSession('work', duration, 'Test task')
            session.complete_session()
            sessions.append(session)
        
        avg_time = get_average_session_time(sessions)
        assert avg_time == 25.0
    
    def test_get_average_session_time_mixed_completed(self):
        """Test average session time with mixed completed/incomplete sessions."""
        sessions = []
        
        # Completed sessions with durations [20, 30] - average 25
        for duration in [20, 30]:
            session = PomodoroSession('work', duration, 'Test task')
            session.complete_session()
            sessions.append(session)
        
        # Incomplete session (should be ignored)
        incomplete_session = PomodoroSession('work', 60, 'Incomplete task')
        sessions.append(incomplete_session)
        
        avg_time = get_average_session_time(sessions)
        assert avg_time == 25.0
    
    def test_get_productivity_trends_empty(self):
        """Test productivity trends with empty sessions."""
        trends = get_productivity_trends([])
        
        assert trends['trend'] == 'stable'
        assert trends['change'] == 0.0
        assert 'No data available' in trends['description']
    
    def test_get_productivity_trends_insufficient_data(self):
        """Test productivity trends with insufficient data."""
        # Only one session
        session = PomodoroSession('work', 25, 'Single task')
        trends = get_productivity_trends([session])
        
        assert trends['trend'] == 'stable'
        assert trends['change'] == 0.0
        assert 'Insufficient data' in trends['description']
    
    @patch('utils.statistics.date')
    def test_get_productivity_trends_improving(self, mock_date):
        """Test productivity trends showing improvement."""
        mock_date.today.return_value = date(2025, 11, 28)
        
        sessions = []
        
        # Last week: 2 completed sessions
        last_week_date = datetime(2025, 11, 20, 10, 0, tzinfo=timezone.utc)
        for i in range(4):
            with patch('utils.session_manager.datetime') as mock_dt:
                mock_dt.now.return_value = last_week_date + timedelta(hours=i)
                session = PomodoroSession('work', 25, f'Last week {i}')
                if i < 2:  # Complete 2 out of 4
                    session.complete_session()
                sessions.append(session)
        
        # This week: 4 completed sessions
        this_week_date = datetime(2025, 11, 25, 10, 0, tzinfo=timezone.utc)
        for i in range(4):
            with patch('utils.session_manager.datetime') as mock_dt:
                mock_dt.now.return_value = this_week_date + timedelta(hours=i)
                session = PomodoroSession('work', 25, f'This week {i}')
                session.complete_session()  # Complete all 4
                sessions.append(session)
        
        trends = get_productivity_trends(sessions)
        
        assert trends['trend'] == 'improving'
        assert trends['change'] == 100.0  # 100% improvement (2 -> 4 = +100%)
        assert 'increased' in trends['description']
    
    @patch('utils.statistics.date')
    def test_get_productivity_trends_declining(self, mock_date):
        """Test productivity trends showing decline."""
        mock_date.today.return_value = date(2025, 11, 28)
        
        sessions = []
        
        # Last week: 4 completed sessions
        last_week_date = datetime(2025, 11, 20, 10, 0, tzinfo=timezone.utc)
        for i in range(4):
            with patch('utils.session_manager.datetime') as mock_dt:
                mock_dt.now.return_value = last_week_date + timedelta(hours=i)
                session = PomodoroSession('work', 25, f'Last week {i}')
                session.complete_session()  # Complete all 4
                sessions.append(session)
        
        # This week: 1 completed session
        this_week_date = datetime(2025, 11, 25, 10, 0, tzinfo=timezone.utc)
        for i in range(4):
            with patch('utils.session_manager.datetime') as mock_dt:
                mock_dt.now.return_value = this_week_date + timedelta(hours=i)
                session = PomodoroSession('work', 25, f'This week {i}')
                if i == 0:  # Complete only 1 out of 4
                    session.complete_session()
                sessions.append(session)
        
        trends = get_productivity_trends(sessions)
        
        assert trends['trend'] == 'declining'
        assert trends['change'] == -75.0  # 75% decline (4 -> 1 = -75%)
        assert 'decreased' in trends['description']
    
    def test_filter_sessions_by_date_range(self):
        """Test filtering sessions by date range."""
        sessions = []
        
        # Create sessions for different dates
        dates = [
            datetime(2025, 11, 25, 10, 0, tzinfo=timezone.utc),
            datetime(2025, 11, 26, 10, 0, tzinfo=timezone.utc),
            datetime(2025, 11, 27, 10, 0, tzinfo=timezone.utc),
            datetime(2025, 11, 28, 10, 0, tzinfo=timezone.utc),
            datetime(2025, 11, 29, 10, 0, tzinfo=timezone.utc),
        ]
        
        for i, session_date in enumerate(dates):
            with patch('utils.session_manager.datetime') as mock_dt:
                mock_dt.now.return_value = session_date
                session = PomodoroSession('work', 25, f'Task {i}')
                sessions.append(session)
        
        # Filter sessions from Nov 26 to Nov 28 (inclusive)
        start_date = date(2025, 11, 26)
        end_date = date(2025, 11, 28)
        
        filtered = filter_sessions_by_date_range(sessions, start_date, end_date)
        
        assert len(filtered) == 3  # Should include sessions from 26th, 27th, and 28th
        for session in filtered:
            assert start_date <= session.start_time.date() <= end_date
    
    def test_get_session_type_distribution_empty(self):
        """Test session type distribution with empty sessions."""
        distribution = get_session_type_distribution([])
        
        expected = {'work': 0, 'short_break': 0, 'long_break': 0}
        assert distribution == expected
    
    def test_get_session_type_distribution_success(self):
        """Test successful session type distribution calculation."""
        sessions = []
        
        # Create different types of sessions
        session_types = ['work'] * 5 + ['short_break'] * 3 + ['long_break'] * 2
        
        for session_type in session_types:
            session = PomodoroSession(session_type, 25, 'Test task')
            sessions.append(session)
        
        distribution = get_session_type_distribution(sessions)
        
        assert distribution['work'] == 5
        assert distribution['short_break'] == 3
        assert distribution['long_break'] == 2
    
    def test_get_session_type_distribution_invalid_types(self):
        """Test session type distribution with invalid session types."""
        sessions = []
        
        # Create sessions with invalid types (should be ignored)
        for session_type in ['work', 'invalid_type', 'short_break']:
            session = PomodoroSession('work', 25, 'Test task')  # Create valid session
            session.session_type = session_type  # Then modify type
            sessions.append(session)
        
        distribution = get_session_type_distribution(sessions)
        
        assert distribution['work'] == 1
        assert distribution['short_break'] == 1
        assert distribution['long_break'] == 0
        # Invalid type should not be counted
    
    def test_get_peak_productivity_hours_empty(self):
        """Test peak productivity hours with empty sessions."""
        result = get_peak_productivity_hours([])
        
        assert result['peak_hour'] is None
        assert result['sessions_count'] == 0
    
    def test_get_peak_productivity_hours_no_completed_work(self):
        """Test peak productivity hours with no completed work sessions."""
        sessions = []
        
        # Create incomplete work sessions and completed break sessions
        work_session = PomodoroSession('work', 25, 'Incomplete work')
        break_session = PomodoroSession('short_break', 5)
        break_session.complete_session()
        
        sessions.extend([work_session, break_session])
        
        result = get_peak_productivity_hours(sessions)
        
        assert result['peak_hour'] is None
        assert result['sessions_count'] == 0
    
    def test_get_peak_productivity_hours_success(self):
        """Test successful peak productivity hours calculation."""
        sessions = []
        
        # Create completed work sessions at different hours
        # 9 AM: 3 sessions, 10 AM: 1 session, 2 PM: 2 sessions
        hours_and_counts = [(9, 3), (10, 1), (14, 2)]
        
        for hour, count in hours_and_counts:
            for i in range(count):
                session_time = datetime(2025, 11, 28, hour, i*15, tzinfo=timezone.utc)
                with patch('utils.session_manager.datetime') as mock_dt:
                    mock_dt.now.return_value = session_time
                    session = PomodoroSession('work', 25, f'Task {hour}:{i}')
                    session.complete_session()
                    sessions.append(session)
        
        result = get_peak_productivity_hours(sessions)
        
        assert result['peak_hour'] == 9  # Most sessions at 9 AM
        assert result['sessions_count'] == 3
        assert 'hourly_distribution' in result
        assert result['hourly_distribution'][9] == 3
        assert result['hourly_distribution'][10] == 1
        assert result['hourly_distribution'][14] == 2
    
    def test_create_empty_stats(self):
        """Test creating empty statistics structure."""
        stats = create_empty_stats()
        
        expected_keys = ['total_sessions', 'completed_sessions', 'total_focus_minutes', 'completion_rate']
        for key in expected_keys:
            assert key in stats
            assert stats[key] == 0 or stats[key] == 0.0
        
        assert stats['total_sessions'] == 0
        assert stats['completed_sessions'] == 0
        assert stats['total_focus_minutes'] == 0
        assert stats['completion_rate'] == 0.0