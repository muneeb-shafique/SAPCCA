/**
 * SAPCCA Authentication Utility
 * Handles token and user data management with multi-tab support
 * TOKEN: localStorage (shared - for easy global logout)
 * USER DATA: sessionStorage (tab-specific - prevents conflicts)
 */

const Auth = {
    // Get authentication token
    getToken() {
        return localStorage.getItem('token');
    },

    // Set authentication token
    setToken(token) {
        localStorage.setItem('token', token);
    },

    // Remove authentication token
    removeToken() {
        localStorage.removeItem('token');
    },

    // Get stored user data (from sessionStorage for tab isolation)
    getUserData() {
        const userStr = sessionStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    },

    // Set user data (in sessionStorage for tab isolation)
    setUserData(user) {
        sessionStorage.setItem('user', JSON.stringify(user));
    },

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.getToken();
    },

    // Logout user
    logout() {
        this.removeToken();
        sessionStorage.clear();
        localStorage.removeItem('rememberedEmail');
        window.location.href = '/welcome.html';
    },

    // Check auth and redirect if not authenticated
    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/welcome.html';
            return false;
        }
        return true;
    }
};

// Export for use in HTML files
if (typeof window !== 'undefined') {
    window.Auth = Auth;
}
