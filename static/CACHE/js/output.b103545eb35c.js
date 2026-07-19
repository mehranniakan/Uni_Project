class ToastManager {
    constructor() {
        this.container = document.getElementById('toastContainer');
        if (!this.container) {
            this.createContainer();
        }
        this.autoCloseTime = 5000;
        this.setupEventListeners();
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        this.container.id = 'toastContainer';
        document.body.appendChild(this.container);
    }

    show(message, type = 'info', title = '', duration = this.autoCloseTime) {
        const toast = this.createToast(message, type, title);
        this.container.appendChild(toast);
        if (duration > 0) {
            this.autoRemove(toast, duration);
        }
        this.playSound(type);
        if (type === 'error' && 'vibrate' in navigator) {
            navigator.vibrate(200);
        }
        return toast;
    }

    createToast(message, type, title) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-times-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        const defaultTitles = {success: 'موفقیت', error: 'خطا', warning: 'هشدار', info: 'اطلاعات'};
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        const toastId = 'toast-' + Date.now();
        toast.id = toastId;
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="fas ${icons[type] || icons.info}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-title">${title || defaultTitles[type] || 'اعلان'}</div>
                <div class="toast-message">${this.escapeHtml(message)}</div>
            </div>
            <button class="toast-close" onclick="toastManager.close('${toastId}')">
                <i class="fas fa-times"></i>
            </button>
            <div class="toast-progress"></div>
        `;
        const progressBar = toast.querySelector('.toast-progress');
        if (progressBar) {
            progressBar.style.animationDuration = this.autoCloseTime + 'ms';
        }
        return toast;
    }

    close(toast) {
        const toastElement = typeof toast === 'string' ? document.getElementById(toast) : toast;
        if (!toastElement) return;
        toastElement.classList.add('hiding');
        setTimeout(() => {
            if (toastElement.parentElement) {
                toastElement.remove();
            }
        }, 400);
    }

    closeAll() {
        const toasts = this.container.querySelectorAll('.toast');
        toasts.forEach(toast => this.close(toast));
    }

    autoRemove(toast, duration) {
        setTimeout(() => {
            if (toast.parentElement) {
                this.close(toast);
            }
        }, duration);
    }

    playSound(type) {
        if (!window.toastSounds) {
            window.toastSounds = {
                success: new Audio('https://assets.mixkit.co/sfx/preview/mixkit-correct-answer-tone-2870.mp3'),
                error: new Audio('https://assets.mixkit.co/sfx/preview/mixkit-wrong-answer-fail-notification-946.mp3'),
                warning: new Audio('https://assets.mixkit.co/sfx/preview/mixkit-warning-alarm-1000.mp3'),
                info: new Audio('https://assets.mixkit.co/sfx/preview/mixkit-message-pop-alert-2354.mp3')
            };
        }
        const sound = window.toastSounds[type];
        if (sound) {
            sound.currentTime = 0;
            sound.play().catch(() => {
            });
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    setupEventListeners() {
        this.container.addEventListener('dblclick', (e) => {
            if (e.target === this.container) {
                this.closeAll();
            }
        });
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.toast') && !e.target.closest('.toast-container')) {
                const toasts = this.container.querySelectorAll('.toast');
                toasts.forEach(toast => {
                    if (!toast.contains(e.target)) {
                        this.close(toast);
                    }
                });
            }
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAll();
            }
        });
    }

    success(message, title = 'موفقیت') {
        return this.show(message, 'success', title);
    }

    error(message, title = 'خطا') {
        return this.show(message, 'error', title);
    }

    warning(message, title = 'هشدار') {
        return this.show(message, 'warning', title);
    }

    info(message, title = 'اطلاعات') {
        return this.show(message, 'info', title);
    }
}

const toastManager = new ToastManager();
window.showToast = (message, type = 'info', title = '', duration = 5000) => {
    return toastManager.show(message, type, title, duration);
};
window.showSuccess = (message, title = 'موفقیت') => {
    return toastManager.success(message, title);
};
window.showError = (message, title = 'خطا') => {
    return toastManager.error(message, title);
};
window.showWarning = (message, title = 'هشدار') => {
    return toastManager.warning(message, title);
};
window.showInfo = (message, title = 'اطلاعات') => {
    return toastManager.info(message, title);
};
window.closeAllToasts = () => {
    toastManager.closeAll();
};
;document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
    }
    initLoginAnimations();
    setupInputFocus();
});

async function handleLoginSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    if (!validateLoginForm(form)) {
        return;
    }
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="loader"></span> در حال ورود...';
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');
    try {
        const formData = new FormData(form);
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        });
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                showSuccess('ورود موفقیت‌آمیز بود! در حال هدایت...');
                setTimeout(() => {
                    window.location.href = data.redirect_url || '/';
                }, 1500);
            } else {
                showError(data.error || 'خطا در ورود');
                highlightErrors(form, data.errors || {});
            }
        } else {
            showError('خطا در ارتباط با سرور');
        }
    } catch (error) {
        showError('خطا در ارتباط با سرور');
        console.error('Login error:', error);
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
    }
}

function validateLoginForm(form) {
    const username = form.querySelector('input[name="username"]');
    const password = form.querySelector('input[name="password"]');
    let isValid = true;
    clearFormErrors(form);
    if (!username.value.trim()) {
        showFieldError(username, 'نام کاربری الزامی است');
        isValid = false;
    }
    if (!password.value) {
        showFieldError(password, 'رمز عبور الزامی است');
        isValid = false;
    } else if (password.value.length < 6) {
        showFieldError(password, 'رمز عبور باید حداقل 6 کاراکتر باشد');
        isValid = false;
    }
    return isValid;
}

function showFieldError(input, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.cssText = `
        color: #ef4444;
        font-size: 12px;
        margin-top: 5px;
        text-align: right;
    `;
    errorDiv.textContent = message;
    input.parentElement.appendChild(errorDiv);
    input.classList.add('error');
    input.style.animation = 'shake 0.5s';
    setTimeout(() => {
        input.style.animation = '';
    }, 500);
}

function clearFormErrors(form) {
    const errors = form.querySelectorAll('.field-error');
    errors.forEach(error => error.remove());
    const inputs = form.querySelectorAll('input');
    inputs.forEach(input => input.classList.remove('error'));
}

function highlightErrors(form, errors) {
    clearFormErrors(form);
    for (const field in errors) {
        const input = form.querySelector(`[name="${field}"]`);
        if (input) {
            showFieldError(input, errors[field][0]);
        }
    }
}

function initLoginAnimations() {
    const boxes = document.querySelectorAll('.square-box');
    boxes.forEach((box, index) => {
        box.style.animationDelay = `${index * 5}s`;
    });
    const loginCard = document.querySelector('.login-card');
    if (loginCard) {
        loginCard.style.opacity = '0';
        loginCard.style.transform = 'translateY(20px)';
        setTimeout(() => {
            loginCard.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            loginCard.style.opacity = '1';
            loginCard.style.transform = 'translateY(0)';
        }, 300);
    }
    window.addEventListener('mousemove', handleParallax);
}

function handleParallax(e) {
    const x = (e.clientX / window.innerWidth - 0.5) * 20;
    const y = (e.clientY / window.innerHeight - 0.5) * 20;
    const boxes = document.querySelectorAll('.square-box');
    boxes.forEach((box, index) => {
        const factor = index === 0 ? 0.5 : 0.3;
        box.style.transform = `rotate(45deg) translate(${x * factor}px, ${y * factor}px)`;
    });
}

function setupInputFocus() {
    const inputs = document.querySelectorAll('.form-input');
    inputs.forEach(input => {
        input.addEventListener('focus', function () {
            this.parentElement.classList.add('focused');
        });
        input.addEventListener('blur', function () {
            this.parentElement.classList.remove('focused');
        });
        input.addEventListener('input', function () {
            if (this.classList.contains('error')) {
                this.classList.remove('error');
                const errorDiv = this.parentElement.querySelector('.field-error');
                if (errorDiv) errorDiv.remove();
            }
        });
    });
}

function showSuccess(message) {
    return toastManager.success(message, 'موفقیت');
}

function showError(message) {
    return toastManager.error(message, 'خطا');
}

function setupDjangoMessages() {
}