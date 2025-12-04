/**
 * SAPCCA Welcome Page Enhancements
 * Password toggle, remember me, and forgot password functionality
 */

document.addEventListener('DOMContentLoaded', function () {

    // 1. PASSWORD TOGGLE FUNCTIONALITY
    const togglePasswordBtn = document.querySelector('#view-login .input-group button[type="button"]');
    const loginPasswordInput = document.getElementById('login-pass');

    if (togglePasswordBtn && loginPasswordInput) {
        togglePasswordBtn.addEventListener('click', function () {
            const icon = this.querySelector('i');
            if (loginPasswordInput.type === 'password') {
                loginPasswordInput.type = 'text';
                icon.setAttribute('data-lucide', 'eye-off');
            } else {
                loginPasswordInput.type = 'password';
                icon.setAttribute('data-lucide', 'eye');
            }
            lucide.createIcons();
        });
    }

    // 2. REMEMBER ME FUNCTIONALITY
    const rememberMeCheckbox = document.querySelector('#view-login input[type="checkbox"]');
    const loginEmailInput = document.getElementById('login-email');

    // Load remembered email on page load
    const rememberedEmail = localStorage.getItem('rememberedEmail');
    if (rememberedEmail && loginEmailInput) {
        loginEmailInput.value = rememberedEmail;
        if (rememberMeCheckbox) {
            rememberMeCheckbox.checked = true;
        }
    }

    // Save/clear email on checkbox change
    if (rememberMeCheckbox) {
        rememberMeCheckbox.addEventListener('change', function () {
            if (this.checked && loginEmailInput.value) {
                localStorage.setItem('rememberedEmail', loginEmailInput.value);
            } else {
                localStorage.removeItem('rememberedEmail');
            }
        });
    }

    // Update remember me on login form submit  
    const loginForm = document.querySelector('#view-login form');
    if (loginForm) {
        const originalOnSubmit = loginForm.onsubmit;
        loginForm.onsubmit = function (e) {
            // Save/remove email based on checkbox before login
            if (rememberMeCheckbox && rememberMeCheckbox.checked && loginEmailInput) {
                localStorage.setItem('rememberedEmail', loginEmailInput.value);
            } else {
                localStorage.removeItem('rememberedEmail');
            }

            // Call original handler
            if (originalOnSubmit) {
                return originalOnSubmit.call(this, e);
            }
        };
    }

    // 3. FORGOT PASSWORD MODAL
    const forgotPasswordLink = document.querySelector('#view-login a[href="#"]');

    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', function (e) {
            e.preventDefault();
            showForgotPasswordModal();
        });
    }

    function showForgotPasswordModal() {
        // Create modal HTML
        const modalHTML = `
            <div id="forgot-password-modal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center opacity-0 transition-opacity duration-300">
                <div class="glass-panel w-full max-w-md p-8 rounded-3xl shadow-2xl mx-4 transform scale-95 transition-transform duration-300">
                    <div class="text-center mb-6">
                        <div class="w-16 h-16 rounded-2xl bg-brand-500/10 flex items-center justify-center mx-auto mb-4 text-brand-400 ring-1 ring-brand-500/20">
                            <i data-lucide="key" class="w-8 h-8"></i>
                        </div>
                        <h2 class="text-2xl font-display font-bold text-white mb-2">Password Recovery</h2>
                        <p class="text-gray-400 text-sm">Feature Coming Soon</p>
                    </div>
                    
                    <div class="bg-white/5 border border-white/10 rounded-xl p-4 mb-6">
                        <p class="text-gray-300 text-sm leading-relaxed">
                            Password recovery via email verification is currently under development. 
                            Please contact your system administrator if you need to reset your password.
                        </p>
                    </div>
                    
                    <button onclick="document.getElementById('forgot-password-modal').remove()" class="w-full bg-gradient-to-r from-gray-900 to-black text-white font-bold py-4 rounded-xl hover:scale-[1.01] hover:shadow-up transition-all transform active:scale-[0.98] ring-1 ring-white/10 flex items-center justify-center gap-2">
                        <i data-lucide="x" class="w-5 h-5"></i>
                        Close
                    </button>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        lucide.createIcons();

        // Animate in
        requestAnimationFrame(() => {
            const modal = document.getElementById('forgot-password-modal');
            if (modal) {
                modal.style.opacity = '1';
                modal.querySelector('.glass-panel').style.transform = 'scale(1)';
            }
        });
    }
});
