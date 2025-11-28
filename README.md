# GitHub Copilot Workshop - Pomodoro Timer

A modern, web-based Pomodoro Timer application built with Flask and vanilla JavaScript. This project demonstrates best practices for AI-assisted development using GitHub Copilot.

## Features

🍅 **Core Timer Functionality**
- 25-minute work sessions
- 5-minute short breaks  
- 15-minute long breaks after 4 work sessions
- Start, pause, and reset controls
- Visual progress indicators

📊 **Session Tracking**
- Automatic session logging to backend
- Session history with filtering
- Statistics dashboard (completion rates, focus time)
- Data export functionality

🎨 **Modern UI**
- Responsive design for desktop and mobile
- Clean, minimalist interface
- Real-time updates
- Accessibility features

🔧 **Technical Features**
- Flask backend with REST API
- Local storage for session persistence
- File-based session logging
- Modular JavaScript architecture

## Installation

### Prerequisites
- Python 3.8+
- [uv](https://docs.astral.sh/uv/#installation) package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd 2025-github-ur-copilot-workshop
   ```

2. **Create virtual environment**
   ```bash
   uv venv
   ```

3. **Install dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

## Usage

### Running the Application

1. **Start the Flask server**
   ```bash
   uv run python app.py
   ```

2. **Open your browser**
   Navigate to http://127.0.0.1:5000

### Using the Timer

1. **Set a task** (optional): Enter what you're working on in the task input field
2. **Start timer**: Click the Start button to begin a 25-minute work session
3. **Take breaks**: Timer automatically switches to break sessions after work sessions
4. **View history**: Navigate to the History page to see completed sessions and statistics

## Testing

The application includes comprehensive unit, integration, and frontend tests using pytest.

### Running Tests

#### Run All Tests
```bash
# Activate virtual environment and run all tests
source .venv/bin/activate
python -m pytest
```

#### Run Specific Test Categories
```bash
# Unit tests only
python -m pytest -m unit

# Integration tests only
python -m pytest -m integration

# Backend tests only
python -m pytest tests/backend/

# Specific test file
python -m pytest tests/backend/test_session_manager.py

# Specific test class
python -m pytest tests/backend/test_session_manager.py::TestPomodoroSession

# Specific test method
python -m pytest tests/backend/test_session_manager.py::TestPomodoroSession::test_session_creation
```

#### Test Coverage
```bash
# Run tests with coverage report
python -m pytest --cov=utils --cov=app --cov=config --cov-report=html

# View coverage report
open htmlcov/index.html
```

#### Verbose Testing
```bash
# Run with verbose output
python -m pytest -v

# Run with extra verbose output and show local variables on failure
python -m pytest -vv -l

# Run failed tests only
python -m pytest --lf
```

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── backend/                 # Backend Python tests
│   ├── test_app.py         # Flask application tests
│   ├── test_config.py      # Configuration tests  
│   ├── test_logger.py      # Session logging tests
│   ├── test_session_manager.py  # Session management tests
│   └── test_statistics.py # Statistics calculation tests
├── frontend/               # Frontend JavaScript tests
│   └── test_frontend.py   # Frontend test placeholders
└── integration/           # End-to-end integration tests
    └── test_integration.py # Full workflow tests
```

### Test Categories

- **Unit Tests** (`-m unit`): Test individual functions and classes in isolation
- **Integration Tests** (`-m integration`): Test complete workflows and component interactions
- **Frontend Tests** (`-m frontend`): Test JavaScript functionality (basic structure provided)
- **Slow Tests** (`-m slow`): Tests that take longer to run (large datasets, etc.)

### Writing New Tests

When adding new functionality, create corresponding tests:

1. **Unit tests** for individual functions in the appropriate `test_*.py` file
2. **Integration tests** if the feature involves multiple components
3. Use the shared fixtures in `conftest.py` for common test data
4. Follow the naming convention: `test_*` for functions, `Test*` for classes

### Test Configuration

- **pytest.ini**: Main pytest configuration with coverage settings
- **conftest.py**: Shared fixtures and test configuration
- **Coverage**: Configured to report on `utils/`, `app.py`, and `config.py`
- **HTML Reports**: Generated in `htmlcov/` directory

### Example Test Commands

```bash
# Quick test run (unit tests only)
python -m pytest -m unit --tb=short

# Full test suite with coverage
python -m pytest --cov --cov-report=term-missing

# Test a specific feature
python -m pytest -k "session_manager" -v

# Test with debugging output
python -m pytest -s tests/backend/test_logger.py::TestSessionLogger::test_log_session_success
```

## Project Structure

The application follows a **frontend-first architecture** with modular, testable components designed for GitHub Copilot development workflows.

## GitHub Copilot Best Practices

This project demonstrates:
- Clear function signatures with type hints
- Small, focused functions (10-20 lines)
- Descriptive comments for AI context
- Consistent patterns and architecture
- Test-driven development approach

For detailed documentation, see `architecture.md` and `development-plan.md`.