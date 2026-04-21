import { Link } from 'react-router-dom';
import styles from './NotFoundPage.module.scss';

export function NotFoundPage() {
  return (
    <div className={styles.page}>
      <span className={styles.emoji}>🗺️</span>
      <h1 className={styles.code}>404</h1>
      <p className={styles.message}>This destination doesn't exist on our map.</p>
      <Link to="/" className={styles.link}>← Back to Home</Link>
    </div>
  );
}
