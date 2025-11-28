/**
 * Main application controller for Pomodoro Timer.
 */

class PomodoroApp {
    /**
     * Initialize Pomodoro application
     */
    constructor() {
        this.timer = null;
        this.storage = new TimerStorage();
        this.currentTask = '';
        this.sessionStartTime = null;
        this.isInitialized = false;
    }
    
    /**
     * Initialize the application
     */
    init() {
        if (this.isInitialized) {
            return;
        }
        
        // Get configuration from window object (set by backend)
        const config = window.TIMER_CONFIG || {
            workMinutes: 25,
            shortBreakMinutes: 5,
            longBreakMinutes: 15
        };
        
        // Create timer instance
        this.timer = new PomodoroTimer(config);
        
        // Set up timer callbacks
        this.timer.onTick((session) => {
            this.updateDisplay(session);
            this.storage.saveCurrentSession(session);
        });
        
        this.timer.onSessionComplete((session) => {
            this.handleSessionComplete(session);
        });
        
        // Bind UI events
        this.bindEvents();
        
        // Load saved session if exists
        this.loadSavedSession();
        
        // Initial display update
        this.updateDisplay(this.timer.getCurrentSession());
        
        // Handle browser visibility changes
        document.addEventListener('visibilitychange', () => {
            handleVisibilityChange(this.timer);
        });
        
        this.isInitialized = true;
        console.log('Pomodoro app initialized');
    }
    
    /**
     * Bind UI event handlers
     */
    bindEvents() {
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const resetBtn = document.getElementById('resetBtn');
        const taskInput = document.getElementById('taskInput');
        
        if (startBtn) {
            startBtn.addEventListener('click', () => this.handleStartClick());
        }
        
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => this.handlePauseClick());
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.handleResetClick());
        }
        
        if (taskInput) {
            taskInput.addEventListener('input', (e) => {
                this.currentTask = e.target.value;
            });
        }
    }
    
    /**
     * Update display with current timer state
     * @param {Object} session - Current session data
     */
    updateDisplay(session) {
        updateTimerDisplay(this.timer.getFormattedTime());
        updateSessionType(session.type);
        
        // Update cycle counter
        const cycleElement = document.getElementById('cycleCount');
        if (cycleElement) {
            cycleElement.textContent = session.cycleCount;
        }
        
        // Update progress bar
        const totalTime = calculateSessionDuration(session.type, this.timer.config) * 60;
        const elapsed = totalTime - session.timeRemaining;
        const percentage = (elapsed / totalTime) * 100;
        this.updateProgress(percentage);
        
        // Update button states
        this.updateButtonStates(session.isRunning);
    }
    
    /**
     * Handle start button click
     */
    handleStartClick() {
        this.timer.start();
        this.sessionStartTime = new Date();
        this.showNotification('Timer started! Stay focused!');
        
        // Create particles during work sessions
        const session = this.timer.getCurrentSession();
        if (session.type === 'work') {
            this.createParticles();
        }
    }
    
    /**
     * Handle pause button click
     */
    handlePauseClick() {
        this.timer.pause();
        this.showNotification('Timer paused');
        this.removeParticles();
    }
    
    /**
     * Handle reset button click
     */
    handleResetClick() {
        this.timer.reset();
        this.sessionStartTime = null;
        this.storage.clearSession();
        this.updateDisplay(this.timer.getCurrentSession());
        this.showNotification('Timer reset');
        this.removeParticles();
    }
    
    /**
     * Handle session completion
     * @param {Object} session - Completed session
     */
    handleSessionComplete(session) {
        const message = showSessionComplete(session.type);
        this.showNotification(message);
        
        // Remove particles when session completes
        this.removeParticles();
        
        // Log completed session to backend
        this.logSessionToBackend(session);
        
        // Auto-start next session if enabled in settings
        const settings = this.storage.loadSettings();
        if (settings.autoStartWork && session.type !== 'work' ||
            settings.autoStartBreaks && session.type === 'work') {
            setTimeout(() => {
                this.timer.start();
                // Create particles for work sessions
                const nextSession = this.timer.getCurrentSession();
                if (nextSession.type === 'work') {
                    this.createParticles();
                }
            }, 3000); // 3 second delay
        }
    }
    
    /**
     * Show notification message
     * @param {string} message - Message to display
     */
    showNotification(message) {
        const notification = document.getElementById('notification');
        const notificationText = document.getElementById('notificationText');
        
        if (notification && notificationText) {
            notificationText.textContent = message;
            notification.style.display = 'block';
            
            // Hide notification after 3 seconds
            setTimeout(() => {
                notification.style.display = 'none';
            }, 3000);
        }
        
        // Browser notification if permission granted
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Pomodoro Timer', { body: message });
        }
    }
    
    /**
     * Update circular progress bar with color transitions
     * @param {number} percentage - Progress percentage (0-100)
     */
    updateProgress(percentage) {
        const progressRing = document.getElementById('progressRing');
        const progressText = document.getElementById('progressText');
        
        if (progressRing) {
            const circumference = 2 * Math.PI * 90; // radius = 90
            const offset = circumference - (percentage / 100) * circumference;
            progressRing.style.strokeDashoffset = offset;
            
            // Dynamic color transitions
            progressRing.classList.remove('progress-early', 'progress-mid', 'progress-urgent');
            if (percentage < 33) {
                progressRing.classList.add('progress-early');
            } else if (percentage < 66) {
                progressRing.classList.add('progress-mid');
            } else {
                progressRing.classList.add('progress-urgent');
            }
        }
        
        if (progressText) {
            progressText.textContent = `${Math.round(percentage)}%`;
        }
        
        // Fallback for old linear progress bar
        const progressFill = document.getElementById('progressFill');
        if (progressFill) {
            progressFill.style.width = `${Math.min(100, Math.max(0, percentage))}%`;
        }
    }
    
    /**
     * Create floating particles during work sessions
     */
    createParticles() {
        const container = document.querySelector('.timer-card');
        if (!container || container.querySelector('.particles-container')) {
            return;
        }
        
        // Check if user prefers reduced motion
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            return;
        }
        
        const particlesDiv = document.createElement('div');
        particlesDiv.className = 'particles-container';
        container.appendChild(particlesDiv);
        
        // Create 20 particles
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 3 + 's';
            particlesDiv.appendChild(particle);
        }
    }
    
    /**
     * Remove particle effects
     */
    removeParticles() {
        const particles = document.querySelector('.particles-container');
        if (particles) {
            particles.remove();
        }
    }
    
    /**
     * Update button states based on timer state
     * @param {boolean} isRunning - Whether timer is running
     */
    updateButtonStates(isRunning) {
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        
        if (startBtn && pauseBtn) {
            if (isRunning) {
                startBtn.style.display = 'none';
                pauseBtn.style.display = 'inline-block';
            } else {
                startBtn.style.display = 'inline-block';
                pauseBtn.style.display = 'none';
            }
        }
    }
    
    /**
     * Load saved session from storage
     */
    loadSavedSession() {
        const savedSession = this.storage.loadCurrentSession();
        if (savedSession && savedSession.timeRemaining > 0) {
            this.timer.currentSession = { ...savedSession };
        }
    }
    
    /**
     * Log completed session to backend
     * @param {Object} session - Session to log
     */
    async logSessionToBackend(session) {
        try {
            const sessionData = {
                session_type: session.type,
                duration_minutes: Math.ceil((session.timeRemaining || 0) / 60),
                task_description: this.currentTask,
                completed: true,
                start_time: this.sessionStartTime?.toISOString(),
                end_time: new Date().toISOString()
            };
            
            const response = await fetch('/api/sessions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(sessionData)
            });
            
            if (response.ok) {
                console.log('Session logged successfully');
            } else {
                console.error('Failed to log session:', response.statusText);
            }
        } catch (error) {
            console.error('Error logging session:', error);
        }
    }
}

/**
 * Update timer display element
 * @param {string} timeString - Formatted time string
 */
function updateTimerDisplay(timeString) {
    const timerElement = document.getElementById('timerDisplay');
    if (timerElement) {
        const timeText = timerElement.querySelector('.time-text');
        if (timeText) {
            timeText.textContent = timeString;
        }
    }
}

/**
 * Update session type indicator
 * @param {string} type - Session type
 */
function updateSessionType(type) {
    const sessionElement = document.getElementById('sessionType');
    if (sessionElement) {
        const sessionText = sessionElement.querySelector('.session-text');
        if (sessionText) {
            const typeNames = {
                'work': 'Work Session',
                'short_break': 'Short Break',
                'long_break': 'Long Break'
            };
            sessionText.textContent = typeNames[type] || 'Work Session';
        }
        
        // Update CSS class for styling
        sessionElement.className = `session-type session-${type.replace('_', '-')}`;
    }
}

/**
 * Show session completion message
 * @param {string} type - Session type that completed
 * @returns {string} Completion message
 */
function showSessionComplete(type) {
    const messages = {
        'work': 'Great work! Time for a break.',
        'short_break': 'Break time over. Ready to focus?',
        'long_break': 'Long break finished. Let\'s get back to work!'
    };
    
    return messages[type] || 'Session completed!';
}

/**
 * Handle browser visibility changes
 * @param {PomodoroTimer} timer - Timer instance
 */
function handleVisibilityChange(timer) {
    if (document.hidden) {
        // Tab became hidden - timer continues running
        console.log('Tab hidden - timer continues in background');
    } else {
        // Tab became visible - update display
        console.log('Tab visible - updating display');
        if (timer && typeof timer.updateDisplay === 'function') {
            timer.updateDisplay();
        }
    }
}

/**
 * Play notification sound (placeholder - will be implemented in Phase 7)
 * @param {string} soundType - Type of sound to play
 */
function playNotificationSound(soundType) {
    // Placeholder for audio functionality
    console.log(`Playing sound: ${soundType}`);
}

// Initialize app when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const app = new PomodoroApp();
        app.init();
        
        // Make app globally accessible for debugging
        window.pomodoroApp = app;
    });
} else {
    // DOM already loaded
    const app = new PomodoroApp();
    app.init();
    window.pomodoroApp = app;
}