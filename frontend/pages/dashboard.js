import { useState, useEffect } from 'react';
import Head from 'next/head';
import styles from '../styles/Dashboard.module.css';

export default function Dashboard() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [botStatus, setBotStatus] = useState('unknown');
  const [logs, setLogs] = useState([]);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');

  // API URL - در محیط واقعی از متغیر محیطی استفاده می‌کنیم
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  useEffect(() => {
    // بررسی وضعیت لاگین کاربر
    checkLoginStatus();
  }, []);

  const checkLoginStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/check-auth`, {
        method: 'GET',
        credentials: 'include',
      });
      
      if (response.ok) {
        setIsLoggedIn(true);
        fetchDashboardData();
      }
    } catch (error) {
      console.error('Error checking authentication:', error);
    }
  };

  const fetchDashboardData = async () => {
    try {
      // دریافت وضعیت ربات
      const statusResponse = await fetch(`${API_URL}/api/bot/status`, {
        credentials: 'include',
      });
      
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setBotStatus(statusData.status);
      }
      
      // دریافت لاگ‌ها
      const logsResponse = await fetch(`${API_URL}/api/logs`, {
        credentials: 'include',
      });
      
      if (logsResponse.ok) {
        const logsData = await logsResponse.json();
        setLogs(logsData.logs);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    
    try {
      const response = await fetch(`${API_URL}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
      });
      
      if (response.ok) {
        setIsLoggedIn(true);
        fetchDashboardData();
      } else {
        const errorData = await response.json();
        setLoginError(errorData.message || 'ورود ناموفق بود');
      }
    } catch (error) {
      console.error('Login error:', error);
      setLoginError('خطا در ارتباط با سرور');
    }
  };

  const handleLogout = async () => {
    try {
      await fetch(`${API_URL}/api/logout`, {
        method: 'POST',
        credentials: 'include',
      });
      setIsLoggedIn(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const startBot = async () => {
    try {
      const response = await fetch(`${API_URL}/api/bot/start`, {
        method: 'POST',
        credentials: 'include',
      });
      
      if (response.ok) {
        setBotStatus('running');
      }
    } catch (error) {
      console.error('Error starting bot:', error);
    }
  };

  const stopBot = async () => {
    try {
      const response = await fetch(`${API_URL}/api/bot/stop`, {
        method: 'POST',
        credentials: 'include',
      });
      
      if (response.ok) {
        setBotStatus('stopped');
      }
    } catch (error) {
      console.error('Error stopping bot:', error);
    }
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>پنل مدیریت | حسین ایکس بات ۳</title>
        <meta name="description" content="پنل مدیریت ربات تلگرامی حسین ایکس بات ۳" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        {!isLoggedIn ? (
          <div className={styles.loginContainer}>
            <h1 className={styles.title}>ورود به پنل مدیریت</h1>
            
            {loginError && <div className={styles.error}>{loginError}</div>}
            
            <form onSubmit={handleLogin} className={styles.form}>
              <div className={styles.formGroup}>
                <label htmlFor="username">نام کاربری:</label>
                <input
                  type="text"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  className={styles.input}
                />
              </div>
              
              <div className={styles.formGroup}>
                <label htmlFor="password">رمز عبور:</label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className={styles.input}
                />
              </div>
              
              <button type="submit" className={styles.button}>ورود</button>
            </form>
          </div>
        ) : (
          <>
            <div className={styles.header}>
              <h1 className={styles.title}>پنل مدیریت حسین ایکس بات ۳</h1>
              <button onClick={handleLogout} className={styles.logoutButton}>خروج</button>
            </div>
            
            <div className={styles.botStatus}>
              <h2>وضعیت ربات</h2>
              <div className={styles.statusIndicator}>
                <span className={`${styles.indicator} ${styles[botStatus]}`}></span>
                <span className={styles.statusText}>
                  {botStatus === 'running' ? 'در حال اجرا' : 
                   botStatus === 'stopped' ? 'متوقف شده' : 'نامشخص'}
                </span>
              </div>
              
              <div className={styles.botControls}>
                <button 
                  onClick={startBot} 
                  className={`${styles.button} ${styles.startButton}`}
                  disabled={botStatus === 'running'}
                >
                  راه‌اندازی ربات
                </button>
                <button 
                  onClick={stopBot} 
                  className={`${styles.button} ${styles.stopButton}`}
                  disabled={botStatus === 'stopped'}
                >
                  توقف ربات
                </button>
              </div>
            </div>
            
            <div className={styles.logsContainer}>
              <h2>آخرین رویدادها</h2>
              {logs.length > 0 ? (
                <ul className={styles.logsList}>
                  {logs.map((log, index) => (
                    <li key={index} className={`${styles.logItem} ${styles[log.level.toLowerCase()]}`}>
                      <span className={styles.logTime}>{new Date(log.timestamp).toLocaleString('fa-IR')}</span>
                      <span className={styles.logLevel}>{log.level}</span>
                      <span className={styles.logMessage}>{log.message}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className={styles.noLogs}>هیچ لاگی موجود نیست</p>
              )}
            </div>
          </>
        )}
      </main>

      <footer className={styles.footer}>
        <a href="https://github.com/Homland1/HosseinX-bot3" target="_blank" rel="noopener noreferrer">
          ساخته شده توسط حسین - کد منبع در GitHub
        </a>
      </footer>
    </div>
  );
}