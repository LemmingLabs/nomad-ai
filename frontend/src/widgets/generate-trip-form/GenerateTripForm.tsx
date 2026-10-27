import { useEffect, useMemo, useState, type ChangeEvent } from 'react';
import { Check, Minus, Plus, Sparkles, X } from 'lucide-react';
import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { generateTripSchema, type GenerateTripFormData } from '../../features/trip/generate-trip';
import { useMyLimitsQuery } from '../../entities/limit';
import { useUserStore } from '../../entities/user';
import { useDestinationsQuery } from '../../entities/destination';
import { getRemaining, getUsageTone, TripLimitNotice, fallbackFreeLimits } from '../../features/subscription/view-usage';
import { Button } from '../../shared/ui/button/Button';
import { Input } from '../../shared/ui/input/Input';
import { Card, Textarea } from '../../shared/ui';
import styles from './GenerateTripForm.module.scss';

const budgetOptions = [
  { value: 'low', label: 'Budget-conscious', hint: 'Prefer lower-priced suggestions' },
  { value: 'medium', label: 'Balanced', hint: 'Prefer mid-priced suggestions' },
  { value: 'high', label: 'Higher comfort', hint: 'Prefer higher-priced suggestions' },
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
  const destinationsQuery = useDestinationsQuery();
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
      country_code: '',
      destination_id: '',
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
  const destinationId = useWatch({ control, name: 'destination_id' });
  const destinations = useMemo(() => destinationsQuery.data ?? [], [destinationsQuery.data]);
  const selectedDestination = destinations.find((destination) => destination.id === destinationId);

  useEffect(() => {
    if (!destinationId && destinations.length > 0) {
      const firstDestination = destinations[0];
      setValue('destination_id', firstDestination.id, { shouldValidate: true });
      setValue('country_code', firstDestination.country_code, { shouldValidate: true });
    }
  }, [destinationId, destinations, setValue]);

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
      <input type="hidden" {...register('country_code')} />
      <input type="hidden" {...register('interests')} />

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
            <h3 className={styles.sectionTitle}>Destination</h3>
            <p className={styles.sectionHint}>
              Choose a destination currently supported by NomadAI.
            </p>
          </div>
          <label className={styles.destinationLabel} htmlFor="trip-destination">
            Country or destination
          </label>
          <select
            id="trip-destination"
            className={styles.destinationSelect}
            value={destinationId}
            disabled={destinationsQuery.isLoading || destinationsQuery.isError || destinations.length === 0}
            aria-invalid={Boolean(errors.destination_id)}
            aria-describedby="trip-destination-status"
            {...register('destination_id', {
              onChange: (event: ChangeEvent<HTMLSelectElement>) => {
                const selected = destinations.find((destination) => destination.id === event.target.value);
                setValue('country_code', selected?.country_code ?? '', { shouldValidate: true });
              },
            })}
          >
            {destinationsQuery.isLoading && <option value="">Loading supported destinations…</option>}
            {destinations.map((destination) => (
              <option key={destination.id} value={destination.id}>
                {destination.name === destination.country_name
                  ? destination.name
                  : `${destination.name}, ${destination.country_name}`}
              </option>
            ))}
          </select>
          <p id="trip-destination-status" className={styles.sectionHint} role={destinationsQuery.isError ? 'alert' : undefined}>
            {destinationsQuery.isError
              ? 'Supported destinations could not be loaded. Try again before generating a trip.'
              : destinations.length === 0 && !destinationsQuery.isLoading
                ? 'There are no destinations available for trip generation right now.'
                : selectedDestination
                  ? `${selectedDestination.country_name} is currently available for trip planning.`
                  : 'Loading the destinations available for trip planning.'}
          </p>
          {destinationsQuery.isError && (
            <Button type="button" variant="secondary" onClick={() => void destinationsQuery.refetch()}>
              Retry loading destinations
            </Button>
          )}
          {errors.destination_id?.message && <p className={styles.error}>{errors.destination_id.message}</p>}
        </Card>

        <Card className={styles.section} padding="lg">
          <div className={styles.sectionHeader}>
            <h3 className={styles.sectionTitle} id="trip-budget-label">Budget preference</h3>
            <p className={styles.sectionHint} id="trip-budget-hint">
              This relative preference guides place suggestions. It is not a price estimate or a per-person or trip total; no currency amount is calculated.
            </p>
          </div>
          <div
            className={styles.optionGrid}
            role="radiogroup"
            aria-labelledby="trip-budget-label"
            aria-describedby={errors.budget ? 'trip-budget-hint trip-budget-error' : 'trip-budget-hint'}
          >
            {budgetOptions.map((option) => (
              <label
                key={option.value}
                className={styles.optionCard}
                data-active={budget === option.value}
              >
                <input
                  className={styles.choiceInput}
                  type="radio"
                  value={option.value}
                  {...register('budget')}
                />
                <span className={styles.optionLabel}>{option.label}</span>
                <span className={styles.optionHint}>{option.hint}</span>
                {budget === option.value && (
                  <span className={styles.choiceCheck} aria-hidden="true">
                    <Check size={14} />
                    Selected
                  </span>
                )}
              </label>
            ))}
          </div>
          {errors.budget?.message && <p className={styles.error} id="trip-budget-error" role="alert">{errors.budget.message}</p>}
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
              aria-label="Decrease trip length"
              onClick={() => setValue('days', Math.max(1, days - 1), { shouldValidate: true })}
              disabled={days <= 1}
            >
              <Minus size={16} />
            </button>
            <div
              className={styles.daysValue}
              role="status"
              aria-live="polite"
              aria-atomic="true"
            >
              <span className={styles.daysNumber}>{days}</span>
              <span className={styles.daysLabel}>{days === 1 ? 'day' : 'days'}</span>
            </div>
            <button
              type="button"
              className={styles.stepperButton}
              aria-label="Increase trip length"
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
            <h3 className={styles.sectionTitle} id="interests-label">Interests</h3>
            <p className={styles.sectionHint} id="interests-hint">Start with suggested themes and add your own.</p>
          </div>

          <div
            className={styles.chipGroup}
            role="group"
            aria-labelledby="interests-label"
            aria-describedby={errors.interests ? 'interests-hint interests-error' : 'interests-hint'}
          >
            {suggestedInterests.map((interest) => {
              const isSelected = interests.includes(interest);

              return (
                <button
                  key={interest}
                  type="button"
                  className={styles.chip}
                  data-active={isSelected}
                  aria-pressed={isSelected}
                  onClick={() =>
                    updateInterests(
                      isSelected
                        ? interests.filter((selectedInterest) => selectedInterest !== interest)
                        : [...interests, interest],
                    )
                  }
                >
                  {isSelected && <Check size={14} aria-hidden="true" />}
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
          {errors.interests?.message && (
            <p className={styles.error} id="interests-error" role="alert">
              {errors.interests.message}
            </p>
          )}
        </Card>

        <Card className={styles.section} padding="lg">
          <div className={styles.sectionHeader}>
            <h3 className={styles.sectionTitle} id="travel-style-label">
              Travel style
            </h3>
            <p className={styles.sectionHint} id="travel-style-hint">
              Guide the tone of the itinerary with one selection.
            </p>
          </div>
          <div
            className={styles.chipGroup}
            role="radiogroup"
            aria-labelledby="travel-style-label"
            aria-describedby={errors.travel_style ? 'travel-style-hint travel-style-error' : 'travel-style-hint'}
          >
            {travelStyleOptions.map((option) => (
              <label
                key={option}
                className={styles.chipOption}
                data-active={travelStyle === option}
              >
                <input
                  className={styles.choiceInput}
                  type="radio"
                  value={option}
                  {...register('travel_style')}
                />
                {travelStyle === option && <Check size={14} aria-hidden="true" />}
                <span>{option}</span>
              </label>
            ))}
          </div>
          {errors.travel_style?.message && (
            <p className={styles.error} id="travel-style-error" role="alert">
              {errors.travel_style.message}
            </p>
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

      <Button
        type="submit"
        fullWidth
        isLoading={isLoading}
        size="lg"
        disabled={!selectedDestination || destinationsQuery.isLoading || destinationsQuery.isError || Boolean(isLoading)}
      >
        Generate Itinerary
      </Button>
    </form>
  );
}
