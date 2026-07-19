// login.js - مدیریت صفحه ورود

document.addEventListener('DOMContentLoaded', function () {
    // فرم ورود
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
    }

    // انیمیشن‌های ورود
    initLoginAnimations();

    // مدیریت focus روی inputها
    setupInputFocus();
});

/**
 * مدیریت ارسال فرم
 */
async function handleLoginSubmit(e) {
    e.preventDefault();

    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');

    // اعتبارسنجی سمت کلاینت
    if (!validateLoginForm(form)) {
        return;
    }

    // نمایش حالت loading
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="loader"></span> در حال ورود...';
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');

    try {
        const formData = new FormData(form);

        // ارسال درخواست
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (response.ok) {
            const data = await response.json();

            if (data.success) {
                // موفقیت‌آمیز
                showSuccess('ورود موفقیت‌آمیز بود! در حال هدایت...');
                setTimeout(() => {
                    window.location.href = data.redirect_url || '/';
                }, 1500);
            } else {
                // خطا از سمت سرور
                showError(data.error || 'خطا در ورود');
                highlightErrors(form, data.errors || {});
            }
        } else {
            // خطای HTTP
            showError('خطا در ارتباط با سرور');
        }
    } catch (error) {
        // خطای شبکه
        showError('خطا در ارتباط با سرور');
        console.error('Login error:', error);
    } finally {
        // بازگرداندن دکمه به حالت عادی
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
    }
}

/**
 * اعتبارسنجی فرم در سمت کلاینت
 */
function validateLoginForm(form) {
    const username = form.querySelector('input[name="username"]');
    const password = form.querySelector('input[name="password"]');
    let isValid = true;

    // پاک کردن خطاهای قبلی
    clearFormErrors(form);

    // اعتبارسنجی نام کاربری
    if (!username.value.trim()) {
        showFieldError(username, 'نام کاربری الزامی است');
        isValid = false;
    }

    // اعتبارسنجی رمز عبور
    if (!password.value) {
        showFieldError(password, 'رمز عبور الزامی است');
        isValid = false;
    } else if (password.value.length < 6) {
        showFieldError(password, 'رمز عبور باید حداقل 6 کاراکتر باشد');
        isValid = false;
    }

    return isValid;
}

/**
 * نمایش خطا برای فیلد خاص
 */
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

    // انیمیشن shake
    input.style.animation = 'shake 0.5s';
    setTimeout(() => {
        input.style.animation = '';
    }, 500);
}

/**
 * پاک کردن خطاهای فرم
 */
function clearFormErrors(form) {
    const errors = form.querySelectorAll('.field-error');
    errors.forEach(error => error.remove());

    const inputs = form.querySelectorAll('input');
    inputs.forEach(input => input.classList.remove('error'));
}

/**
 * هایلایت کردن خطاها
 */
function highlightErrors(form, errors) {
    clearFormErrors(form);

    for (const field in errors) {
        const input = form.querySelector(`[name="${field}"]`);
        if (input) {
            showFieldError(input, errors[field][0]);
        }
    }
}

/**
 * انیمیشن‌های صفحه ورود
 */
function initLoginAnimations() {
    // انیمیشن المان‌های پس‌زمینه
    const boxes = document.querySelectorAll('.square-box');
    boxes.forEach((box, index) => {
        box.style.animationDelay = `${index * 5}s`;
    });

    // انیمیشن کارت ورود
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

    // افکت parallax
    window.addEventListener('mousemove', handleParallax);
}

/**
 * افکت Parallax با حرکت موس
 */
function handleParallax(e) {
    const x = (e.clientX / window.innerWidth - 0.5) * 20;
    const y = (e.clientY / window.innerHeight - 0.5) * 20;

    const boxes = document.querySelectorAll('.square-box');
    boxes.forEach((box, index) => {
        const factor = index === 0 ? 0.5 : 0.3;
        box.style.transform = `rotate(45deg) translate(${x * factor}px, ${y * factor}px)`;
    });
}

/**
 * تنظیم focus روی inputها
 */
function setupInputFocus() {
    const inputs = document.querySelectorAll('.form-input');

    inputs.forEach(input => {
        // افکت focus
        input.addEventListener('focus', function () {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function () {
            this.parentElement.classList.remove('focused');
        });

        // تایپ live validation
        input.addEventListener('input', function () {
            if (this.classList.contains('error')) {
                this.classList.remove('error');
                const errorDiv = this.parentElement.querySelector('.field-error');
                if (errorDiv) errorDiv.remove();
            }
        });
    });
}

/**
 * توابع کمکی برای نمایش Toast
 */
function showSuccess(message) {
    return toastManager.success(message, 'موفقیت');
}

function showError(message) {
    return toastManager.error(message, 'خطا');
}

/**
 * تنظیمات برای نمایش خطاهای Django
 */
function setupDjangoMessages() {
}

// این تابع می‌تواند خطاهای Django را از طریق