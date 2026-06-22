/**
 * ============================================================================
 * API SERVICE MODULE - File & Workspace Automation Agent
 * ============================================================================
 * 
 * This module contains ES6 classes that handle all API communication.
 * It implements Object-Oriented Programming (OOP) principles:
 * - Encapsulation: Private methods and properties
 * - Abstraction: Clean public interface for API operations
 * - Inheritance: BaseService as parent class
 * 
 * Author: Carlos
 * Date: 2026
 * ============================================================================
 */


/**
 * ApiConfig class - Manages API configuration and authentication tokens.
 * Uses Singleton pattern to ensure only one instance exists.
 */
class ApiConfig {
    // Base URL for the FastAPI backend
    static BASE_URL = 'http://localhost:8000';
    
    // LocalStorage key for storing the authentication token
    static TOKEN_KEY = 'auth_token';
    
    // LocalStorage key for storing user data
    static USER_KEY = 'user_data';

    /**
     * Get the stored authentication token from localStorage.
     * @returns {string|null} The token or null if not found
     */
    static getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    }

    /**
     * Save the authentication token to localStorage.
     * @param {string} token - The JWT or custom token to store
     */
    static setToken(token) {
        localStorage.setItem(this.TOKEN_KEY, token);
    }

    /**
     * Remove the authentication token from localStorage (logout).
     */
    static clearToken() {
        localStorage.removeItem(this.TOKEN_KEY);
    }

    /**
     * Get stored user data from localStorage.
     * @returns {Object|null} User data object or null
     */
    static getUser() {
        const user = localStorage.getItem(this.USER_KEY);
        return user ? JSON.parse(user) : null;
    }

    /**
     * Save user data to localStorage.
     * @param {Object} userData - User information object
     */
    static setUser(userData) {
        localStorage.setItem(this.USER_KEY, JSON.stringify(userData));
    }

    /**
     * Clear user data from localStorage.
     */
    static clearUser() {
        localStorage.removeItem(this.USER_KEY);
    }

    /**
     * Check if user is authenticated (has a valid token).
     * @returns {boolean} True if token exists
     */
    static isAuthenticated() {
        return !!this.getToken();
    }

    /**
     * Build headers for API requests, including authentication token if available.
     * @param {boolean} includeAuth - Whether to include the auth token
     * @returns {Object} Headers object for fetch requests
     */
    static getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        };

        // Add authentication token if available and requested
        if (includeAuth) {
            const token = this.getToken();
            if (token) {
                headers['X-Token'] = token;
            }
        }

        return headers;
    }
}


/**
 * BaseService - Abstract parent class for all API service classes.
 * Provides common HTTP methods (GET, POST, PUT, DELETE) with error handling.
 */
class BaseService {
    /**
     * Constructor for BaseService.
     * @param {string} endpoint - The API endpoint path (e.g., '/api/users')
     */
    constructor(endpoint) {
        this.endpoint = endpoint;
    }

    /**
     * Perform a GET request to the API.
     * @param {string} [path=''] - Additional path to append to endpoint
     * @param {boolean} [includeAuth=true] - Whether to include auth token
     * @returns {Promise<any>} Response data
     */
    async get(path = '', includeAuth = true) {
        try {
            const response = await fetch(`${ApiConfig.BASE_URL}${this.endpoint}${path}`, {
                method: 'GET',
                headers: ApiConfig.getHeaders(includeAuth),
            });

            // Handle 401 Unauthorized - redirect to login
            if (response.status === 401) {
                console.warn('Authentication failed. Redirecting to login...');
                ApiConfig.clearToken();
                ApiConfig.clearUser();
                window.location.href = 'index.html';
                throw new Error('Session expired. Please login again.');
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`GET ${this.endpoint}${path} failed:`, error);
            throw error;
        }
    }

    /**
     * Perform a POST request to the API.
     * @param {Object} data - Request body data
     * @param {string} [path=''] - Additional path to append
     * @param {boolean} [includeAuth=true] - Whether to include auth token
     * @returns {Promise<any>} Response data
     */
    async post(data, path = '', includeAuth = true) {
        try {
            const response = await fetch(`${ApiConfig.BASE_URL}${this.endpoint}${path}`, {
                method: 'POST',
                headers: ApiConfig.getHeaders(includeAuth),
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`POST ${this.endpoint}${path} failed:`, error);
            throw error;
        }
    }

    /**
     * Perform a PUT request to the API.
     * @param {Object} data - Request body data
     * @param {string} [path=''] - Additional path to append
     * @param {boolean} [includeAuth=true] - Whether to include auth token
     * @returns {Promise<any>} Response data
     */
    async put(data, path = '', includeAuth = true) {
        try {
            const response = await fetch(`${ApiConfig.BASE_URL}${this.endpoint}${path}`, {
                method: 'PUT',
                headers: ApiConfig.getHeaders(includeAuth),
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`PUT ${this.endpoint}${path} failed:`, error);
            throw error;
        }
    }

    /**
     * Perform a DELETE request to the API.
     * @param {string} [path=''] - Additional path to append
     * @param {boolean} [includeAuth=true] - Whether to include auth token
     * @returns {Promise<any>} Response data
     */
    async delete(path = '', includeAuth = true) {
        try {
            const response = await fetch(`${ApiConfig.BASE_URL}${this.endpoint}${path}`, {
                method: 'DELETE',
                headers: ApiConfig.getHeaders(includeAuth),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`DELETE ${this.endpoint}${path} failed:`, error);
            throw error;
        }
    }
}


/**
 * AuthService - Handles user authentication operations.
 * Manages login, registration, logout, and session validation.
 */
class AuthService extends BaseService {
    /**
     * Constructor for AuthService.
     */
    constructor() {
        super('/api/auth');
    }

    /**
     * Register a new user account.
     * @param {Object} userData - User registration data
     * @param {string} userData.username - Unique username
     * @param {string} userData.password - User password
     * @param {string} [userData.full_name] - Optional full name
     * @returns {Promise<Object>} Created user data
     */
    async register(userData) {
        try {
            const response = await this.post(userData, '/register', false);
            console.log('Registration successful:', response);
            return response;
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    }

    /**
     * Authenticate user and store token in localStorage.
     * @param {Object} credentials - Login credentials
     * @param {string} credentials.username - Username
     * @param {string} credentials.password - Password
     * @returns {Promise<Object>} Login response with token and user data
     */
    async login(credentials) {
        try {
            const response = await this.post(credentials, '/login', false);
            
            // Store token and user data in localStorage
            if (response.access_token) {
                ApiConfig.setToken(response.access_token);
                if (response.user) {
                    ApiConfig.setUser(response.user);
                }
            }
            
            console.log('Login successful');
            return response;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    }

    /**
     * Get current authenticated user profile.
     * @returns {Promise<Object>} User profile data
     */
    async getMe() {
        try {
            const response = await this.get('/me');
            ApiConfig.setUser(response);
            return response;
        } catch (error) {
            console.error('Get profile failed:', error);
            throw error;
        }
    }

    /**
     * Update user password.
     * @param {string} newPassword - New password to set
     * @returns {Promise<Object>} Success message
     */
    async updatePassword(newPassword) {
        try {
            const response = await fetch(`${ApiConfig.BASE_URL}${this.endpoint}/update-password`, {
                method: 'PUT',
                headers: {
                    ...ApiConfig.getHeaders(),
                    'X-New-Password': newPassword,
                },
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Update password failed:', error);
            throw error;
        }
    }

    /**
     * Logout user and clear session data.
     * @returns {Promise<Object>} Logout confirmation
     */
    async logout() {
        try {
            const response = await this.delete('/logout');
            
            // Clear local storage
            ApiConfig.clearToken();
            ApiConfig.clearUser();
            
            console.log('Logout successful');
            return response;
        } catch (error) {
            console.error('Logout failed:', error);
            // Still clear local data even if API call fails
            ApiConfig.clearToken();
            ApiConfig.clearUser();
            throw error;
        }
    }
}


/**
 * UserService - Handles user management CRUD operations.
 * Used by admin users to manage workspace members.
 */
class UserService extends BaseService {
    /**
     * Constructor for UserService.
     */
    constructor() {
        super('/api/users');
    }

    /**
     * Get all users from the workspace.
     * @returns {Promise<Array>} List of users
     */
    async getAll() {
        return await this.get('/');
    }

    /**
     * Get a specific user by ID.
     * @param {string} userId - MongoDB user ID
     * @returns {Promise<Object>} User data
     */
    async getById(userId) {
        return await this.get(`/${userId}`);
    }

    /**
     * Create a new user in the workspace.
     * @param {Object} userData - User creation data
     * @param {string} userData.username - Unique username
     * @param {string} userData.email - User email
     * @param {string} userData.full_name - Full name
     * @param {string} userData.password - Password
     * @param {string} [userData.role='viewer'] - User role (admin, operator, viewer)
     * @returns {Promise<Object>} Created user data
     */
    async create(userData) {
        return await this.post(userData, '/');
    }

    /**
     * Update an existing user.
     * @param {string} userId - MongoDB user ID
     * @param {Object} updateData - Fields to update
     * @returns {Promise<Object>} Updated user data
     */
    async update(userId, updateData) {
        return await this.put(updateData, `/${userId}`);
    }

    /**
     * Delete a user from the workspace.
     * @param {string} userId - MongoDB user ID
     * @returns {Promise<Object>} Deletion confirmation
     */
    async delete(userId) {
        return await super.delete(`/${userId}`);
    }
}


/**
 * RuleService - Handles automation rules CRUD operations.
 * Manages file automation rules for the workspace.
 */
class RuleService extends BaseService {
    /**
     * Constructor for RuleService.
     */
    constructor() {
        super('/api/services');
    }

    /**
     * Get all automation rules.
     * @returns {Promise<Array>} List of rules
     */
    async getAll() {
        return await this.get('/');
    }

    /**
     * Get a specific rule by ID.
     * @param {string} ruleId - MongoDB rule ID
     * @returns {Promise<Object>} Rule data
     */
    async getById(ruleId) {
        return await this.get(`/${ruleId}`);
    }

    /**
     * Create a new automation rule.
     * @param {Object} ruleData - Rule creation data
     * @param {string} ruleData.name - Rule name
     * @param {string} ruleData.file_type - Target file type (pdf, image, document, etc.)
     * @param {string} ruleData.action - Action to perform (move, rename, classify, delete)
     * @param {string} ruleData.destination - Destination path
     * @param {string} [ruleData.description] - Optional description
     * @param {boolean} [ruleData.is_active=true] - Whether rule is active
     * @returns {Promise<Object>} Created rule data
     */
    async create(ruleData) {
        return await this.post(ruleData, '/');
    }

    /**
     * Update an existing automation rule.
     * @param {string} ruleId - MongoDB rule ID
     * @param {Object} updateData - Fields to update
     * @returns {Promise<Object>} Updated rule data
     */
    async update(ruleId, updateData) {
        return await this.put(updateData, `/${ruleId}`);
    }

    /**
     * Delete an automation rule.
     * @param {string} ruleId - MongoDB rule ID
     * @returns {Promise<Object>} Deletion confirmation
     */
    async delete(ruleId) {
        return await super.delete(`/${ruleId}`);
    }
}


/**
 * ProductService - Handles workspace files/products CRUD operations.
 * Manages file metadata and organization.
 */
class ProductService extends BaseService {
    /**
     * Constructor for ProductService.
     */
    constructor() {
        super('/api/products');
    }

    /**
     * Get all files/products from the workspace.
     * @returns {Promise<Array>} List of files
     */
    async getAll() {
        return await this.get('/');
    }

    /**
     * Get a specific file by ID.
     * @param {string} productId - MongoDB file ID
     * @returns {Promise<Object>} File data
     */
    async getById(productId) {
        return await this.get(`/${productId}`);
    }

    /**
     * Register a new file in the workspace.
     * @param {Object} productData - File creation data
     * @param {string} productData.name - File name
     * @param {string} productData.category - File category (document, image, spreadsheet, etc.)
     * @param {string} productData.file_path - File path in workspace
     * @param {number} productData.file_size - File size in bytes
     * @param {string} productData.mime_type - MIME type (e.g., application/pdf)
     * @param {string} [productData.description] - Optional description
     * @param {Array<string>} [productData.tags=[]] - Tags for classification
     * @param {boolean} [productData.is_archived=false] - Whether file is archived
     * @param {string} [productData.owner_id] - ID of file owner
     * @returns {Promise<Object>} Created file data
     */
    async create(productData) {
        return await this.post(productData, '/');
    }

    /**
     * Update file metadata.
     * @param {string} productId - MongoDB file ID
     * @param {Object} updateData - Fields to update
     * @returns {Promise<Object>} Updated file data
     */
    async update(productId, updateData) {
        return await this.put(updateData, `/${productId}`);
    }

    /**
     * Delete a file record from the workspace.
     * @param {string} productId - MongoDB file ID
     * @returns {Promise<Object>} Deletion confirmation
     */
    async delete(productId) {
        return await super.delete(`/${productId}`);
    }
}


/**
 * ============================================================================
 * EXPORTS - Make classes available globally
 * ============================================================================
 * Since we're using vanilla JavaScript (no module bundler),
 * we attach classes to the window object for global access.
 */

// Attach all classes to window for global access
window.ApiConfig = ApiConfig;
window.BaseService = BaseService;
window.AuthService = AuthService;
window.UserService = UserService;
window.RuleService = RuleService;
window.ProductService = ProductService;

// Log initialization message
console.log('✅ API Service Module loaded successfully');
console.log('Available services: AuthService, UserService, RuleService, ProductService');