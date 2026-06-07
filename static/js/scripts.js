/*!
* Start Bootstrap - Clean Blog v6.0.9 (https://startbootstrap.com/theme/clean-blog)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-clean-blog/blob/master/LICENSE)
*/
window.addEventListener('DOMContentLoaded', () => {
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav.clientHeight;
    window.addEventListener('scroll', function() {
        const currentTop = document.body.getBoundingClientRect().top * -1;
        if ( currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else {
                console.log(123);
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            mainNav.classList.remove(['is-visible']);
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop;
    });

    // ===== Auth Forms - Password Toggle & Strength Indicator =====
    // Initialize password toggles
    function initPasswordToggles() {
        const toggleButtons = document.querySelectorAll('.password-toggle');
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const wrapper = this.closest('.password-wrapper');
                if (!wrapper) return;
                
                const input = wrapper.querySelector('.form-control-custom');
                
                if (input) {
                    if (input.type === 'password') {
                        input.type = 'text';
                    } else {
                        input.type = 'password';
                    }
                }
            });
        });
    }

    // Initialize password strength indicator
    function initPasswordStrength() {
        const passwordField = document.querySelector('input[name="password"]');
        if (passwordField) {
            passwordField.addEventListener('input', function() {
                const strength = calculatePasswordStrength(this.value);
                updateStrengthMeter(strength);
            });
        }
    }

    // Calculate password strength (0-4)
    function calculatePasswordStrength(password) {
        let strength = 0;
        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;
        return Math.min(strength, 4);
    }

    // Update password strength meter
    function updateStrengthMeter(strength) {
        const fill = document.querySelector('.strength-meter-fill');
        const text = document.querySelector('.strength-text span');
        
        if (!fill || !text) return;
        
        const strengths = ['--', 'Weak', 'Fair', 'Good', 'Strong'];
        const colors = ['#ddd', '#dc3545', '#fd7e14', '#ffc107', '#198754'];
        
        fill.style.width = ((strength / 4) * 100) + '%';
        fill.style.backgroundColor = colors[strength];
        text.textContent = strengths[strength];
    }

    // Initialize auth form features
    initPasswordToggles();
    initPasswordStrength();
});
