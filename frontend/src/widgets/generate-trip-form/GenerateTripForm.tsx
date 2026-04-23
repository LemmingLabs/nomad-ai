import { useState } from 'react';
import { Minus, Plus, Sparkles, X } from 'lucide-react';
import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { generateTripSchema, type GenerateTripFormData } from '../../features/trip/generate-trip';
import { useMyLimitsQuery } from '../../entities/limit';
import { useUserStore } from '../../entities/user';
import { getRemaining, getUsageTone, TripLimitNotice, fallbackFreeLimits } from '../../features/subscription/view-usage';
import { Button } from '../../shared/ui/button/Button';
import { Input } from '../../shared/ui/input/Input';
import { Card, Textarea } from '../../shared/ui';
import styles from './GenerateTripForm.module.scss';

const budgetOptions = [
  { value: 'low', label: 'Low', hint: '$200-500' },
  { value: 'medium', label: 'Medium', hint: '$500-1200' },
  { value: 'high', label: 'High', hint: '$1200+' },
] as const;

const suggestedInterests = [
  'nature',
  'mountains',
  'food',
  'culture',
  'lakes',
  'adventure',
  'relaxation',
  'photography',
  'history',
  'local markets',
] as const;

const travelStyleOptions = [
  'relaxed',
  'adventure',
  'luxury',
  'cultural',
  'active',
  'romantic',
] as const;

function parseInterests(value: string): string[] {
  return value
    .split(',')
    .map((interest) => interest.trim())
    .filter(Boolean);
}

interface GenerateTripFormProps {
  onSubmit: (data: GenerateTripFormData) => void;
  isLoading?: boolean;
}

export function GenerateTripForm({ onSubmit, isLoading }: GenerateTripFormProps) {
  const { isAuthenticated } = useUserStore();
  const limitsQuery = useMyLimitsQuery();
  const limits = limitsQuery.data ?? (isAuthenticated ? fallbackFreeLimits : null);

  const remainingTrips = limits
    ? getRemaining(limits.trip_generations_used, limits.trip_limit_per_day)
    : null;
  const tripTone = limits
    ? getUsageTone(limits.trip_generations_used, limits.trip_limit_per_day)
    : 'ok';

  const {
    register,
    handleSubmit,
    setValue,
    control,
    formState: { errors },
  } = useForm<GenerateTripFormData>({
    resolver: zodResolver(generateTripSchema),
    defaultValues: {
      budget: 'medium',
      days: 5,
      interests: 'nature, culture',
      travel_style: 'relaxed',
      prompt: '',
    },
  });
  const [customInterest, setCustomInterest] = useState('');
  const budget = useWatch({ control, name: 'budget' });
  const days = useWatch({ control, name: 'days' });
  const interests = parseInterests(useWatch({ control, name: 'interests' }));
  const travelStyle = useWatch({ control, name: 'travel_style' });

  const updateInterests = (nextInterests: string[]) => {
    setValue('interests', nextInterests.join(', '), { shouldValidate: true });
  };

  const addCustomInterest = () => {
    const normalizedInterest = customInterest.trim().toLowerCase();
    if (!normalizedInterest || interests.includes(normalizedInterest)) {
      setCustomInterest('');
      return;
    }

    updateInterests([...interests, normalizedInterest]);
    setCustomInterest('');
  };

  return (
    <form
      className={styles.form}
      onSubmit={(event) => {
        void handleSubmit(onSubmit)(event);
      }}
    >
      <input type="hidden" {...register('budget')} />
      <input type="hidden" {...register('interests')} />
      <input type="hidden" {...register('travel_style')} />

      <div className={styles.header}>
        <span className={styles.badge}>
          <Sparkles size={14} />
          AI trip planner
        </span>
        <h2 className={styles.title}>Build your next itinerary</h2>
        <p className={styles.subtitle}>
          Pick the vibe, budget, and interests. We&apos;ll turn it into a travel plan
          that feels tailored from the first draft.
        </p>
      </div>

      <div className={styles.fields}>
        <Card className={styles.section} padding="lg">
          <div className={styles.sectionHeader}>
            <h3 className={styles.sectionTitle}>Budget</h3>
            <p className={styles.sectionHint}>Choose a comfort level, not a raw backend value.</p>
          </div>
          <div className={styles.optionGrid}>
            {budgetOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                className={styles.optionCard}
                data-active={budget === option.value}
                onClick={() => setValue('budget', option.value, { shouldValidate: true })}
              >
                <span className={styles.optionLabel}>{option.label}</span>
                <span className={styles.optionHint}>{option.hint}</span>
              </button>
            ))}
          </div>
          {errors.budget?.message && <p className={styles.error}>{errors.budget.message}</p>}
        </Card>

        <Card className={styles.section} padding="lg">
          <div className={styles.sectionHeader}>
            <h3 className={styles.sectionTitle}>Trip length</h3>
            <p className={styles.sectionHint}>A clean stepper keeps the plan realistic.</p>
          </div>
          <div className={styles.daysStepper}>
            <button
              type="button"
              className={styles.stepperButton}
              onClick={() => setValue('days', Math.max(1, days - 1), { shouldValidate: true })}
              disabled={days <= 1}
            >
              <Minus size={16} />
            </button>
            <div className={styles.daysValue}>
              <span className={styles.daysNumber}>{days}</span>
              <span className={styles.daysLabel}>{days === 1 ? 'day' : 'days'}</span>
            </div>
            <button
              type="button"
              className={styles.stepperButton}
              onClick={() => setValue('days', Math.min(14, days + 1), { shouldValidate: true })}
              disabled={days >= 14}
            >
              <Plus size={16} />
            </button>
          </div>
          {errors.days?.message && <p className={styles.error}>{errors.days.message}</p>}
        </Card>

        <Card className={styles.section} padding="lg">
          <div className={styles.sectionHeader}>
            <h3 className={styles.sectionTitle}>Interests</h3>
            <p className={styles.sectionHint}>Start with suggested themes and add your own.</p>
          </div>

          <div className={styles.chipGroup}>
            {suggestedInterests.map((interest) => {
              const isSelected = interests.includes(interest);

              return (
                <button
                  key={interest}
                  type="button"
                  className={styles.chip}
                  data-active={isSelected}
                  onClick={() =>
                    updateInterests(
                      isSelected
                        ? interests.filter((selectedInterest) => selectedInterest !== interest)
                        : [...interests, interest],
                    )
                  }
                >
                  {interest}
                </button>
              );
            })}
          </div>

          <div className={styles.customInterest}>
            <Input
              label="Add custom interest"
              placeholder="stargazing, road trips, cafes..."
              value={customInterest}
              onChange={(event) => setCustomInterest(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  event.preventDefault();
                  addCustomInterest();
                }
              }}
            />
            <Button type="button" variant="secondary" onClick={addCustomInterest}>
              Add
            </Button>
          </div>

          {interests.length > 0 && (
            <div className={styles.selectedChips}>
              {interests.map((interest) => (
                <span key={interest} className={styles.selectedChip}>
                  {interest}
                  <button
                    type="button"
                    className={styles.selectedChipRemove}
                    onClick={() =>
                      updateInterests(
                        interests.filter((selectedInterest) => selectedInterest !== interest),
                      )
                    }
                    aria-label={`Remove ${interest}`}
                  >
                    <X size={14} />
                  </button>
                </span>
              ))}
            </div>
          )}
          {errors.interests?.message && <p className={styles.error}>{errors.interests.message}</p>}
        </Card>

        <Card className={styles.section} padding="lg">
          <div className={styles.sectionHeader}>
            <h3 className={styles.sectionTitle}>Travel style</h3>
            <p className={styles.sectionHint}>Guide the tone of the itinerary with one tap.</p>
          </div>
          <div className={styles.chipGroup}>
            {travelStyleOptions.map((option) => (
              <button
                key={option}
                type="button"
                className={styles.chip}
                data-active={travelStyle === option}
                onClick={() =>
                  setValue('travel_style', option, { shouldValidate: true })
                }
              >
                {option}
              </button>
            ))}
          </div>
          {errors.travel_style?.message && (
            <p className={styles.error}>{errors.travel_style.message}</p>
          )}
        </Card>

        <Card className={styles.section} padding="lg">
          <div className={styles.sectionHeader}>
            <h3 className={styles.sectionTitle}>Trip brief</h3>
            <p className={styles.sectionHint}>
              Tell the AI what kind of trip you want, preferences, pace, places, food, scenery,
              or special requests.
            </p>
          </div>
          <Textarea
            label="Prompt"
            placeholder="Slow mornings, scenic drives, lakeside dinners, local food, and a little photography time each day."
            rows={5}
            error={errors.prompt?.message}
            {...register('prompt')}
          />
        </Card>
      </div>

      {isAuthenticated && limits && remainingTrips !== null && (
        <TripLimitNotice
          remaining={remainingTrips}
          limit={limits.trip_limit_per_day}
          tone={tripTone}
        />
      )}

      <Button type="submit" fullWidth isLoading={isLoading} size="lg">
        Generate Itinerary
      </Button>
    </form>
  );
}
