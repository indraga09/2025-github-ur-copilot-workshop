/**
 * History page functionality for Pomodoro Timer.
 */

class HistoryManager {
    /**
     * Initialize history manager
     */
    constructor() {
        this.sessions = [];
        this.filteredSessions = [];
        this.currentFilter = 'today';
        this.isLoaded = false;
    }
    
    /**
     * Initialize history page
     */
    async init() {
        if (this.isLoaded) {
            return;
        }
        
        this.bindEvents();
        await this.loadData();
        this.updateDisplay();
        
        this.isLoaded = true;
        console.log('History manager initialized');
    }
    
    /**
     * Bind event handlers
     */
    bindEvents() {
        const dateFilter = document.getElementById('dateFilter');
        const exportBtn = document.getElementById('exportBtn');
        
        if (dateFilter) {
            dateFilter.addEventListener('change', (e) => {
                this.currentFilter = e.target.value;
                this.filterSessions();
                this.updateDisplay();
            });
        }
        
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportData());
        }
    }
    
    /**
     * Load sessions and statistics data
     */
    async loadData() {
        try {
            // Load sessions
            const sessionsResponse = await fetch('/api/sessions');\n            if (sessionsResponse.ok) {\n                const sessionsData = await sessionsResponse.json();\n                this.sessions = sessionsData.sessions || [];\n            } else {\n                console.error('Failed to load sessions:', sessionsResponse.statusText);\n                this.sessions = [];\n            }\n            \n            // Load statistics\n            const statsResponse = await fetch('/api/stats');\n            if (statsResponse.ok) {\n                this.stats = await statsResponse.json();\n            } else {\n                console.error('Failed to load stats:', statsResponse.statusText);\n                this.stats = this.createEmptyStats();\n            }\n            \n            this.filterSessions();\n        } catch (error) {\n            console.error('Error loading data:', error);\n            this.sessions = [];\n            this.stats = this.createEmptyStats();\n        }\n    }\n    \n    /**\n     * Filter sessions based on current filter\n     */\n    filterSessions() {\n        const now = new Date();\n        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());\n        \n        switch (this.currentFilter) {\n            case 'today':\n                this.filteredSessions = this.sessions.filter(session => {\n                    const sessionDate = new Date(session.start_time);\n                    const sessionDay = new Date(sessionDate.getFullYear(), sessionDate.getMonth(), sessionDate.getDate());\n                    return sessionDay.getTime() === today.getTime();\n                });\n                break;\n                \n            case 'week':\n                const weekStart = new Date(today);\n                weekStart.setDate(today.getDate() - today.getDay());\n                this.filteredSessions = this.sessions.filter(session => {\n                    const sessionDate = new Date(session.start_time);\n                    return sessionDate >= weekStart && sessionDate <= now;\n                });\n                break;\n                \n            case 'month':\n                const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);\n                this.filteredSessions = this.sessions.filter(session => {\n                    const sessionDate = new Date(session.start_time);\n                    return sessionDate >= monthStart && sessionDate <= now;\n                });\n                break;\n                \n            case 'all':\n            default:\n                this.filteredSessions = [...this.sessions];\n                break;\n        }\n        \n        // Sort by start time (newest first)\n        this.filteredSessions.sort((a, b) => \n            new Date(b.start_time).getTime() - new Date(a.start_time).getTime()\n        );\n    }\n    \n    /**\n     * Update display with current data\n     */\n    updateDisplay() {\n        this.updateStatistics();\n        this.updateSessionsList();\n    }\n    \n    /**\n     * Update statistics dashboard\n     */\n    updateStatistics() {\n        const stats = this.calculateFilteredStats();\n        \n        this.updateStatElement('totalSessions', stats.total_sessions);\n        this.updateStatElement('completedSessions', stats.completed_sessions);\n        this.updateStatElement('totalFocusTime', this.formatFocusTime(stats.total_focus_minutes));\n        this.updateStatElement('completionRate', `${stats.completion_rate}%`);\n    }\n    \n    /**\n     * Update individual stat element\n     */\n    updateStatElement(elementId, value) {\n        const element = document.getElementById(elementId);\n        if (element) {\n            element.textContent = value;\n        }\n    }\n    \n    /**\n     * Update sessions list display\n     */\n    updateSessionsList() {\n        const sessionItems = document.getElementById('sessionItems');\n        const emptyState = document.getElementById('emptyState');\n        \n        if (!sessionItems) {\n            return;\n        }\n        \n        if (this.filteredSessions.length === 0) {\n            sessionItems.innerHTML = '';\n            if (emptyState) {\n                emptyState.style.display = 'block';\n            }\n            return;\n        }\n        \n        if (emptyState) {\n            emptyState.style.display = 'none';\n        }\n        \n        const sessionsHtml = this.filteredSessions.map(session => \n            this.createSessionItem(session)\n        ).join('');\n        \n        sessionItems.innerHTML = sessionsHtml;\n    }\n    \n    /**\n     * Create HTML for session item\n     */\n    createSessionItem(session) {\n        const startTime = new Date(session.start_time);\n        const sessionTypeNames = {\n            'work': 'Work Session',\n            'short_break': 'Short Break',\n            'long_break': 'Long Break'\n        };\n        \n        const statusClass = session.completed ? 'completed' : 'incomplete';\n        const statusIcon = session.completed ? '✅' : '❌';\n        \n        return `\n            <div class=\"session-item ${statusClass}\">\n                <div class=\"session-header\">\n                    <span class=\"session-type-badge session-${session.session_type.replace('_', '-')}\">\n                        ${sessionTypeNames[session.session_type] || 'Unknown'}\n                    </span>\n                    <span class=\"session-status\">${statusIcon}</span>\n                </div>\n                <div class=\"session-details\">\n                    <div class=\"session-time\">\n                        <strong>Started:</strong> ${startTime.toLocaleTimeString()}\n                    </div>\n                    <div class=\"session-duration\">\n                        <strong>Duration:</strong> ${session.duration_minutes} minutes\n                    </div>\n                    ${session.task_description ? `\n                        <div class=\"session-task\">\n                            <strong>Task:</strong> ${this.escapeHtml(session.task_description)}\n                        </div>\n                    ` : ''}\n                    ${session.interruptions > 0 ? `\n                        <div class=\"session-interruptions\">\n                            <strong>Interruptions:</strong> ${session.interruptions}\n                        </div>\n                    ` : ''}\n                </div>\n            </div>\n        `;\n    }\n    \n    /**\n     * Calculate statistics for filtered sessions\n     */\n    calculateFilteredStats() {\n        const total = this.filteredSessions.length;\n        const completed = this.filteredSessions.filter(s => s.completed).length;\n        const workSessions = this.filteredSessions.filter(s => \n            s.session_type === 'work' && s.completed\n        );\n        const focusMinutes = workSessions.reduce((sum, s) => sum + s.duration_minutes, 0);\n        const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;\n        \n        return {\n            total_sessions: total,\n            completed_sessions: completed,\n            total_focus_minutes: focusMinutes,\n            completion_rate: completionRate\n        };\n    }\n    \n    /**\n     * Format focus time for display\n     */\n    formatFocusTime(minutes) {\n        const hours = Math.floor(minutes / 60);\n        const remainingMinutes = minutes % 60;\n        \n        if (hours > 0) {\n            return `${hours}h ${remainingMinutes}m`;\n        } else {\n            return `${remainingMinutes}m`;\n        }\n    }\n    \n    /**\n     * Export data to JSON file\n     */\n    exportData() {\n        const exportData = {\n            sessions: this.filteredSessions,\n            statistics: this.calculateFilteredStats(),\n            exported_at: new Date().toISOString(),\n            filter: this.currentFilter\n        };\n        \n        const dataStr = JSON.stringify(exportData, null, 2);\n        const dataBlob = new Blob([dataStr], { type: 'application/json' });\n        \n        const link = document.createElement('a');\n        link.href = URL.createObjectURL(dataBlob);\n        link.download = `pomodoro-sessions-${this.currentFilter}-${new Date().toISOString().split('T')[0]}.json`;\n        link.click();\n        \n        URL.revokeObjectURL(link.href);\n    }\n    \n    /**\n     * Escape HTML characters\n     */\n    escapeHtml(text) {\n        const div = document.createElement('div');\n        div.textContent = text;\n        return div.innerHTML;\n    }\n    \n    /**\n     * Create empty statistics\n     */\n    createEmptyStats() {\n        return {\n            total_sessions: 0,\n            completed_sessions: 0,\n            total_focus_minutes: 0,\n            completion_rate: 0\n        };\n    }\n    \n    /**\n     * Refresh data from server\n     */\n    async refresh() {\n        await this.loadData();\n        this.updateDisplay();\n    }\n}\n\n// Initialize history manager when DOM is loaded\nif (document.readyState === 'loading') {\n    document.addEventListener('DOMContentLoaded', () => {\n        const historyManager = new HistoryManager();\n        historyManager.init();\n        \n        // Make globally accessible for debugging\n        window.historyManager = historyManager;\n    });\n} else {\n    // DOM already loaded\n    const historyManager = new HistoryManager();\n    historyManager.init();\n    window.historyManager = historyManager;\n}