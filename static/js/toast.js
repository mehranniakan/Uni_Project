function closeToast(id) {
    const el = document.getElementById(id);
    if (el) {
        el.style.opacity = '0';
        el.style.transform = 'translateX(20px)';
        setTimeout(() => el.remove(), 400);
    }
}

// حذف خودکار بعد از ۵ ثانیه
setTimeout(() => {
    document.querySelectorAll('.toast-item').forEach(t => closeToast(t.id));
}, 5000);