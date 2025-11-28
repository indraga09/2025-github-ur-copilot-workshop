/**
 * Local storage management for Pomodoro Timer application.
 */

class TimerStorage {
    /**
     * Initialize storage manager
     * @param {string} storageKey - Key for localStorage
     */
    constructor(storageKey = 'pomodoroTimer') {
        this.storageKey = storageKey;
        this.settingsKey = `${storageKey}_settings`;
        this.sessionKey = `${storageKey}_session`;
    }
    
    /**
     * Save current session state
     * @param {Object} sessionData - Session data to save
     * @returns {boolean} True if saved successfully
     */
    saveCurrentSession(sessionData) {
        try {
            if (!this.isStorageAvailable()) {
                return false;
            }
            
            const sanitizedData = sanitizeStorageInput(sessionData);
            if (!validateStorageData(sanitizedData)) {
                return false;
            }
            
            localStorage.setItem(this.sessionKey, JSON.stringify(sanitizedData));
            return true;
        } catch (error) {
            console.error('Failed to save session:', error);
            return false;
        }
    }
    
    /**
     * Load current session state
     * @returns {Object|null} Session data or null if not found
     */
    loadCurrentSession() {
        try {
            if (!this.isStorageAvailable()) {
                return null;
            }
            
            const data = localStorage.getItem(this.sessionKey);
            if (!data) {
                return null;
            }
            
            const parsed = JSON.parse(data);
            return validateStorageData(parsed) ? parsed : null;
        } catch (error) {
            console.error('Failed to load session:', error);
            return null;
        }
    }
    
    /**
     * Save user settings
     * @param {Object} settings - Settings to save
     * @returns {boolean} True if saved successfully
     */
    saveSettings(settings) {
        try {
            if (!this.isStorageAvailable()) {
                return false;
            }
            
            const sanitizedSettings = sanitizeStorageInput(settings);
            localStorage.setItem(this.settingsKey, JSON.stringify(sanitizedSettings));
            return true;
        } catch (error) {
            console.error('Failed to save settings:', error);
            return false;
        }
    }
    
    /**
     * Load user settings
     * @returns {Object} Settings object or defaults
     */
    loadSettings() {
        try {
            if (!this.isStorageAvailable()) {
                return createDefaultSettings();
            }
            
            const data = localStorage.getItem(this.settingsKey);
            if (!data) {
                return createDefaultSettings();
            }
            
            const parsed = JSON.parse(data);
            // Migrate old data if needed
            return migrateStorageVersion(parsed);
        } catch (error) {
            console.error('Failed to load settings:', error);
            return createDefaultSettings();
        }
    }
    
    /**
     * Clear current session
     * @returns {boolean} True if cleared successfully
     */
    clearSession() {
        try {
            if (!this.isStorageAvailable()) {
                return false;
            }
            
            localStorage.removeItem(this.sessionKey);
            return true;
        } catch (error) {
            console.error('Failed to clear session:', error);
            return false;
        }
    }
    
    /**
     * Check if localStorage is available
     * @returns {boolean} True if storage is available
     */
    isStorageAvailable() {
        try {
            const test = '__storage_test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (error) {
            return false;
        }
    }
}

/**
 * Validate storage data
 * @param {Object} data - Data to validate
 * @returns {boolean} True if valid
 */
function validateStorageData(data) {
    if (!data || typeof data !== 'object') {
        return false;
    }
    
    // Check required fields for session data
    if (data.type && !['work', 'short_break', 'long_break'].includes(data.type)) {
        return false;
    }
    
    if (data.timeRemaining && (typeof data.timeRemaining !== 'number' || data.timeRemaining < 0)) {
        return false;
    }
    
    if (data.cycleCount && (typeof data.cycleCount !== 'number' || data.cycleCount < 1)) {
        return false;
    }
    
    return true;
}

/**
 * Migrate storage data from old version
 * @param {Object} oldData - Old storage data
 * @returns {Object} Migrated data
 */
function migrateStorageVersion(oldData) {
    const defaults = createDefaultSettings();
    
    // Merge old data with new defaults
    return {
        ...defaults,
        ...oldData,
        version: '1.0.0' // Update version
    };
}

/**
 * Create default settings
 * @returns {Object} Default settings object
 */
function createDefaultSettings() {
    return {
        workDuration: 25,
        shortBreakDuration: 5,
        longBreakDuration: 15,
        soundEnabled: true,
        notificationsEnabled: true,
        autoStartBreaks: false,
        autoStartWork: false,
        volume: 0.5,
        theme: 'light',
        version: '1.0.0'
    };
}

/**
 * Sanitize input data to prevent XSS
 * @param {Object} input - Input data to sanitize
 * @returns {Object} Sanitized data
 */
function sanitizeStorageInput(input) {
    if (!input || typeof input !== 'object') {
        return {};
    }
    
    const sanitized = {};
    
    for (const [key, value] of Object.entries(input)) {
        if (typeof value === 'string') {
            // Basic string sanitization
            sanitized[key] = value.replace(/[<>"'&]/g, '');
        } else if (typeof value === 'number' || typeof value === 'boolean') {
            sanitized[key] = value;
        } else if (Array.isArray(value)) {
            sanitized[key] = value.filter(item => typeof item === 'string' || typeof item === 'number');
        }
    }
    
    return sanitized;
}