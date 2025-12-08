/**
 * Friend Request Modal Handler
 * Add this to friends.html to enable sending friend requests
 */

document.addEventListener('DOMContentLoaded', function () {

    // Add "Send Friend Request" button if it doesn't exist
    const headerDiv = document.querySelector('header .flex.gap-3');
    if (headerDiv && !document.getElementById('btn-add-friend')) {
        const addFriendBtn = document.createElement('button');
        addFriendBtn.id = 'btn-add-friend';
        addFriendBtn.className = 'flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-sm font-medium transition-colors shadow-lg shadow-brand-500/20';
        addFriendBtn.innerHTML = '<i data-lucide="user-plus" class="w-4 h-4"></i> Send Request';
        addFriendBtn.onclick = showAddFriendModal;
        headerDiv.appendChild(addFriendBtn);
        lucide.createIcons();
    }

    function showAddFriendModal() {
        const modalHTML = `
            <div id="add-friend-modal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center opacity-0 transition-opacity duration-300">
                <div class="glass w-full max-w-md p-8 rounded-3xl shadow-2xl mx-4 transform scale-95 transition-transform duration-300 border border-white/10">
                    <div class="text-center mb-6">
                        <div class="w-16 h-16 rounded-2xl bg-brand-500/10 flex items-center justify-center mx-auto mb-4 text-brand-400 ring-1 ring-brand-500/20">
                            <i data-lucide="user-plus" class="w-8 h-8"></i>
                        </div>
                        <h2 class="text-2xl font-display font-bold text-white mb-2">Send Friend Request</h2>
                        <p class="text-gray-400 text-sm">Enter username, email, registration number, or user ID</p>
                    </div>
                    
                    <form id="send-request-form" class="space-y-4">
                        <div class="space-y-2">
                            <label class="text-xs font-mono text-gray-500 uppercase">User Identifier</label>
                            <input type="text" id="friend-user-id" required 
                                class="w-full p-4 rounded-xl bg-black/30 border border-white/10 text-white focus:border-brand-500 focus:outline-none transition-all"
                                placeholder="Enter username, email, registration number, or ID">
                        </div>
                        
                        <div class="flex gap-3">
                            <button type="button" onclick="document.getElementById('add-friend-modal').remove()" 
                                class="flex-1 py-3 rounded-xl border border-white/10 text-gray-400 hover:text-white hover:bg-white/10 transition-all">
                                Cancel
                            </button>
                            <button type="submit" 
                                class="flex-1 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-bold transition-all shadow-lg shadow-brand-500/20">
                                Send Request
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        lucide.createIcons();

        // Animate in
        requestAnimationFrame(() => {
            const modal = document.getElementById('add-friend-modal');
            if (modal) {
                modal.style.opacity = '1';
                modal.querySelector('.glass').style.transform = 'scale(1)';
            }
        });

        // Handle form submission
        const form = document.getElementById('send-request-form');
        form.onsubmit = async function (e) {
            e.preventDefault();

            const identifier = document.getElementById('friend-user-id').value.trim();
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin mx-auto"></i>';
            lucide.createIcons();

            try {
                const token = sessionStorage.getItem('token');
                const response = await fetch('/api/friends/request', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ identifier: identifier })
                });

                const data = await response.json();

                if (response.ok) {
                    // Success
                    if (typeof showToast === 'function') {
                        showToast('Success', 'Friend request sent!', 'success');
                    } else {
                        alert('Friend request sent successfully!');
                    }
                    document.getElementById('add-friend-modal').remove();
                } else {
                    // Error
                    if (typeof showToast === 'function') {
                        showToast('Error', data.error || 'Failed to send request', 'error');
                    } else {
                        alert('Error: ' + (data.error || 'Failed to send request'));
                    }
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }
            } catch (error) {
                console.error('Error sending friend request:', error);
                if (typeof showToast === 'function') {
                    showToast('Error', 'Network error. Please try again.', 'error');
                } else {
                    alert('Network error. Please try again.');
                }
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        };
    }

    // Export to window for onclick handlers
    window.showAddFriendModal = showAddFriendModal;
});
