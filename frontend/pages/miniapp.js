import { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import styles from '../styles/MiniApp.module.css';

export default function MiniApp() {
  const router = useRouter();
  const [telegramUser, setTelegramUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  
  // API URL - در محیط واقعی از متغیر محیطی استفاده می‌کنیم
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  useEffect(() => {
    if (typeof window !== 'undefined') {
      initTelegramMiniApp();
    }
  }, [router.query]);

  const initTelegramMiniApp = async () => {
    setLoading(true);
    
    // اگر در محیط تلگرام نیستیم، از پارامتر query استفاده می‌کنیم
    const { user_id } = router.query;
    
    // تلاش برای دستیابی به ویژگی‌های مینی‌اپ تلگرام
    try {
      // ویژگی WebApp در تلگرام
      const tg = window.Telegram?.WebApp;
      
      if (tg) {
        // در محیط تلگرام هستیم
        tg.ready();
        
        // تنظیم رویدادهای تعاملی
        setupEventListeners(tg);
        
        // نمایش اطلاعات کاربر
        if (tg.initDataUnsafe?.user) {
          setTelegramUser(tg.initDataUnsafe.user);
          loadUserMessages(tg.initDataUnsafe.user.id);
        }
      } else if (user_id) {
        // در محیط تلگرام نیستیم، اما شناسه کاربر را داریم
        // دریافت اطلاعات کاربر از سرور
        try {
          const response = await fetch(`${API_URL}/api/telegram-user/${user_id}`);
          if (response.ok) {
            const userData = await response.json();
            setTelegramUser(userData);
            loadUserMessages(userData.telegram_id);
          } else {
            setError('خطا در دریافت اطلاعات کاربر');
          }
        } catch (error) {
          console.error('Error fetching user data:', error);
          setError('خطا در ارتباط با سرور');
        }
      } else {
        setError('در محیط تلگرام نیستید یا شناسه کاربر ارائه نشده است');
      }
    } catch (error) {
      console.error('Error initializing mini app:', error);
      setError('خطا در راه‌اندازی مینی‌اپ');
    } finally {
      setLoading(false);
    }
  };

  const setupEventListeners = (tg) => {
    // تنظیم دکمه اصلی
    tg.MainButton.text = 'ارسال پیام';
    tg.MainButton.color = '#0C8DE8';
    
    // رویداد کلیک دکمه اصلی
    tg.MainButton.onClick(() => {
      if (newMessage.trim() && telegramUser) {
        sendMessage(telegramUser.id, newMessage);
      }
    });
  };

  const loadUserMessages = async (userId) => {
    try {
      const response = await fetch(`${API_URL}/api/messages/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages || []);
      } else {
        console.error('Error loading messages:', response.statusText);
      }
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const sendMessage = async (userId, text) => {
    if (!text.trim()) return;
    
    try {
      const response = await fetch(`${API_URL}/api/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          telegram_user_id: userId,
          message_text: text,
          is_from_user: true
        }),
      });
      
      if (response.ok) {
        // افزودن پیام به لیست پیام‌ها
        const newMessageObj = {
          telegram_user_id: userId,
          message_text: text,
          timestamp: new Date().toISOString(),
          is_from_user: true
        };
        
        setMessages(prevMessages => [newMessageObj, ...prevMessages]);
        setNewMessage('');
        
        // نمایش دکمه اصلی در تلگرام
        const tg = window.Telegram?.WebApp;
        if (tg) {
          tg.MainButton.hide();
        }
        
        // لود مجدد پیام‌ها از سرور پس از مدت کوتاهی
        setTimeout(() => loadUserMessages(userId), 1000);
      } else {
        console.error('Error sending message:', response.statusText);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleMessageChange = (e) => {
    setNewMessage(e.target.value);
    
    // نمایش یا مخفی کردن دکمه اصلی
    const tg = window.Telegram?.WebApp;
    if (tg) {
      if (e.target.value.trim()) {
        tg.MainButton.show();
      } else {
        tg.MainButton.hide();
      }
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (newMessage.trim() && telegramUser) {
      sendMessage(telegramUser.id || telegramUser.telegram_id, newMessage);
    }
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>مینی اپ حسین ایکس بات ۳</title>
        <meta name="description" content="مینی اپ تلگرام حسین ایکس بات ۳" />
        <link rel="icon" href="/favicon.ico" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
      </Head>

      <main className={styles.main}>
        {loading ? (
          <div className={styles.loading}>
            <div className={styles.spinner}></div>
            <p>در حال بارگذاری...</p>
          </div>
        ) : error ? (
          <div className={styles.error}>{error}</div>
        ) : (
          <>
            <div className={styles.userInfo}>
              {telegramUser && (
                <>
                  <div className={styles.avatar}>
                    {telegramUser.first_name ? telegramUser.first_name.charAt(0).toUpperCase() : 'U'}
                  </div>
                  <div className={styles.userDetails}>
                    <h2 className={styles.userName}>
                      {telegramUser.first_name} {telegramUser.last_name || ''}
                    </h2>
                    {telegramUser.username && (
                      <p className={styles.userUsername}>@{telegramUser.username}</p>
                    )}
                  </div>
                </>
              )}
            </div>

            <div className={styles.messagesContainer}>
              <h3 className={styles.sectionTitle}>پیام‌های شما</h3>
              
              {messages.length > 0 ? (
                <div className={styles.messagesList}>
                  {messages.map((msg, index) => (
                    <div 
                      key={index} 
                      className={`${styles.messageItem} ${msg.is_from_user ? styles.userMessage : styles.botMessage}`}
                    >
                      <div className={styles.messageContent}>
                        <p className={styles.messageText}>{msg.message_text}</p>
                        <span className={styles.messageTime}>
                          {new Date(msg.timestamp).toLocaleString('fa-IR', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className={styles.noMessages}>هنوز پیامی وجود ندارد</p>
              )}
            </div>

            <form onSubmit={handleSubmit} className={styles.messageForm}>
              <input
                type="text"
                value={newMessage}
                onChange={handleMessageChange}
                placeholder="پیام خود را بنویسید..."
                className={styles.messageInput}
              />
              <button 
                type="submit" 
                className={styles.sendButton}
                disabled={!newMessage.trim()}
              >
                ارسال
              </button>
            </form>
          </>
        )}
      </main>
    </div>
  );
}