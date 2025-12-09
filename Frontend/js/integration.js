/**
 * SAPCCA Complete Frontend-Backend Integration Script
 * WITH PROPER MULTI-TAB ISOLATION
 * Uses sessionStorage for user data (tab-specific)
 */

(function () {
    'use strict';

    // ===== AUTHENTICATION CHECK =====
    function checkAuth() {
        const token = sessionStorage.getItem('token');
        const currentPage = window.location.pathname;

        // Redirect to welcome if not authenticated
        if (!token && !currentPage.includes('welcome.html')) {
            window.location.href = '/welcome.html';
            return false;
        }

        return true;
    }

    // Run auth check immediately
    if (!checkAuth()) return;

    // ===== GLOBAL USER DATA (tab-specific via sessionStorage) =====
    let currentUser = null;
    let friendsList = [];
    let activeChat = null;

    // ===== API HELPERS =====
    const API_BASE = '';

    async function apiRequest(endpoint, options = {}) {
        const token = sessionStorage.getItem('token');
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(API_BASE + endpoint, {
                ...options,
                headers
            });

            const data = await response.json();

            if (response.status === 401) {
                logout();
                throw new Error('Session expired');
            }

            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            showToast('Error', error.message, 'error');
            throw error;
        }
    }

    // ===== UTILITY FUNCTIONS =====
    function showToast(title, message, type = 'success') {
        if (typeof window.showToast === 'function') {
            window.showToast(title, message, type === 'error');
            return;
        }
        console.log(`[${type.toUpperCase()}] ${title}: ${message}`);
    }

    function getAvatar(userId) {
        return `https://robohash.org/${userId}?set=set4&bgset=bg2`;
    }

    function logout() {
        sessionStorage.removeItem('token');
        sessionStorage.clear(); // Clear all session data
        window.location.href = '/welcome.html';
    }

    // ===== LOAD USER PROFILE =====
    async function loadUserProfile() {
        try {
            const profile = await apiRequest('/api/profile');
            currentUser = profile;

            // Store in sessionStorage (tab-specific)
            sessionStorage.setItem('user', JSON.stringify({
                id: profile.id,
                name: profile.name,
                email: profile.email
            }));

            updateUserUI();
            return profile;
        } catch (error) {
            console.error('Failed to load profile:', error);
        }
    }

    function updateUserUI() {
        if (!currentUser) return;

        const userData = JSON.parse(sessionStorage.getItem('user') || '{}');
        const userId = userData.id || currentUser.id || 'Loading...';
        const userName = currentUser.name || userData.name || 'User';

        // Update all name elements
        const nameElements = document.querySelectorAll('#global-user-name, .user-name');
        nameElements.forEach(el => {
            if (el) el.textContent = userName;
        });

        // Update all email elements
        const emailElements = document.querySelectorAll('.user-email');
        emailElements.forEach(el => {
            if (el) el.textContent = currentUser.email || '';
        });

        // Update all avatar elements
        const avatarElements = document.querySelectorAll('#global-user-avatar, #sidebar-avatar, .user-avatar');
        avatarElements.forEach(el => {
            if (el) el.src = currentUser.avatar || getAvatar(currentUser.email);
        });

        // Update all User ID displays (format: "ID: 123")
        const userIdElements = document.querySelectorAll('.user-id-display');
        userIdElements.forEach(el => {
            if (el) el.textContent = `ID: ${userId}`;
        });
    }

    // ===== CHAT PAGE INTEGRATION =====
    async function initChatPage() {
        if (!window.location.pathname.includes('chat.html')) return;
        await loadFriends();
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.onclick = (e) => {
                e.preventDefault();
                logout();
            };
        }
    }

    async function loadFriends() {
        try {
            const friends = await apiRequest('/api/friends/list');
            friendsList = friends;

            const chatListContainer = document.getElementById('chat-list-container');
            if (!chatListContainer) return;

            chatListContainer.innerHTML = '';

            if (friends.length === 0) {
                chatListContainer.innerHTML = `
                    <div class="flex flex-col items-center justify-center p-8 text-center">
                        <div class="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-4">
                            <i data-lucide="users" class="w-10 h-10 text-gray-600"></i>
                        </div>
                        <h3 class="text-white font-bold mb-2">No Contacts Yet</h3>
                        <p class="text-gray-400 text-sm">Add friends to start chatting</p>
                    </div>
                `;
                lucide.createIcons();
                return;
            }

            friends.forEach(friend => {
                const friendEl = document.createElement('div');
                friendEl.className = 'p-3 rounded-xl cursor-pointer transition-all border border-transparent hover:bg-white/5 flex items-center gap-3 group';
                friendEl.innerHTML = `
                    <div class="relative flex-shrink-0">
                        <img src="${getAvatar(friend.id)}" class="w-12 h-12 rounded-full bg-black object-cover ring-2 ring-white/5">
                        <div class="absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-[#111317] bg-gray-500"></div>
                    </div>
                    <div class="flex-1 min-w-0">
                        <h4 class="text-sm font-bold text-white truncate">${friend.display_name}</h4>
                        <p class="text-xs text-gray-400 truncate">Click to open chat</p>
                    </div>
                `;

                friendEl.onclick = () => openChat(friend);
                chatListContainer.appendChild(friendEl);
            });

            lucide.createIcons();
        } catch (error) {
            console.error('Failed to load friends:', error);
        }
    }

    async function openChat(friend) {
        activeChat = friend;
        document.getElementById('chat-title').textContent = friend.display_name;
        document.getElementById('chat-id-display').textContent = friend.id;
        document.getElementById('chat-avatar').src = getAvatar(friend.id);
        document.getElementById('welcome-container').classList.add('hidden');
        document.getElementById('active-chat-interface').classList.remove('hidden');
        document.getElementById('active-chat-interface').classList.add('flex');
        await loadChatHistory(friend.id);
    }

    async function loadChatHistory(friendId) {
        try {
            const response = await apiRequest(`/api/messages/chat/${friendId}`);
            const messages = response.messages || [];

            const container = document.getElementById('messages-container');
            if (!container) return;

            container.innerHTML = '';

            if (messages.length === 0) {
                container.innerHTML = `
                    <div class="flex flex-col items-center justify-center h-full text-center">
                        <i data-lucide="message-circle" class="w-16 h-16 text-gray-600 mb-4"></i>
                        <p class="text-gray-400">No messages yet. Start the conversation!</p>
                    </div>
                `;
                lucide.createIcons();
                return;
            }

            const userData = JSON.parse(sessionStorage.getItem('user') || '{}');
            const currentUserId = userData.id;

            messages.forEach(msg => {
                const isMe = msg.from === currentUserId;
                const bubble = document.createElement('div');
                bubble.className = `flex w-full ${isMe ? 'justify-end' : 'justify-start'}`;

                bubble.innerHTML = `
                    <div class="max-w-[75%]">
                        <div class="p-3 rounded-2xl text-sm ${isMe ? 'bg-brand-600 text-white' : 'bg-white/5 text-gray-200'}">
                            ${msg.text}
                        </div>
                        <div class="text-[10px] text-gray-500 mt-1 ${isMe ? 'text-right' : 'text-left'}">
                            ${new Date(msg.time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                        </div>
                    </div>
                `;

                container.appendChild(bubble);
            });

            container.scrollTop = container.scrollHeight;
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    }

    function setupSendMessage() {
        const form = document.getElementById('send-message-form');
        const input = document.getElementById('new-message-input');

        if (!form || !input) return;

        form.onsubmit = async (e) => {
            e.preventDefault();

            const text = input.value.trim();
            if (!text || !activeChat) return;

            try {
                await apiRequest('/api/messages/send', {
                    method: 'POST',
                    body: JSON.stringify({
                        receiver_id: activeChat.id,
                        message: text
                    })
                });

                input.value = '';
                await loadChatHistory(activeChat.id);
            } catch (error) {
                console.error('Failed to send message:', error);
            }
        };
    }

    // ===== FRIENDS PAGE INTEGRATION =====
    async function initFriendsPage() {
        if (!window.location.pathname.includes('friends.html')) return;
        await loadPendingRequests();
        setupFriendRequestHandlers();
        setupFriendTabs();
    }

    function setupFriendTabs() {
        const tabs = document.querySelectorAll('[data-tab]');
        tabs.forEach(tab => {
            tab.addEventListener('click', async (e) => {
                e.preventDefault();
                const tabName = tab.dataset.tab;

                // Update active tab styling
                tabs.forEach(t => {
                    t.className = 'text-gray-500 hover:text-white border-b-2 border-transparent hover:border-white/20 pb-2 px-2 font-medium text-sm tracking-wide transition-all';
                });
                tab.className = 'text-white border-b-2 border-brand-500 pb-2 px-2 font-medium text-sm tracking-wide';

                // Load appropriate content
                if (tabName === 'pending') {
                    await loadPendingRequests();
                } else if (tabName === 'outgoing') {
                    await loadOutgoingRequests();
                } else if (tabName === 'ignored') {
                    await loadIgnoredRequests();
                }
            });
        });
    }

    function showEmptyState(message) {
        const container = document.getElementById('request-list');
        if (!container) return;

        container.innerHTML = `
            <div class="glass-card p-12 rounded-2xl text-center">
                <i data-lucide="inbox" class="w-16 h-16 text-gray-600 mx-auto mb-4"></i>
                <h3 class="text-xl font-bold text-white mb-2">${message}</h3>
                <p class="text-gray-400">Nothing to show here.</p>
            </div>
        `;
        lucide.createIcons();
    }

    async function loadPendingRequests() {
        try {
            const response = await apiRequest('/api/friends/pending');
            const requests = response.requests || [];

            const container = document.getElementById('request-list');
            if (!container) return;

            container.innerHTML = '';

            if (requests.length === 0) {
                container.innerHTML = `
                    <div class="glass-card p-12 rounded-2xl text-center">
                        <i data-lucide="check-circle" class="w-16 h-16 text-brand-400 mx-auto mb-4"></i>
                        <h3 class="text-xl font-bold text-white mb-2">All Caught Up!</h3>
                        <p class="text-gray-400">No pending friend requests at the moment.</p>
                    </div>
                `;
                lucide.createIcons();
                return;
            }

            requests.forEach(req => {
                const card = document.createElement('div');
                card.className = 'glass-card p-5 rounded-xl flex flex-col md:flex-row items-center gap-6 group hover:bg-white/5 transition-colors border-l-4 border-l-brand-500';
                card.id = `req-${req.request_id}`;
                card.innerHTML = `
                    <div class="relative flex-shrink-0">
                        <div class="w-16 h-16 rounded-full p-0.5 bg-gradient-to-tr from-brand-400 to-indigo-500">
                            <img src="${getAvatar(req.sender_id)}" class="w-full h-full rounded-full bg-black object-cover">
                        </div>
                    </div>
                    
                    <div class="flex-1 text-center md:text-left">
                        <h3 class="text-lg font-bold text-white font-display">${req.sender_name}</h3>
                        <p class="text-sm text-gray-400">ID: ${req.sender_id}</p>
                    </div>
                    
                    <div class="flex items-center gap-3 w-full md:w-auto">
                        <button onclick="window.rejectFriendRequest('${req.request_id}')" class="flex-1 md:flex-none py-2 px-4 rounded-lg border border-white/10 text-gray-400 hover:text-white hover:bg-white/10 transition-all text-sm font-medium">
                            Ignore
                        </button>
                        <button onclick="window.acceptFriendRequest('${req.request_id}')" class="flex-1 md:flex-none py-2 px-6 rounded-lg bg-brand-600 hover:bg-brand-500 text-white transition-all text-sm font-bold flex items-center justify-center gap-2">
                            <i data-lucide="check" class="w-4 h-4"></i>
                            Accept
                        </button>
                    </div>
                `;

                container.appendChild(card);
            });

            lucide.createIcons();
        } catch (error) {
            console.error('Failed to load pending requests:', error);
        }
    }

    async function loadOutgoingRequests() {
        try {
            const response = await apiRequest('/api/friends/outgoing');
            const requests = response.requests || [];

            const container = document.getElementById('request-list');
            if (!container) return;

            container.innerHTML = '';

            if (requests.length === 0) {
                container.innerHTML = `
                    <div class="glass-card p-12 rounded-2xl text-center">
                        <i data-lucide="send" class="w-16 h-16 text-gray-600 mx-auto mb-4"></i>
                        <h3 class="text-xl font-bold text-white mb-2">No Outgoing Requests</h3>
                        <p class="text-gray-400">You haven't sent any friend requests yet.</p>
                    </div>
                `;
                lucide.createIcons();
                return;
            }

            requests.forEach(req => {
                const card = document.createElement('div');
                card.className = 'glass-card p-5 rounded-xl flex flex-col md:flex-row items-center gap-6 group hover:bg-white/5 transition-colors border-l-4 border-l-yellow-500';
                card.id = `req-${req.request_id}`;
                card.innerHTML = `
                    <div class="relative flex-shrink-0">
                        <div class="w-16 h-16 rounded-full p-0.5 bg-gradient-to-tr from-yellow-400 to-orange-500">
                            <img src="${getAvatar(req.receiver_id)}" class="w-full h-full rounded-full bg-black object-cover">
                        </div>
                    </div>
                    
                    <div class="flex-1 text-center md:text-left">
                        <h3 class="text-lg font-bold text-white font-display">${req.receiver_name}</h3>
                        <p class="text-sm text-gray-400">ID: ${req.receiver_id}</p>
                        <p class="text-xs text-gray-500 mt-1"><i data-lucide="clock" class="w-3 h-3 inline"></i> Pending since ${new Date(req.timestamp).toLocaleDateString()}</p>
                    </div>
                    
                    <div class="flex items-center gap-3 w-full md:w-auto">
                        <button onclick="window.cancelFriendRequest('${req.request_id}')" class="flex-1 md:flex-none py-2 px-4 rounded-lg border border-red-500/20 text-red-400 hover:bg-red-500/10 transition-all text-sm font-medium">
                            Cancel Request
                        </button>
                    </div>
                `;

                container.appendChild(card);
            });

            lucide.createIcons();
        } catch (error) {
            console.error('Failed to load outgoing requests:', error);
        }
    }

    async function loadIgnoredRequests() {
        try {
            const response = await apiRequest('/api/friends/ignored');
            const requests = response.requests || [];

            const container = document.getElementById('request-list');
            if (!container) return;

            container.innerHTML = '';

            if (requests.length === 0) {
                container.innerHTML = `
                    <div class="glass-card p-12 rounded-2xl text-center">
                        <i data-lucide="user-x" class="w-16 h-16 text-gray-600 mx-auto mb-4"></i>
                        <h3 class="text-xl font-bold text-white mb-2">No Ignored Requests</h3>
                        <p class="text-gray-400">You haven't ignored any friend requests.</p>
                    </div>
                `;
                lucide.createIcons();
                return;
            }

            requests.forEach(req => {
                const card = document.createElement('div');
                card.className = 'glass-card p-5 rounded-xl flex flex-col md:flex-row items-center gap-6 group hover:bg-white/5 transition-colors border-l-4 border-l-red-500';
                card.id = `req-${req.request_id}`;
                card.innerHTML = `
                    <div class="relative flex-shrink-0">
                        <div class="w-16 h-16 rounded-full p-0.5 bg-gradient-to-tr from-red-400 to-gray-500">
                            <img src="${getAvatar(req.sender_id)}" class="w-full h-full rounded-full bg-black object-cover opacity-60">
                        </div>
                    </div>
                    
                    <div class="flex-1 text-center md:text-left">
                        <h3 class="text-lg font-bold text-gray-300 font-display">${req.sender_name}</h3>
                        <p class="text-sm text-gray-500">ID: ${req.sender_id}</p>
                        <p class="text-xs text-gray-600 mt-1"><i data-lucide="x-circle" class="w-3 h-3 inline"></i> Rejected on ${new Date(req.timestamp).toLocaleDateString()}</p>
                    </div>
                    
                    <div class="flex items-center gap-3 w-full md:w-auto">
                        <button onclick="window.deleteIgnoredRequest('${req.request_id}')" class="flex-1 md:flex-none py-2 px-4 rounded-lg border border-red-500/20 text-red-400 hover:bg-red-500/10 transition-all text-sm font-medium">
                            Delete
                        </button>
                    </div>
                `;

                container.appendChild(card);
            });

            lucide.createIcons();
        } catch (error) {
            console.error('Failed to load ignored requests:', error);
        }
    }

    function setupFriendRequestHandlers() {
        window.acceptFriendRequest = async (requestId) => {
            try {
                await apiRequest('/api/friends/accept', {
                    method: 'POST',
                    body: JSON.stringify({ request_id: parseInt(requestId) })
                });

                showToast('Success', 'Friend request accepted!');

                const card = document.getElementById(`req-${requestId}`);
                if (card) card.remove();

                setTimeout(() => loadPendingRequests(), 500);
            } catch (error) {
                console.error('Failed to accept request:', error);
            }
        };

        window.rejectFriendRequest = async (requestId) => {
            try {
                await apiRequest('/api/friends/reject', {
                    method: 'POST',
                    body: JSON.stringify({ request_id: parseInt(requestId) })
                });

                showToast('Info', 'Request ignored');

                const card = document.getElementById(`req-${requestId}`);
                if (card) card.remove();

                setTimeout(() => loadPendingRequests(), 500);
            } catch (error) {
                console.error('Failed to reject request:', error);
            }
        };

        window.cancelFriendRequest = async (requestId) => {
            try {
                await apiRequest('/api/friends/cancel', {
                    method: 'POST',
                    body: JSON.stringify({ request_id: parseInt(requestId) })
                });

                showToast('Info', 'Request cancelled');

                const card = document.getElementById(`req-${requestId}`);
                if (card) card.remove();

                setTimeout(() => loadOutgoingRequests(), 500);
            } catch (error) {
                console.error('Failed to cancel request:', error);
            }
        };

        window.deleteIgnoredRequest = async (requestId) => {
            try {
                // Use the delete endpoint to permanently remove the ignored request
                await apiRequest('/api/friends/delete', {
                    method: 'POST',
                    body: JSON.stringify({ request_id: parseInt(requestId) })
                });

                showToast('Info', 'Ignored request deleted');

                const card = document.getElementById(`req-${requestId}`);
                if (card) card.remove();

                setTimeout(() => loadIgnoredRequests(), 500);
            } catch (error) {
                console.error('Failed to delete ignored request:', error);
            }
        };
    }

    // ===== SETTINGS PAGE INTEGRATION =====
    async function initSettingsPage() {
        if (!window.location.pathname.includes('settings.html')) return;
        await loadProfileSettings();
        setupProfileUpdate();
    }

    async function loadProfileSettings() {
        try {
            const profile = await apiRequest('/api/profile');

            const userData = JSON.parse(sessionStorage.getItem('user') || '{}');
            const userId = userData.id || profile.id || 'Loading...';

            const nameInput = document.getElementById('input-username');
            const emailInput = document.getElementById('input-email');
            const regNumberInput = document.getElementById('input-reg-number');
            const avatarPreview = document.getElementById('avatar-preview');
            const userIdInput = document.getElementById('input-clearance-id');

            if (nameInput) nameInput.value = profile.name || '';
            if (emailInput) emailInput.value = profile.email || '';
            if (regNumberInput) regNumberInput.value = profile.registration_number || 'N/A';
            if (avatarPreview) avatarPreview.src = profile.avatar || getAvatar(profile.email);
            if (userIdInput) {
                userIdInput.value = `ID: ${userId}`;
                userIdInput.classList.remove('opacity-50');
                userIdInput.classList.add('text-brand-400', 'font-bold');
            }

            // Also update any other ID displays on the page
            const userIdDisplays = document.querySelectorAll('.user-id-display');
            userIdDisplays.forEach(el => {
                if (el) el.textContent = userId;
            });
        } catch (error) {
            console.error('Failed to load profile settings:', error);
        }
    }

    // ===== CHAT PAGE - ADD FRIEND BUTTON =====
    function setupChatAddFriendButton() {
        const addContactBtn = document.getElementById('add-contact-btn');
        if (addContactBtn && window.location.pathname.includes('chat.html')) {
            addContactBtn.onclick = () => {
                if (typeof window.showAddFriendModal === 'function') {
                    window.showAddFriendModal();
                } else {
                    // Fallback: redirect to friends page
                    window.location.href = '/friends.html';
                }
            };
        }
    }

    function setupProfileUpdate() {
        const saveBtn = document.getElementById('btn-save');

        if (!saveBtn) return;

        saveBtn.onclick = async () => {
            const nameInput = document.getElementById('input-username');

            if (!nameInput) return;

            try {
                await apiRequest('/api/profile/update', {
                    method: 'POST',
                    body: JSON.stringify({
                        name: nameInput.value
                    })
                });

                showToast('Success', 'Profile updated successfully');
                await loadUserProfile();
            } catch (error) {
                console.error('Failed to update profile:', error);
            }
        };
    }

    // ===== INITIALIZE ON PAGE LOAD =====
    window.addEventListener('DOMContentLoaded', async function () {
        await loadUserProfile();
        await initChatPage();
        await initFriendsPage();
        await initSettingsPage();
        setupSendMessage();
        setupChatAddFriendButton();

        const userData = JSON.parse(sessionStorage.getItem('user') || '{}');
        console.log(`SAPCCA Integration loaded for User ID: ${userData.id || 'Unknown'}`);
    });

})();
