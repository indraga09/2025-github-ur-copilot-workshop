/**
 * Timer functionality for Pomodoro Timer application.
 */

class PomodoroTimer {
    /**
     * Initialize Pomodoro Timer
     * @param {Object} config - Timer configuration
     */
    constructor(config = {}) {
        this.config = {
            workMinutes: config.workMinutes || 25,
            shortBreakMinutes: config.shortBreakMinutes || 5,
            longBreakMinutes: config.longBreakMinutes || 15
        };
        
        this.currentSession = {
            type: 'work',
            timeRemaining: this.config.workMinutes * 60, // seconds
            isRunning: false,
            cycleCount: 1
        };
        
        this.interval = null;
        this.onTickCallback = null;
        this.onCompleteCallback = null;
    }
    
    /**
     * Start the timer
     */
    start() {
        if (!this.currentSession.isRunning) {
            this.currentSession.isRunning = true;
            this.interval = setInterval(() => this.tick(), 1000);
        }
    }
    
    /**
     * Pause the timer
     */
    pause() {
        if (this.currentSession.isRunning) {
            this.currentSession.isRunning = false;
            if (this.interval) {
                clearInterval(this.interval);
                this.interval = null;
            }
        }
    }
    
    /**
     * Reset the timer to start of current session
     */
    reset() {
        this.pause();
        const duration = calculateSessionDuration(this.currentSession.type, this.config);
        this.currentSession.timeRemaining = duration * 60;
    }
    
    /**
     * Timer tick function called every second
     * @private
     */
    tick() {
        if (this.currentSession.timeRemaining > 0) {
            this.currentSession.timeRemaining--;
            
            if (this.onTickCallback) {
                this.onTickCallback(this.currentSession);
            }
        } else {
            this.onComplete();
        }
    }
    
    /**
     * Handle timer completion
     * @private
     */
    onComplete() {
        this.pause();
        
        if (this.onCompleteCallback) {
            this.onCompleteCallback(this.currentSession);
        }
        
        // Auto-transition to next session type
        this.moveToNextSession();
    }
    
    /**
     * Move to next session type based on Pomodoro rules
     */
    moveToNextSession() {
        const nextType = calculateNextSessionType(
            this.currentSession.type, 
            this.currentSession.cycleCount
        );
        
        this.currentSession.type = nextType;
        
        if (nextType === 'work') {
            this.currentSession.cycleCount++;
        }
        
        const duration = calculateSessionDuration(nextType, this.config);
        this.currentSession.timeRemaining = duration * 60;
    }
    
    /**
     * Get time remaining in seconds
     * @returns {number} Seconds remaining
     */
    getTimeRemaining() {
        return this.currentSession.timeRemaining;
    }
    
    /**
     * Get formatted time string (MM:SS)
     * @returns {string} Formatted time
     */
    getFormattedTime() {
        return formatTime(this.currentSession.timeRemaining);
    }
    
    /**
     * Check if timer is running
     * @returns {boolean} True if running
     */
    isRunning() {
        return this.currentSession.isRunning;
    }
    
    /**
     * Get current session information
     * @returns {Object} Current session data
     */
    getCurrentSession() {
        return { ...this.currentSession };
    }
    
    /**
     * Set callback for timer tick
     * @param {Function} callback - Function to call on each tick
     */
    onTick(callback) {
        this.onTickCallback = callback;
    }
    
    /**
     * Set callback for timer completion
     * @param {Function} callback - Function to call on completion
     */
    onSessionComplete(callback) {
        this.onCompleteCallback = callback;
    }
    
    /**
     * Manually set session type
     * @param {string} type - Session type (work, short_break, long_break)
     */
    setSessionType(type) {
        if (validateSessionType(type)) {
            this.pause();
            this.currentSession.type = type;
            const duration = calculateSessionDuration(type, this.config);
            this.currentSession.timeRemaining = duration * 60;
        }
    }
}

/**
 * Format seconds into MM:SS string
 * @param {number} seconds - Seconds to format
 * @returns {string} Formatted time string
 */
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

/**
 * Validate duration in minutes
 * @param {number} minutes - Duration to validate
 * @returns {boolean} True if valid
 */
function validateDuration(minutes) {
    return typeof minutes === 'number' && minutes > 0 && minutes <= 120;
}

/**
 * Create timer configuration object
 * @param {number} workMin - Work session minutes
 * @param {number} shortBreak - Short break minutes
 * @param {number} longBreak - Long break minutes
 * @returns {Object} Timer configuration
 */
function createTimerConfig(workMin, shortBreak, longBreak) {
    return {
        workMinutes: workMin,
        shortBreakMinutes: shortBreak,
        longBreakMinutes: longBreak
    };
}

/**
 * Calculate next session type based on Pomodoro rules
 * @param {string} currentType - Current session type
 * @param {number} cycleCount - Current cycle count
 * @returns {string} Next session type
 */
function calculateNextSessionType(currentType, cycleCount) {
    if (currentType === 'work') {
        // After 4 work sessions, take long break
        return (cycleCount % 4 === 0) ? 'long_break' : 'short_break';
    } else {
        // After any break, return to work
        return 'work';
    }
}

/**
 * Calculate session duration based on type and config
 * @param {string} sessionType - Type of session
 * @param {Object} config - Timer configuration
 * @returns {number} Duration in minutes
 */
function calculateSessionDuration(sessionType, config) {
    const durations = {
        'work': config.workMinutes,
        'short_break': config.shortBreakMinutes,
        'long_break': config.longBreakMinutes
    };
    return durations[sessionType] || config.workMinutes;
}

/**
 * Validate session type
 * @param {string} type - Session type to validate
 * @returns {boolean} True if valid
 */
function validateSessionType(type) {
    const validTypes = ['work', 'short_break', 'long_break'];
    return validTypes.includes(type);
}