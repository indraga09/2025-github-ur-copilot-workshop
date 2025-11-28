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