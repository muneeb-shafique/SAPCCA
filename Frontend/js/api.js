/**
 * SAPCCA API Utility
 * Centralized API request handler with authentication
 */

const API = {
    // Base URL for API requests
    BASE_URL: '',  // Empty string means same origin (localhost:5000)

    /**
     * Make an authenticated API request
     * @param {string} endpoint - API endpoint (e.g., '/api/profile')
     * @param {object} options - Fetch options
     * @returns {Promise<object>} - Response data
     */
    async request(endpoint, options = {}) {
        const token = Auth.getToken();

        // Setup headers
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Add authorization header if token exists
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        // Merge options
        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(this.BASE_URL + endpoint, config);
            const data = await response.json();

            // Handle unauthorized (token expired/invalid)
            if (response.status === 401) {
                Auth.logout();
                throw new Error('Session expired. Please login again.');
            }

            // Handle other errors
            if (!response.ok) {
                throw new Error(data.error || `Request failed with status ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    },

    // Convenience methods for common HTTP verbs
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    async post(endpoint, body) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(body)
        });
    },

    async put(endpoint, body) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(body)
        });
    },

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
};

// Export for use in HTML files
if (typeof window !== 'undefined') {
    window.API = API;
}
