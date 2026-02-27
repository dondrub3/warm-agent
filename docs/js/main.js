/**
 * Warm Agent 官网JavaScript
 */

// 复制代码功能
function copyCode(btn) {
    const code = btn.closest('.code-block').querySelector('code').textContent;
    copyToClipboard(code);
    
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-check"></i>';
    btn.style.color = '#06D6A0';
    
    setTimeout(() => {
        btn.innerHTML = originalHTML;
        btn.style.color = '';
    }, 2000);
}

// 注册功能
function register() {
    const email = document.getElementById('emailInput').value;
    const password = document.getElementById('passwordInput').value;
    const terms = document.getElementById('termsCheckbox').checked;
    
    // 简单验证
    if (!email || !validateEmail(email)) {
        showToast('请输入有效的邮箱地址', 'error');
        return;
    }
    
    if (!password || password.length < 8) {
        showToast('密码至少需要8位', 'error');
        return;
    }
    
    if (!terms) {
        showToast('请同意服务条款和隐私政策', 'error');
        return;
    }
    
    // 模拟注册成功
    showToast('注册成功！正在生成API密钥...', 'success');
    
    setTimeout(() => {
        // 生成API密钥
        const apiKey = generateApiKey();
        document.getElementById('apiKeyDisplay').textContent = apiKey;
        
        // 显示结果
        document.getElementById('apiKeyForm').style.display = 'none';
        document.getElementById('apiKeyResult').style.display = 'block';
    }, 1000);
}

// 复制API密钥
function copyApiKey() {
    const apiKey = document.getElementById('apiKeyDisplay').textContent;
    copyToClipboard(apiKey);
    showToast('API密钥已复制到剪贴板', 'success');
}

// 生成API密钥
function generateApiKey() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let apiKey = 'wa_sk_';
    for (let i = 0; i < 32; i++) {
        apiKey += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return apiKey;
}

// 验证邮箱
function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// 复制到剪贴板
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
    } else {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    }
}

// 显示提示
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = toast.querySelector('i');
    
    toastMessage.textContent = message;
    
    if (type === 'error') {
        toast.style.backgroundColor = '#EF476F';
        toastIcon.className = 'fas fa-exclamation-circle';
    } else {
        toast.style.backgroundColor = '#06D6A0';
        toastIcon.className = 'fas fa-check-circle';
    }
    
    toast.classList.add('active');
    
    setTimeout(() => {
        toast.classList.remove('active');
    }, 3000);
}

// 平滑滚动
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// 导航栏滚动效果
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.boxShadow = 'none';
    }
});

// 滚动动画
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.feature-card, .pricing-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// 控制台欢迎信息
console.log('%c🤖 Warm Agent', 'font-size: 24px; font-weight: bold; color: #FF6B6B;');
console.log('%c让AI拥有温暖的心', 'font-size: 16px; color: #5D5D6B;');
console.log('%c了解更多：https://warm-agent.com', 'font-size: 14px; color: #4ECDC4;');