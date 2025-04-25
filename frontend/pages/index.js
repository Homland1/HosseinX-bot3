import Head from 'next/head';
import styles from '../styles/Home.module.css';

export default function Home() {
  return (
    <div className={styles.container}>
      <Head>
        <title>حسین ایکس بات ۳</title>
        <meta name="description" content="HosseinX-bot3 - ربات تلگرامی حسین ایکس" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>
          به <span className={styles.highlight}>حسین ایکس بات ۳</span> خوش آمدید!
        </h1>

        <p className={styles.description}>
          پنل مدیریت ربات تلگرامی حسین ایکس
        </p>

        <div className={styles.grid}>
          <a href="https://t.me/HoseinX_bot" className={styles.card}>
            <h2>ربات تلگرام &rarr;</h2>
            <p>دسترسی به ربات تلگرام حسین ایکس بات ۳</p>
          </a>

          <a href="/dashboard" className={styles.card}>
            <h2>پنل مدیریت &rarr;</h2>
            <p>دسترسی به پنل مدیریت ربات</p>
          </a>

          <a href="/miniapp" className={styles.card}>
            <h2>مینی اپ &rarr;</h2>
            <p>دسترسی به مینی اپ تلگرام</p>
          </a>

          <a href="/api/docs" className={styles.card}>
            <h2>API &rarr;</h2>
            <p>مستندات API ربات</p>
          </a>
        </div>
      </main>

      <footer className={styles.footer}>
        <a href="https://github.com/Homland1/HosseinX-bot3" target="_blank" rel="noopener noreferrer">
          ساخته شده توسط حسین - کد منبع در GitHub
        </a>
      </footer>
    </div>
  );
}

