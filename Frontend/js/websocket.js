/**
 * WebSocket Real-Time Messaging for SAPCCA
 * Connects to SocketIO backend for real-time message delivery
 */

(function () {
    'use strict';

    // Wait for SocketIO library to load
    if (typeof io === 'undefined') {
        console.error('SocketIO library not loaded!');
        return;
    }

    // Connect to WebSocket server
    const socket = io();
    let currentRoom = null;
    let currentUserId = null;

    // Get user ID from sessionStorage
    function getUserId() {
        const userData = JSON.parse(sessionStorage.getItem('user') || '{}');
        return userData.id;
    }

    // Generate room ID for 1-on-1 chat
    function getRoomId(userId1, userId2) {
        const sorted = [userId1, userId2].sort((a, b) => a - b);
        return `chat_${sorted[0]}_${sorted[1]}`;
    }

    // Socket event handlers
    socket.on('connect', () => {
        console.log('✅ Socket connected');
        currentUserId = getUserId();
    });

    socket.on('disconnect', () => {
        console.log('❌ Socket disconnected');
    });

    socket.on('new_message', (data) => {
        console.log('📨 New message received:', data);

        // Only display if we're in the correct chat
        if (window.activeChat && window.activeChat.id == data.from || data.to == currentUserId) {
            displayIncomingMessage(data);
        }
    });

    // Display incoming message in real-time
    function displayIncomingMessage(msgData) {
        const container = document.getElementById('messages-container');
        if (!container) return;

        const isMe = msgData.from == currentUserId;
        const bubble = document.createElement('div');
        bubble.className = `flex w-full ${isMe ? 'justify-end' : 'justify-start'}`;

        bubble.innerHTML = `
            <div class="max-w-[75%]">
                <div class="p-3 rounded-2xl text-sm ${isMe ? 'bg-brand-600 text-white' : 'bg-white/5 text-gray-200'}">
                    ${msgData.text}
                </div>
                <div class="text-[10px] text-gray-500 mt-1 ${isMe ? 'text-right' : 'text-left'}">
                    ${new Date(msgData.time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                </div>
            </div>
        `;

        container.appendChild(bubble);
        container.scrollTop = container.scrollHeight;
    }

    // Join chat room when opening a chat
    window.joinChatRoom = function (friendId) {
        const userId = getUserId();
        if (!userId || !friendId) return;

        const roomId = getRoomId(userId, friendId);

        // Leave previous room if any
        if (currentRoom) {
            socket.emit('leave_room', { room: currentRoom });
        }

        // Join new room
        socket.emit('join_room', { room: roomId });
        currentRoom = roomId;
        console.log(`🔗 Joined room: ${roomId}`);
    };

    // Send message via WebSocket
    window.sendSocketMessage = function (receiverId, text) {
        const senderId = getUserId();
        if (!senderId || !receiverId || !text) return;

        const roomId = getRoomId(senderId, receiverId);

        socket.emit('send_message', {
            room: roomId,
            sender: senderId,
            receiver: receiverId,
            text: text
        });

        console.log(`📤 Message sent via socket to room: ${roomId}`);
    };

    console.log('🚀 WebSocket integration loaded');
})();
