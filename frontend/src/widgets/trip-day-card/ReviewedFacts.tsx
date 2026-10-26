import type { TripReviewedFact } from '../../entities/trip';
import { humanizeToken } from '../../entities/trip/lib/presentation';
import styles from './ReviewedFacts.module.scss';

type ReviewedFactsProps = {
  facts?: TripReviewedFact[];
};

export function ReviewedFacts({ facts }: ReviewedFactsProps) {
  if (!facts?.length) return null;

  return (
    <section className={styles.card} aria-label="Source-reviewed facts">
      <div className={styles.header}>
        <p className={styles.eyebrow}>Source-reviewed facts</p>
        <p className={styles.copy}>Each claim has its own source and check date.</p>
      </div>
      <ul className={styles.list}>
        {facts.map((fact, index) => (
          <li className={styles.fact} key={`${fact.subject_type}-${fact.fact_type}-${index}`}>
            <div className={styles.label}>{humanizeToken(fact.fact_type) ?? fact.fact_type}</div>
            <p className={styles.value}>{fact.value}</p>
            <div className={styles.attribution}>
              <a href={fact.source_url} target="_blank" rel="noreferrer">
                {fact.attribution_text || fact.source_name}
              </a>
              <time dateTime={fact.checked_at}>
                Checked {new Date(fact.checked_at).toLocaleDateString()}
              </time>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
