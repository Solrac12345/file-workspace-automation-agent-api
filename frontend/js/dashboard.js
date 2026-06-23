/**
 * ============================================================================
 * DASHBOARD CONTROLLER - File & Workspace Automation Agent
 * ============================================================================
 * 
 * This script handles the dashboard page functionality:
 * - Loads user data from authentication
 * - Fetches files/products from the API
 * - Updates the UI with real data from MongoDB
 * - Handles logout functionality
 * 
 * Author: Carlos
 * Date: 2026
 * ============================================================================
 */

/**
 * DashboardController class - Manages dashboard data and UI updates.
 * Uses OOP principles to encapsulate dashboard logic.
 */
class DashboardController {
    /**
     * Constructor for DashboardController.
     * Initializes service instances for API communication.
     */
    constructor() {
        // Initialize API service instances
        this.authService = new AuthService();
        this.productService = new ProductService();
        this.userService = new UserService();
        this.ruleService = new RuleService();
        
        // Cache DOM elements
        this.elements = {
            userBadge: document.getElementById('userBadge'),
            welcomeMessage: document.getElementById('welcomeMessage'),
            fileCount: document.getElementById('fileCount'),
            automationStatus: document.getElementById('automationStatus'),
            fileList: document.getElementById('fileList'),
            logoutBtn: document.getElementById('logoutBtn'),
        };

        // Bind event listeners
        this.bindEvents();
    }

    /**
     * Bind event listeners to DOM elements.
     */
    bindEvents() {
        // Logout button handler
        if (this.elements.logoutBtn) {
            this.elements.logoutBtn.addEventListener('click', () => this.handleLogout());
        }
    }

    /**
     * Initialize dashboard - load all data from API.
     */
    async init() {
        console.log('🚀 Initializing dashboard...');
        
        // Check authentication first
        if (!ApiConfig.isAuthenticated()) {
            console.warn('User not authenticated, redirecting to login...');
            window.location.href = 'index.html';
            return;
        }

        try {
            // Load user profile
            await this.loadUserProfile();
            
            // Load files/products
            await this.loadFiles();
            
            // Update automation status
            this.updateAutomationStatus();
            
            console.log('✅ Dashboard initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize dashboard:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    /**
     * Load user profile and update UI.
     */
    async loadUserProfile() {
        try {
            // Try to get user from localStorage first (faster)
            const cachedUser = ApiConfig.getUser();
            
            if (cachedUser) {
                this.updateUserInfo(cachedUser);
                return;
            }

            // If not cached, fetch from API
            const user = await this.authService.getMe();
            this.updateUserInfo(user);
        } catch (error) {
            console.error('Failed to load user profile:', error);
            // Use fallback data
            this.updateUserInfo({ username: 'Usuario', full_name: 'Usuario del Workspace' });
        }
    }

    /**
     * Update UI with user information.
     * @param {Object} user - User data object
     */
    updateUserInfo(user) {
        const displayName = user.full_name || user.username || 'Usuario';
        const username = user.username || 'usuario';
        
        // Update badge with username
        if (this.elements.userBadge) {
            this.elements.userBadge.textContent = username;
        }
        
        // Update welcome message
        if (this.elements.welcomeMessage) {
            this.elements.welcomeMessage.textContent = `Bienvenido, ${displayName}!`;
        }
    }

    /**
     * Load files/products from API and update the file list.
     */
    async loadFiles() {
        try {
            const files = await this.productService.getAll();
            this.renderFileList(files);
            this.updateFileCount(files.length);
        } catch (error) {
            console.error('Failed to load files:', error);
            this.renderEmptyState();
        }
    }

    /**
     * Render file list in the UI.
     * @param {Array} files - Array of file objects from API
     */
    renderFileList(files) {
        const fileList = this.elements.fileList;
        if (!fileList) return;

        // Clear existing content
        fileList.innerHTML = '';

        // If no files, show empty state
        if (!files || files.length === 0) {
            this.renderEmptyState();
            return;
        }

        // Render each file
        files.forEach(file => {
            const li = document.createElement('li');
            li.className = 'file-item';
            
            // Determine icon based on file type/category
            const icon = this.getFileIcon(file.category || file.mime_type);
            const extension = this.getFileExtension(file.name || file.mime_type);
            
            li.innerHTML = `
                <span class="file-item__icon" aria-hidden="true">${icon}</span>
                <span class="file-item__name">${this.escapeHtml(file.name || 'Sin nombre')}</span>
                <span class="file-item__meta">${extension.toUpperCase()}</span>
            `;
            
            fileList.appendChild(li);
        });
    }

    /**
     * Render empty state when no files are available.
     */
    renderEmptyState() {
        const fileList = this.elements.fileList;
        if (!fileList) return;

        fileList.innerHTML = `
            <li class="file-item" style="opacity: 0.5;">
                <span class="file-item__icon" aria-hidden="true">📭</span>
                <span class="file-item__name">No hay archivos registrados</span>
                <span class="file-item__meta">—</span>
            </li>
        `;
    }

    /**
     * Update file count in the stats card.
     * @param {number} count - Number of files
     */
    updateFileCount(count) {
        if (this.elements.fileCount) {
            this.elements.fileCount.textContent = count;
        }
    }

    /**
     * Update automation status based on active rules.
     */
    async updateAutomationStatus() {
        try {
            const rules = await this.ruleService.getAll();
            const activeRules = rules.filter(rule => rule.is_active !== false);
            
            if (this.elements.automationStatus) {
                if (activeRules.length > 0) {
                    this.elements.automationStatus.textContent = `${activeRules.length} activa${activeRules.length > 1 ? 's' : ''}`;
                    this.elements.automationStatus.className = 'stat-card__value stat-card__value--status';
                } else {
                    this.elements.automationStatus.textContent = 'Sin reglas';
                    this.elements.automationStatus.className = 'stat-card__value';
                }
            }
        } catch (error) {
            console.error('Failed to load rules:', error);
            if (this.elements.automationStatus) {
                this.elements.automationStatus.textContent = 'Error';
            }
        }
    }

    /**
     * Get appropriate icon for file type.
     * @param {string} type - File category or MIME type
     * @returns {string} Emoji icon
     */
    getFileIcon(type) {
        if (!type) return '📄';
        
        const typeLower = type.toLowerCase();
        
        if (typeLower.includes('pdf') || typeLower === 'document') return '📄';
        if (typeLower.includes('image') || typeLower.includes('png') || typeLower.includes('jpg')) return '️';
        if (typeLower.includes('spreadsheet') || typeLower.includes('excel') || typeLower.includes('xlsx')) return '';
        if (typeLower.includes('presentation') || typeLower.includes('ppt')) return '️';
        if (typeLower.includes('archive') || typeLower.includes('zip')) return '📦';
        
        return '';
    }

    /**
     * Get file extension from name or MIME type.
     * @param {string} nameOrMime - File name or MIME type
     * @returns {string} File extension
     */
    getFileExtension(nameOrMime) {
        if (!nameOrMime) return 'file';
        
        // If it's a MIME type
        if (nameOrMime.includes('/')) {
            const parts = nameOrMime.split('/');
            return parts[1] || 'file';
        }
        
        // If it's a filename, extract extension
        const parts = nameOrMime.split('.');
        return parts.length > 1 ? parts[parts.length - 1] : 'file';
    }

    /**
     * Escape HTML to prevent XSS attacks.
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Show error message in the UI.
     * @param {string} message - Error message to display
     */
    showError(message) {
        if (this.elements.welcomeMessage) {
            this.elements.welcomeMessage.textContent = `Error: ${message}`;
            this.elements.welcomeMessage.style.color = '#ef4444';
        }
    }

    /**
     * Handle logout button click.
     */
    async handleLogout() {
        try {
            console.log('🚪 Logging out...');
            await this.authService.logout();
            console.log('✅ Logout successful, redirecting to login...');
            window.location.href = 'index.html';
        } catch (error) {
            console.error('❌ Logout failed:', error);
            // Still redirect even if API call fails
            ApiConfig.clearToken();
            ApiConfig.clearUser();
            window.location.href = 'index.html';
        }
    }
}

/**
 * Navigation function for automation button.
 * Called from inline onclick handler.
 */
function goAutomation() {
    console.log(' Navigating to automation page...');
    window.location.href = 'automation.html';
}

/**
 * Initialize dashboard when DOM is ready.
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('📦 Dashboard script loaded');
    
    // Create and initialize dashboard controller
    const dashboard = new DashboardController();
    dashboard.init();
});