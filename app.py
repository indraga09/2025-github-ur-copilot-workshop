"""Flask application for Pomodoro Timer."""
import logging
from datetime import datetime, date
from flask import Flask, render_template, Response, jsonify, request
from typing import Dict, Any, Tuple
from config import Config
from utils.session_manager import PomodoroSession, validate_session_type
from utils.logger import SessionLogger


def create_app() -> Flask:
    """Create and configure the Flask application.
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config = Config()
    app.config.from_object(config)
    
    # Configure logging
    configure_logging(app)
    
    # Register routes
    register_routes(app)
    
    # Validate configuration
    if not config.validate_config():
        app.logger.warning("Configuration validation failed. Please check your settings.")
    
    return app


def configure_logging(app: Flask) -> None:
    """Configure application logging.
    
    Args:
        app: Flask application instance
    """
    config = Config()
    log_settings = config.get_log_settings()
    
    # Set logging level
    log_level = getattr(logging, log_settings['level'].upper(), logging.INFO)
    app.logger.setLevel(log_level)
    
    # Create file handler if not exists
    if not app.logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)


def register_routes(app: Flask) -> None:
    """Register application routes.
    
    Args:
        app: Flask application instance
    """
    
    @app.route('/')
    def serve_index() -> str:
        """Serve the main timer page.
        
        Returns:
            Rendered HTML template
        """
        config = Config()
        timer_defaults = config.get_timer_defaults()
        return render_template_with_config('index.html', timer_defaults=timer_defaults)
    
    @app.route('/health')
    def health_check() -> Dict[str, str]:
        """Health check endpoint.
        
        Returns:
            JSON response with health status
        """
        return jsonify({'status': 'healthy', 'service': 'pomodoro-timer'})
    
    @app.route('/history')
    def serve_history() -> str:
        """Serve the session history page.
        
        Returns:
            Rendered HTML template
        """
        return render_template_with_config('history.html')
    
    @app.route('/api/sessions', methods=['POST'])
    def api_create_session() -> Response:
        """Create a new session log entry.
        
        Returns:
            JSON response with creation status
        """
        try:
            session_data = create_session()
            return jsonify(session_data), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            app.logger.error(f"Failed to create session: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/sessions', methods=['GET'])
    def api_get_sessions() -> Response:
        """Get session history.
        
        Returns:
            JSON response with session list
        """
        try:
            sessions_data = get_sessions()
            return jsonify(sessions_data), 200
        except Exception as e:
            app.logger.error(f"Failed to get sessions: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/stats', methods=['GET'])
    def api_get_stats() -> Response:
        """Get session statistics.
        
        Returns:
            JSON response with statistics
        """
        try:
            stats_data = get_session_stats()
            return jsonify(stats_data), 200
        except Exception as e:
            app.logger.error(f"Failed to get stats: {e}")
            return jsonify({'error': 'Internal server error'}), 500


def render_template_with_config(template: str, **kwargs) -> str:
    """Render template with configuration context.
    
    Args:
        template: Template filename
        **kwargs: Additional template variables
        
    Returns:
        Rendered HTML string
    """
    config = Config()
    return render_template(
        template,
        config=config,
        **kwargs
    )


def create_session() -> Dict[str, Any]:
    """Create a new session from request data.
    
    Returns:
        Dictionary with session creation result
    """
    try:
        request_data = request.get_json(force=True)
    except:
        request_data = None
        
    data = validate_session_request(request_data or {})
    
    session = PomodoroSession(
        session_type=data['session_type'],
        duration=data['duration_minutes'],
        task_description=data.get('task_description', '')
    )
    
    if data.get('completed'):
        session.complete_session()
    
    session.interruptions = data.get('interruptions', 0)
    
    # Log the session
    config = Config()
    log_settings = config.get_log_settings()
    logger = SessionLogger(log_settings['file_path'])
    
    success = logger.log_session(session)
    
    return {
        'success': success,
        'session_id': session.session_id,
        'message': 'Session logged successfully' if success else 'Failed to log session'
    }


def get_sessions() -> Dict[str, Any]:
    """Get session history.
    
    Returns:
        Dictionary with session list and metadata
    """
    config = Config()
    log_settings = config.get_log_settings()
    logger = SessionLogger(log_settings['file_path'])
    
    # Get query parameters
    limit = int(request.args.get('limit', '100'))
    date_filter = request.args.get('date')
    
    if date_filter:
        try:
            filter_date = datetime.fromisoformat(date_filter).date()
            sessions = logger.read_sessions_by_date(filter_date)
        except ValueError:
            sessions = logger.read_sessions(limit)
    else:
        sessions = logger.read_sessions(limit)
    
    return {
        'sessions': [session.to_dict() for session in sessions],
        'total': len(sessions)
    }


def get_session_stats() -> Dict[str, Any]:
    """Get session statistics.
    
    Returns:
        Dictionary with session statistics
    """
    config = Config()
    log_settings = config.get_log_settings()
    logger = SessionLogger(log_settings['file_path'])
    
    sessions = logger.read_sessions(limit=1000)
    
    total_sessions = len(sessions)
    completed_sessions = sum(1 for s in sessions if s.completed)
    work_sessions = [s for s in sessions if s.session_type == 'work']
    
    total_focus_minutes = sum(s.duration_minutes for s in work_sessions if s.completed)
    completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    return {
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'total_focus_minutes': total_focus_minutes,
        'completion_rate': round(completion_rate, 1),
        'today_sessions': len([s for s in sessions if s.start_time.date() == date.today()])
    }


def validate_session_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate session request data.
    
    Args:
        request_data: Request data to validate
        
    Returns:
        Validated data dictionary
        
    Raises:
        ValueError: If validation fails
    """
    if not request_data:
        raise ValueError("Request data is required")
    
    session_type = request_data.get('session_type')
    if not session_type or not validate_session_type(session_type):
        raise ValueError("Invalid session type")
    
    duration = request_data.get('duration_minutes')
    if not duration or not isinstance(duration, int) or duration <= 0:
        raise ValueError("Invalid duration")
    
    return request_data


if __name__ == '__main__':
    app = create_app()
    config = Config()
    
    app.logger.info(f"Starting Pomodoro Timer on {config.HOST}:{config.PORT}")
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.FLASK_DEBUG
    )