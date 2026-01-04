/**
 * SAPCCA Welcome Page Enhancements
 * Password toggle, strength indicator, and improved UX
 */

document.addEventListener('DOMContentLoaded', function () {

    // 1. PASSWORD TOGGLE FUNCTIONALITY (Login)
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

    // 2. PASSWORD TOGGLE FOR SIGNUP
    const signupPasswordInput = document.getElementById('signup-pass');
    if (signupPasswordInput) {
        // Add toggle button
        const signupPasswordGroup = signupPasswordInput.closest('.input-group');
        if (signupPasswordGroup) {
            const toggleBtn = document.createElement('button');
            toggleBtn.type = 'button';
            toggleBtn.className = 'absolute right-4 top-4 text-gray-500 hover:text-white transition-colors z-10';
            toggleBtn.innerHTML = '<i data-lucide="eye" class="w-5 h-5"></i>';
            signupPasswordGroup.appendChild(toggleBtn);
            lucide.createIcons();

            toggleBtn.addEventListener('click', function () {
                const icon = this.querySelector('i');
                if (signupPasswordInput.type === 'password') {
                    signupPasswordInput.type = 'text';
                    icon.setAttribute('data-lucide', 'eye-off');
                } else {
                    signupPasswordInput.type = 'password';
                    icon.setAttribute('data-lucide', 'eye');
                }
                lucide.createIcons();
            });
        }

        // 3. PASSWORD STRENGTH INDICATOR
        const strengthContainer = document.createElement('div');
        strengthContainer.className = 'mt-2 hidden';
        strengthContainer.innerHTML = `
            <div class="flex gap-1 mb-1">
                <div class="strength-bar h-1 flex-1 rounded-full bg-white/10 transition-all"></div>
                <div class="strength-bar h-1 flex-1 rounded-full bg-white/10 transition-all"></div>
                <div class="strength-bar h-1 flex-1 rounded-full bg-white/10 transition-all"></div>
                <div class="strength-bar h-1 flex-1 rounded-full bg-white/10 transition-all"></div>
            </div>
            <p class="text-xs text-gray-500"><span class="strength-text">Enter password</span></p>
        `;
        signupPasswordInput.parentElement.appendChild(strengthContainer);

        signupPasswordInput.addEventListener('input', function () {
            const password = this.value;
            if (password.length === 0) {
                strengthContainer.classList.add('hidden');
                return;
            }

            strengthContainer.classList.remove('hidden');

            let strength = 0;
            const bars = strengthContainer.querySelectorAll('.strength-bar');
            const strengthText = strengthContainer.querySelector('.strength-text');

            // Calculate strength
            if (password.length >= 8) strength++;
            if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
            if (/[0-9]/.test(password)) strength++;
            if (/[^a-zA-Z0-9]/.test(password)) strength++;

            // Update bars
            bars.forEach((bar, index) => {
                if (index < strength) {
                    bar.style.opacity = '1';
                    if (strength === 1) bar.style.background = '#ef4444'; // red
                    else if (strength === 2) bar.style.background = '#f59e0b'; // orange
                    else if (strength === 3) bar.style.background = '#eab308'; // yellow
                    else bar.style.background = '#22c55e'; // green
                } else {
                    bar.style.opacity = '0.1';
                    bar.style.background = '#fff';
                }
            });

            // Update text - FIX: Remove all color classes first, then add new one
            if (strength === 0) {
                strengthText.textContent = 'Too short';
                strengthText.className = 'text-xs strength-text text-gray-400';
            } else if (strength === 1) {
                strengthText.textContent = 'Weak password';
                strengthText.className = 'text-xs strength-text text-red-400';
            } else if (strength === 2) {
                strengthText.textContent = 'Fair password';
                strengthText.className = 'text-xs strength-text text-orange-400';
            } else if (strength === 3) {
                strengthText.textContent = 'Good password';
                strengthText.className = 'text-xs strength-text text-yellow-400';
            } else if (strength === 4) {
                strengthText.textContent = 'Strong password ✓';
                strengthText.className = 'text-xs strength-text text-green-400 font-semibold';
            }
        });
    }

    // 4. OTP PASTE SUPPORT
    const otpInputs = document.querySelectorAll('.otp-box');
    if (otpInputs.length > 0) {
        otpInputs[0].addEventListener('paste', function (e) {
            e.preventDefault();
            const pastedData = e.clipboardData.getData('text').replace(/\D/g, '');
            const digits = pastedData.split('').slice(0, otpInputs.length);

            digits.forEach((digit, index) => {
                if (otpInputs[index]) {
                    otpInputs[index].value = digit;
                }
            });

            // Focus last filled input
            const lastIndex = Math.min(digits.length, otpInputs.length - 1);
            if (otpInputs[lastIndex]) otpInputs[lastIndex].focus();
        });
    }

    // 5. REMEMBER ME FUNCTIONALITY
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

    // 6. ENHANCED FORM VALIDATION WITH SHAKE ANIMATION
    const addShakeAnimation = (element) => {
        element.classList.add('animate-shake');
        element.style.animation = 'shake 0.5s';
        setTimeout(() => {
            element.style.animation = '';
            element.classList.remove('animate-shake');
        }, 500);
    };

    // Add shake keyframes if CSS doesn't have it
    if (!document.querySelector('#shake-keyframes')) {
        const style = document.createElement('style');
        style.id = 'shake-keyframes';
        style.textContent = `
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
                20%, 40%, 60%, 80% { transform: translateX(5px); }
            }
        `;
        document.head.appendChild(style);
    }

    // Apply shake to invalid inputs
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function (e) {
            const requiredInputs = this.querySelectorAll('[required]');
            let hasInvalid = false;

            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    addShakeAnimation(input);
                    hasInvalid = true;
                }
            });

            // Don't prevent default - let the original handlers work
        });
    });

    // 7. FORGOT PASSWORD MODAL
    const forgotPasswordLink = document.querySelector('#view-login a[href="#"]');

    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', function (e) {
            e.preventDefault();
            showForgotPasswordModal();
        });
    }

    function showForgotPasswordModal() {
        // Use SharedUI modal if available
        if (window.SharedUI && window.SharedUI.EnhancedModal) {
            const modal = new window.SharedUI.EnhancedModal({
                title: 'Password Recovery',
                content: 'Password recovery via email verification is currently under development. Please contact your system administrator if you need to reset your password.',
                type: 'info',
                confirmText: 'Close',
                cancelText: '',
                onConfirm: () => { }
            });
            modal.show();
            return;
        }

        // Fallback to custom modal
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

    console.log('✨ Welcome page enhancements loaded');
});
