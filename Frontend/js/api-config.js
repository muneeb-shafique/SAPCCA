// API Base URL Configuration
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : 'https://your-backend-url.com';

console.log('[API CONFIG] Base URL:', API_BASE_URL);

// Override fetch to use base URL
const originalFetch = window.fetch;
window.fetch = function (url, options) {
    // Only modify relative URLs starting with /api
    if (url.startsWith('/api')) {
        url = API_BASE_URL + url;
    }
    console.log('[FETCH]', url);
    return originalFetch(url, options);
};
