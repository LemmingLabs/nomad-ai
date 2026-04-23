import { Sidebar } from '../../widgets/sidebar';
import { PricingPlans } from '../../widgets/pricing-plans';
import styles from './PricingPage.module.scss';

export function PricingPage() {
  return (
    <div className={styles.layout}>
      <Sidebar />
      <main className={styles.main}>
        <PricingPlans />
      </main>
    </div>
  );
}

