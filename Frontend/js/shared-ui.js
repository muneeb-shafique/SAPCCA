/**
 * SAPCCA Shared UI Components
 * Reusable UI utilities for enhanced user experience
 */

(function () {
    'use strict';

    // ===== TOAST NOTIFICATION SYSTEM =====
    class ToastManager {
        constructor() {
            this.container = null;
            this.initContainer();
        }

        initContainer() {
            // Check if container already exists
            let existingContainer = document.getElementById('toast-container');
            if (existingContainer) {
                this.container = existingContainer;
                return;
            }

            // Create new container
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none';
            this.container.style.cssText = 'max-width: 400px;';

            // Append to body (will work even if called before DOMContentLoaded)
            if (document.body) {
                document.body.appendChild(this.container);
            } else {
                // If body doesn't exist yet, wait for it
                document.addEventListener('DOMContentLoaded', () => {
                    document.body.appendChild(this.container);
                });
            }
        }

        show(title, message, type = 'info', duration = 4000) {
            // Ensure container exists
            if (!this.container || !this.container.parentElement) {
                this.initContainer();
            }

            // If still no container (edge case), create inline
            if (!this.container) {
                console.error('Toast container could not be initialized');
                return null;
            }

            const toast = document.createElement('div');
            toast.className = 'pointer-events-auto glass-card p-4 rounded-xl shadow-2xl transform translate-x-full transition-all duration-300 flex items-start gap-3 border';

            const colors = {
                success: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', icon: 'text-emerald-400', iconName: 'check-circle' },
                error: { bg: 'bg-red-500/10', border: 'border-red-500/30', icon: 'text-red-400', iconName: 'alert-circle' },
                warning: { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', icon: 'text-yellow-400', iconName: 'alert-triangle' },
                info: { bg: 'bg-brand-500/10', border: 'border-brand-500/30', icon: 'text-brand-400', iconName: 'info' }
            };

            const style = colors[type] || colors.info;
            toast.classList.add(style.bg, style.border);

            toast.innerHTML = `
                <div class="p-2 rounded-lg ${style.bg}">
                    <i data-lucide="${style.iconName}" class="w-5 h-5 ${style.icon}"></i>
                </div>
                <div class="flex-1 min-w-0">
                    <h4 class="text-sm font-bold text-white">${title}</h4>
                    <p class="text-xs text-gray-400 mt-0.5">${message}</p>
                </div>
                <button class="toast-close p-1 text-gray-500 hover:text-white transition-colors">
                    <i data-lucide="x" class="w-4 h-4"></i>
                </button>
            `;

            this.container.appendChild(toast);

            // Initialize Lucide icons
            if (window.lucide) lucide.createIcons();

            // Animate in
            setTimeout(() => toast.classList.remove('translate-x-full'), 10);

            // Close button
            const closeBtn = toast.querySelector('.toast-close');
            const close = () => {
                toast.classList.add('translate-x-full', 'opacity-0');
                setTimeout(() => toast.remove(), 300);
            };
            closeBtn.onclick = close;

            // Auto dismiss
            if (duration > 0) {
                setTimeout(close, duration);
            }

            return toast;
        }
    }

    // ===== SKELETON LOADERS =====
    const SkeletonLoaders = {
        chatMessage() {
            return `
                <div class="flex gap-3 mb-4 animate-pulse">
                    <div class="w-10 h-10 rounded-full bg-white/5"></div>
                    <div class="flex-1 space-y-2">
                        <div class="h-4 bg-white/5 rounded w-1/4"></div>
                        <div class="h-3 bg-white/5 rounded w-3/4"></div>
                    </div>
                </div>
            `;
        },

        chatList() {
            return `
                <div class="p-3 rounded-xl border border-white/5 animate-pulse">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 rounded-full bg-white/5"></div>
                        <div class="flex-1 space-y-2">
                            <div class="h-4 bg-white/5 rounded w-1/2"></div>
                            <div class="h-3 bg-white/5 rounded w-3/4"></div>
                        </div>
                    </div>
                </div>
            `;
        },

        card() {
            return `
                <div class="glass-card p-6 rounded-2xl animate-pulse">
                    <div class="flex items-center gap-3 mb-4">
                        <div class="w-12 h-12 rounded-xl bg-white/5"></div>
                        <div class="flex-1 space-y-2">
                            <div class="h-4 bg-white/5 rounded w-1/3"></div>
                            <div class="h-3 bg-white/5 rounded w-1/2"></div>
                        </div>
                    </div>
                    <div class="space-y-2">
                        <div class="h-3 bg-white/5 rounded"></div>
                        <div class="h-3 bg-white/5 rounded w-5/6"></div>
                    </div>
                </div>
            `;
        },

        statCard() {
            return `
                <div class="glass-card p-6 rounded-2xl animate-pulse">
                    <div class="flex justify-between items-start mb-4">
                        <div class="w-12 h-12 rounded-xl bg-white/5"></div>
                        <div class="h-6 bg-white/5 rounded w-16"></div>
                    </div>
                    <div class="h-8 bg-white/5 rounded w-20 mb-2"></div>
                    <div class="h-3 bg-white/5 rounded w-24"></div>
                </div>
            `;
        },

        render(type, count = 1, container) {
            if (!container) return;

            const loader = this[type];
            if (!loader) return;

            let html = '';
            for (let i = 0; i < count; i++) {
                html += loader();
            }

            container.innerHTML = html;
        }
    };

    // ===== TYPING INDICATOR =====
    class TypingIndicator {
        constructor(userName = 'Someone') {
            this.userName = userName;
        }

        create() {
            const indicator = document.createElement('div');
            indicator.className = 'typing-indicator flex items-center gap-2 p-3 rounded-2xl bg-white/5 max-w-fit animate-fade-in';
            indicator.innerHTML = `
                <div class="flex gap-1">
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                </div>
                <span class="text-xs text-gray-400">${this.userName} is typing...</span>
            `;
            return indicator;
        }
    }

    // ===== ANIMATED COUNTER =====
    function animateCounter(element, start, end, duration = 1000) {
        if (!element) return;

        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 16);
    }

    // ===== PAGE TRANSITIONS =====
    const PageTransitions = {
        fadeIn(element, duration = 300) {
            if (!element) return;
            element.style.opacity = '0';
            element.style.transition = `opacity ${duration}ms ease-in-out`;
            setTimeout(() => element.style.opacity = '1', 10);
        },

        slideUp(element, duration = 300) {
            if (!element) return;
            element.style.transform = 'translateY(20px)';
            element.style.opacity = '0';
            element.style.transition = `all ${duration}ms ease-out`;
            setTimeout(() => {
                element.style.transform = 'translateY(0)';
                element.style.opacity = '1';
            }, 10);
        },

        staggeredFadeIn(elements, delay = 100) {
            if (!elements || !elements.length) return;
            elements.forEach((el, index) => {
                setTimeout(() => this.fadeIn(el), index * delay);
            });
        }
    };

    // ===== ENHANCED MODAL SYSTEM =====
    class EnhancedModal {
        constructor(options = {}) {
            this.title = options.title || 'Modal';
            this.content = options.content || '';
            this.confirmText = options.confirmText || 'Confirm';
            this.cancelText = options.cancelText || 'Cancel';
            this.type = options.type || 'info'; // info, success, warning, error
            this.onConfirm = options.onConfirm || (() => { });
            this.onCancel = options.onCancel || (() => { });
            this.modal = null;
        }

        show() {
            // Create modal overlay
            this.modal = document.createElement('div');
            this.modal.className = 'fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm opacity-0 transition-opacity duration-300';

            const colors = {
                success: { icon: 'check-circle', color: 'emerald' },
                error: { icon: 'alert-circle', color: 'red' },
                warning: { icon: 'alert-triangle', color: 'yellow' },
                info: { icon: 'info', color: 'brand' }
            };
            const style = colors[this.type] || colors.info;

            this.modal.innerHTML = `
                <div class="glass-card w-full max-w-md p-6 rounded-2xl shadow-2xl transform scale-95 transition-all duration-300 m-4">
                    <div class="flex items-center gap-3 mb-4">
                        <div class="p-3 rounded-xl bg-${style.color}-500/20">
                            <i data-lucide="${style.icon}" class="w-6 h-6 text-${style.color}-400"></i>
                        </div>
                        <h3 class="text-lg font-bold text-white">${this.title}</h3>
                    </div>
                    <div class="text-sm text-gray-400 mb-6 leading-relaxed">${this.content}</div>
                    <div class="flex gap-3 justify-end">
                        <button class="modal-cancel px-4 py-2 rounded-lg border border-white/10 text-gray-400 hover:text-white hover:bg-white/5 transition-all text-sm font-medium">
                            ${this.cancelText}
                        </button>
                        <button class="modal-confirm px-6 py-2 rounded-lg bg-${style.color}-600 hover:bg-${style.color}-500 text-white transition-all text-sm font-bold">
                            ${this.confirmText}
                        </button>
                    </div>
                </div>
            `;

            document.body.appendChild(this.modal);
            if (window.lucide) lucide.createIcons();

            // Animate in
            setTimeout(() => {
                this.modal.classList.remove('opacity-0');
                this.modal.querySelector('.glass-card').classList.remove('scale-95');
            }, 10);

            // Event listeners
            this.modal.querySelector('.modal-confirm').onclick = () => {
                this.onConfirm();
                this.hide();
            };

            this.modal.querySelector('.modal-cancel').onclick = () => {
                this.onCancel();
                this.hide();
            };

            // Click outside to close
            this.modal.onclick = (e) => {
                if (e.target === this.modal) this.hide();
            };

            return this;
        }

        hide() {
            if (!this.modal) return;
            this.modal.classList.add('opacity-0');
            this.modal.querySelector('.glass-card').classList.add('scale-95');
            setTimeout(() => this.modal.remove(), 300);
        }
    }

    // ===== LOADING BUTTON STATE =====
    function setButtonLoading(button, loading = true, originalText = null) {
        if (!button) return;

        if (loading) {
            button.dataset.originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Loading...`;
            if (window.lucide) lucide.createIcons();
        } else {
            button.disabled = false;
            button.innerHTML = originalText || button.dataset.originalText || 'Submit';
            if (window.lucide) lucide.createIcons();
        }
    }

    // ===== EXPORT TO WINDOW =====
    window.SharedUI = {
        toast: new ToastManager(),
        skeleton: SkeletonLoaders,
        TypingIndicator,
        animateCounter,
        transitions: PageTransitions,
        EnhancedModal,
        setButtonLoading
    };

    // Make toast available as global function for backward compatibility
    window.showToast = function (title, message, typeOrIsError = false) {
        // Handle backward compatibility: if third param is boolean, convert to type string
        let type;
        if (typeof typeOrIsError === 'boolean') {
            type = typeOrIsError ? 'error' : 'success';
        } else {
            type = typeOrIsError || 'success';
        }

        window.SharedUI.toast.show(title, message, type);
    };

    console.log('✨ SharedUI loaded successfully');

})();
