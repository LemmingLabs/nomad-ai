import { Sidebar } from '../../widgets/sidebar';
import { SubscriptionSummary } from '../../widgets/subscription-summary';
import styles from './ProfilePage.module.scss';

export function ProfilePage() {
  return (
    <div className={styles.layout}>
      <Sidebar />
      <main className={styles.main}>
        <header className={styles.header}>
          <h1 className={styles.title}>Your plan</h1>
          <p className={styles.subtitle}>
            See what you can do today, track your subscription, and upgrade when you need more room to iterate.
          </p>
        </header>
        <SubscriptionSummary />
      </main>
    </div>
  );
}

