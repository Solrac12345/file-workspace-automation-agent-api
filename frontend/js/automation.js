/**
 * ============================================================================
 * AUTOMATION CONTROLLER - File & Workspace Automation Agent
 * ============================================================================
 * 
 * This script handles the automation rules page functionality:
 * - Loads rules from MongoDB via RuleService
 * - Creates new automation rules
 * - Toggles rule active/inactive status
 * - Deletes rules
 * - Validates user authentication
 * 
 * Author: Carlos
 * Date: 2026
 * ============================================================================
 */

/**
 * AutomationController class - Manages automation rules CRUD operations.
 * Uses OOP principles to encapsulate automation logic.
 */
class AutomationController {
    /**
     * Constructor for AutomationController.
     * Initializes RuleService instance and binds events.
     */
    constructor() {
        // Initialize RuleService for API communication
        this.ruleService = new RuleService();
        
        // Cache DOM elements
        this.elements = {
            rulesList: document.getElementById('rulesList'),
            newRuleForm: document.getElementById('newRuleForm'),
        };

        // Bind event listeners
        this.bindEvents();
    }

    /**
     * Bind event listeners to DOM elements.
     */
    bindEvents() {
        // Form submission handler
        if (this.elements.newRuleForm) {
            this.elements.newRuleForm.addEventListener('submit', (e) => this.handleCreateRule(e));
        }
    }

    /**
     * Initialize automation page - load rules from API.
     */
    async init() {
        console.log('🚀 Initializing automation page...');
        
        // Check authentication first
        if (!ApiConfig.isAuthenticated()) {
            console.warn('User not authenticated, redirecting to login...');
            window.location.href = 'index.html';
            return;
        }

        try {
            // Load rules from MongoDB
            await this.loadRules();
            console.log('✅ Automation page initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize automation page:', error);
            this.showError('Failed to load automation rules');
        }
    }

    /**
     * Load all rules from API and render them.
     */
    async loadRules() {
        try {
            const rules = await this.ruleService.getAll();
            this.renderRules(rules);
        } catch (error) {
            console.error('Failed to load rules:', error);
            this.renderEmptyState();
        }
    }

    /**
     * Render rules list in the UI.
     * @param {Array} rules - Array of rule objects from API
     */
    renderRules(rules) {
        const rulesList = this.elements.rulesList;
        if (!rulesList) return;

        // Clear existing content
        rulesList.innerHTML = '';

        // If no rules, show empty state
        if (!rules || rules.length === 0) {
            this.renderEmptyState();
            return;
        }

        // Render each rule
        rules.forEach(rule => {
            const ruleElement = this.createRuleElement(rule);
            rulesList.appendChild(ruleElement);
        });
    }

    /**
     * Create a rule DOM element.
     * @param {Object} rule - Rule data object
     * @returns {HTMLElement} Rule element
     */
    createRuleElement(rule) {
        const label = document.createElement('label');
        label.className = 'option-row';
        
        const isActive = rule.is_active !== false;
        const statusText = isActive ? 'Activa' : 'Inactiva';
        const statusColor = isActive ? '#4ade80' : '#ef4444';
        
        label.innerHTML = `
            <span class="option-row__text">
                <strong>${this.escapeHtml(rule.name)}</strong>
                <span class="option-row__hint">
                    ${this.escapeHtml(rule.description || 'Sin descripción')} | 
                    Tipo: ${rule.file_type} | 
                    Acción: ${rule.action} | 
                    Destino: ${this.escapeHtml(rule.destination)} |
                    <span style="color: ${statusColor}; font-weight: 600;">${statusText}</span>
                </span>
            </span>
            <div style="display: flex; gap: 0.5rem; align-items: center;">
                <input type="checkbox" ${isActive ? 'checked' : ''} 
                       onchange="window.automationController.toggleRule('${rule.id}', this.checked)">
                <button type="button" class="btn btn--secondary" 
                        style="padding: 0.25rem 0.5rem; font-size: 0.75rem;"
                        onclick="window.automationController.deleteRule('${rule.id}')">
                    🗑️ Eliminar
                </button>
            </div>
        `;
        
        return label;
    }

    /**
     * Render empty state when no rules exist.
     */
    renderEmptyState() {
        const rulesList = this.elements.rulesList;
        if (!rulesList) return;

        rulesList.innerHTML = `
            <div class="option-row" style="opacity: 0.5;">
                <span class="option-row__text">
                    No hay reglas de automatización
                    <span class="option-row__hint">Crea tu primera regla usando el formulario de arriba</span>
                </span>
            </div>
        `;
    }

    /**
     * Handle new rule form submission.
     * @param {Event} event - Form submit event
     */
    async handleCreateRule(event) {
        event.preventDefault();
        
        const formData = {
            name: document.getElementById('ruleName').value.trim(),
            file_type: document.getElementById('ruleFileType').value,
            action: document.getElementById('ruleAction').value,
            destination: document.getElementById('ruleDestination').value.trim(),
            description: document.getElementById('ruleDescription').value.trim(),
            is_active: true
        };

        // Basic validation
        if (!formData.name || !formData.destination) {
            alert('Por favor completa los campos obligatorios');
            return;
        }

        try {
            console.log('📝 Creating new rule:', formData);
            await this.ruleService.create(formData);
            
            // Clear form
            this.elements.newRuleForm.reset();
            
            // Reload rules
            await this.loadRules();
            
            alert('✅ Regla creada exitosamente');
            console.log('✅ Rule created successfully');
        } catch (error) {
            console.error('❌ Failed to create rule:', error);
            alert(`Error al crear la regla: ${error.message}`);
        }
    }

    /**
     * Toggle rule active/inactive status.
     * @param {string} ruleId - Rule ID
     * @param {boolean} isActive - New active status
     */
    async toggleRule(ruleId, isActive) {
        try {
            console.log(`🔄 Toggling rule ${ruleId} to ${isActive ? 'active' : 'inactive'}`);
            
            await this.ruleService.update(ruleId, {
                is_active: isActive
            });
            
            // Reload rules to update UI
            await this.loadRules();
            
            console.log('✅ Rule status updated');
        } catch (error) {
            console.error('❌ Failed to toggle rule:', error);
            alert(`Error al actualizar la regla: ${error.message}`);
            
            // Reload to revert UI state
            await this.loadRules();
        }
    }

    /**
     * Delete a rule.
     * @param {string} ruleId - Rule ID to delete
     */
    async deleteRule(ruleId) {
        if (!confirm('¿Estás seguro de eliminar esta regla?')) {
            return;
        }

        try {
            console.log('🗑️ Deleting rule:', ruleId);
            await this.ruleService.delete(ruleId);
            
            // Reload rules
            await this.loadRules();
            
            console.log('✅ Rule deleted successfully');
        } catch (error) {
            console.error('❌ Failed to delete rule:', error);
            alert(`Error al eliminar la regla: ${error.message}`);
        }
    }

    /**
     * Show error message in the UI.
     * @param {string} message - Error message
     */
    showError(message) {
        const rulesList = this.elements.rulesList;
        if (rulesList) {
            rulesList.innerHTML = `
                <div class="option-row" style="opacity: 0.5; color: #ef4444;">
                    <span class="option-row__text">
                        Error: ${message}
                        <span class="option-row__hint">Intenta recargar la página</span>
                    </span>
                </div>
            `;
        }
    }

    /**
     * Escape HTML to prevent XSS attacks.
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

/**
 * Global function to refresh rules (called from button).
 */
function refreshRules() {
    if (window.automationController) {
        window.automationController.loadRules();
    }
}

/**
 * Initialize automation page when DOM is ready.
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('📦 Automation script loaded');
    
    // Create and initialize automation controller
    const controller = new AutomationController();
    window.automationController = controller; // Make it globally accessible
    controller.init();
});