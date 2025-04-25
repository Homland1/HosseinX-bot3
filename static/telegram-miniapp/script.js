// انتظار می‌رود که ابتدا اسکریپت Telegram Web App در صفحه لود شده باشد
document.addEventListener('DOMContentLoaded', function() {
    // اطمینان از اینکه ابتدا اسکریپت تلگرام لود شده باشد
    if (window.Telegram && window.Telegram.WebApp) {
        initTelegramMiniApp();
    } else {
        console.error('Telegram WebApp script not loaded!');
        showError('خطا در بارگذاری ابزارهای تلگرام. لطفاً دوباره تلاش کنید.');
    }
});

/**
 * راه‌اندازی مینی اپ تلگرام
 */
function initTelegramMiniApp() {
    // دسترسی به WebApp تلگرام
    const tg = window.Telegram.WebApp;
    
    // آماده‌سازی مینی اپ
    tg.ready();
    
    // تنظیم رنگ هدر
    tg.setHeaderColor('secondary_bg_color');
    
    // باز کردن مینی اپ به اندازه کامل
    tg.expand();
    
    // نمایش اطلاعات کاربر
    displayUserInfo(tg.initDataUnsafe);
    
    // تنظیم رویدادها
    setupEventListeners(tg);
    
    // لود پیام‌های کاربر
    loadUserMessages();
}

/**
 * نمایش اطلاعات کاربر در صفحه
 */
function displayUserInfo(initData) {
    const userNameElement = document.getElementById('userName');
    const userIdElement = document.getElementById('userId');
    
    // ابتدا بررسی می‌کنیم آیا می‌توانیم اطلاعات کاربر را از تلگرام بگیریم
    if (initData && initData.user) {
        const user = initData.user;
        
        // نمایش نام کاربر
        let displayName = user.first_name;
        if (user.last_name) {
            displayName += ' ' + user.last_name;
        }
        userNameElement.textContent = displayName;
        
        // نمایش شناسه کاربر
        userIdElement.textContent = `شناسه: ${user.id}`;
        
        // اگر کاربر عکس پروفایل دارد
        if (user.photo_url) {
            const userAvatar = document.getElementById('userAvatar');
            userAvatar.innerHTML = `<img src="${user.photo_url}" class="rounded-circle" width="60" height="60" alt="${displayName}">`;
        }
    } else {
        // اگر اطلاعات کاربر از تلگرام در دسترس نبود، از پارامتر URL استفاده می‌کنیم
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const userId = urlParams.get('user_id');
            
            if (userId) {
                userNameElement.textContent = 'کاربر تلگرام';
                userIdElement.textContent = `شناسه: ${userId}`;
            } else {
                userNameElement.textContent = 'کاربر ناشناس';
                userIdElement.textContent = 'اطلاعات کاربر در دسترس نیست';
            }
        } catch (e) {
            userNameElement.textContent = 'کاربر ناشناس';
            userIdElement.textContent = 'اطلاعات کاربر در دسترس نیست';
        }
    }
}

/**
 * تنظیم رویدادهای تعاملی
 */
function setupEventListeners(tg) {
    // برگشت به چت
    document.getElementById('backToChat').addEventListener('click', function() {
        tg.close();
    });
    
    // نمایش تاریخچه پیام‌ها
    document.getElementById('showHistory').addEventListener('click', function() {
        const historySection = document.getElementById('historySection');
        const showHistoryBtn = document.getElementById('showHistory');
        
        if (historySection.style.display === 'none') {
            historySection.style.display = 'block';
            showHistoryBtn.innerHTML = '<i class="fas fa-eye-slash ms-2"></i>مخفی کردن تاریخچه';
            // اسکرول به بخش تاریخچه
            historySection.scrollIntoView({ behavior: 'smooth' });
        } else {
            historySection.style.display = 'none';
            showHistoryBtn.innerHTML = '<i class="fas fa-eye ms-2"></i>نمایش تاریخچه';
        }
    });
    
    // تنظیمات
    document.getElementById('showSettings').addEventListener('click', function() {
        tg.showPopup({
            title: 'تنظیمات',
            message: 'این بخش در حال توسعه است و به زودی فعال خواهد شد.',
            buttons: [{ type: 'ok' }]
        });
    });
    
    // راهنما
    document.getElementById('showHelp').addEventListener('click', function() {
        tg.showPopup({
            title: 'راهنمای ربات',
            message: 'دستورات ربات:\n\n' +
                    '/start - شروع ربات\n' +
                    '/help - نمایش راهنما\n' +
                    '/about - درباره ربات',
            buttons: [{ type: 'ok' }]
        });
    });
}

/**
 * بارگذاری پیام‌های کاربر از API
 */
function loadUserMessages() {
    const messageList = document.getElementById('messageList');
    const tg = window.Telegram.WebApp;
    let userId = null;
    
    // بررسی دسترسی به اطلاعات کاربر
    if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
        // گرفتن شناسه کاربر از تلگرام
        userId = tg.initDataUnsafe.user.id;
    } else {
        // تلاش برای گرفتن شناسه کاربر از پارامترهای URL
        try {
            const urlParams = new URLSearchParams(window.location.search);
            userId = urlParams.get('user_id');
        } catch (e) {
            console.error('Error getting user_id from URL:', e);
        }
    }
    
    if (userId) {
        // بارگذاری پیام‌ها برای کاربر (به صورت نمونه)
        // در اینجا می‌توانید به API خود متصل شوید و پیام‌های واقعی را بارگذاری کنید
        
        // نمایش شناسه کاربر در کنسول برای اشکال‌زدایی
        console.log('Loading messages for user:', userId);
        
        // تاخیر ساختگی برای شبیه‌سازی بارگذاری از سرور
        setTimeout(function() {
            // نمونه پیام‌ها برای نمایش
            const sampleMessages = [
                { text: 'سلام به ربات HosseinX-bot3 خوش آمدید!', time: '12:30', isFromUser: false },
                { text: 'سلام، ممنون.', time: '12:31', isFromUser: true },
                { text: 'چطور می‌توانم کمکتان کنم؟', time: '12:31', isFromUser: false },
                { text: 'لیست دستورات را به من نشان بده', time: '12:32', isFromUser: true },
                { text: 'دستورات ربات:\n/start - شروع ربات\n/help - نمایش راهنما\n/about - درباره ربات', time: '12:32', isFromUser: false }
            ];
            
            // نمایش پیام‌ها در لیست
            messageList.innerHTML = '';
            sampleMessages.forEach(msg => {
                const messageHTML = createMessageElement(msg.text, msg.time, msg.isFromUser);
                messageList.innerHTML += messageHTML;
            });
            
        }, 1000);
    } else {
        // اگر اطلاعات کاربر در دسترس نبود
        messageList.innerHTML = `
            <div class="alert alert-warning m-3">
                <i class="fas fa-exclamation-triangle me-2"></i>
                برای مشاهده پیام‌ها، لطفاً از طریق ربات تلگرام وارد شوید.
            </div>
        `;
    }
}

/**
 * ایجاد المان HTML برای یک پیام
 */
function createMessageElement(text, time, isFromUser) {
    return `
        <div class="message-item ${isFromUser ? 'message-user' : 'message-bot'}">
            <div class="message-content">
                <div class="message-text">${text.replace(/\n/g, '<br>')}</div>
                <div class="message-time">${time}</div>
            </div>
        </div>
    `;
}

/**
 * نمایش پیغام خطا در صفحه
 */
function showError(message) {
    const appContainer = document.querySelector('.app-container');
    const errorAlert = document.createElement('div');
    errorAlert.className = 'alert alert-danger m-3';
    errorAlert.innerHTML = `<i class="fas fa-exclamation-circle me-2"></i>${message}`;
    
    appContainer.prepend(errorAlert);
}