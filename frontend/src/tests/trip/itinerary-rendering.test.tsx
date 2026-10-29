import { afterEach, expect, test } from 'vitest';
import { cleanup, render, screen, within } from '@testing-library/react';
import { TripPreview } from '../../widgets/trip-preview/TripPreview';
import type { TripItinerary } from '../../entities/trip/model/types';

afterEach(cleanup);

test('renders route evidence and place details for a multi-day itinerary', () => {
  const itinerary: TripItinerary = {
    summary: 'Lakes and culture',
    total_days: 2,
    interests: ['nature', 'culture'],
    travel_style: 'relaxed',
    days: [
      {
        day: 1, title: 'Old town', city: 'Bishkek', location: 'Ala-Too Square',
        activities: [{ time: 'morning', description: 'Explore the square', type: 'culture', content_status: 'ai_suggestion', duration_minutes: 90, duration_status: 'estimated' }],
      },
      {
        day: 2, title: 'Lake shore', city: 'Cholpon-Ata', location: 'Issyk-Kul',
        activities: [{ time: 'afternoon', description: 'Walk along the lake', type: 'nature', content_status: 'mock_suggestion' }],
        route_from_previous: {
          origin: 'Bishkek', destination: 'Cholpon-Ata', transport_type: 'car',
          distance_km: 260, duration_mins: 240, estimated_cost: 3000,
        },
        place_candidate: {
          provider: 'google_places',
          name: 'Lake Promenade', city: 'Cholpon-Ata', lat: 42.64, lng: 77.07,
          rating: 4.6, user_rating_count: 1200, matched_interest: 'nature',
          business_status: 'OPERATIONAL', types: ['point_of_interest', 'park'],
          website_uri: 'https://example.com/lake',
        },
      },
    ],
  };

  render(<TripPreview itinerary={itinerary} tripId={42} budget="medium" />);

  expect(screen.getByText('Old town')).toBeTruthy();
  expect(screen.getByText('Lake shore')).toBeTruthy();
  expect(screen.getByRole('navigation', { name: 'Jump to itinerary day' })).toBeTruthy();
  expect(screen.getByRole('link', { name: 'Day 2: Lake shore, Cholpon-Ata' }).getAttribute('href'))
    .toBe('#trip-day-2');
  expect(screen.getByText('Explore the square')).toBeTruthy();
  expect(screen.getByText('AI suggestion')).toBeTruthy();
  expect(screen.getByText('Development mock')).toBeTruthy();
  expect(screen.getByText('Budget preference')).toBeTruthy();
  expect(screen.getByText('Balanced')).toBeTruthy();
  expect(screen.getByText(/Relative price preference only; no trip cost calculated/)).toBeTruthy();
  expect(screen.getByText('Walk along the lake')).toBeTruthy();
  expect(screen.getByText(/Google Places result\. Check current listing details/)).toBeTruthy();
  expect(screen.getByText('Est. 90 min')).toBeTruthy();
  expect(screen.getByText('Transfer snapshot')).toBeTruthy();
  expect(screen.getAllByText('260 km').length).toBeGreaterThan(0);
  expect(screen.getAllByText('Lake Promenade').length).toBeGreaterThan(0);
  expect(screen.getByRole('link', { name: /website/i }).getAttribute('href')).toBe('https://example.com/lake');
});

test('does not infer a day duration from the number of activities', () => {
  const itinerary: TripItinerary = {
    total_days: 1,
    days: [{
      day: 1,
      title: 'City day',
      city: 'Bishkek',
      location: 'City Center',
      activities: [
        { description: 'Visit a museum', type: 'culture' },
        { description: 'Walk in a park', type: 'nature' },
      ],
    }],
  };

  render(<TripPreview itinerary={itinerary} />);

  expect(screen.queryByText('Day pace')).toBeNull();
  expect(screen.queryByText(/exploring/)).toBeNull();
});

test('labels an estimated taxi fare as a per-leg vehicle amount', () => {
  const itinerary: TripItinerary = {
    total_days: 2,
    days: [
      {
        day: 1,
        title: 'Arrival',
        city: 'Bishkek',
        location: 'Airport',
        activities: [],
      },
      {
        day: 2,
        title: 'City walk',
        city: 'Bishkek',
        location: 'City Center',
        activities: [],
        route_from_previous: {
          origin: 'Airport',
          destination: 'City Center',
          transport_type: 'taxi',
          distance_km: 30,
          duration_mins: 40,
          estimated_cost: 440,
        },
      },
    ],
  };

  render(<TripPreview itinerary={itinerary} />);

  expect(screen.getByText('~440 KGS')).toBeTruthy();
  expect(screen.getByText(/Rough taxi fare for this route leg, for the vehicle rather than per traveler/)).toBeTruthy();
  expect(screen.getByText(/separate from the trip total/)).toBeTruthy();
});

test('renders degraded generation state and missing timing for a legacy day', () => {
  const itinerary: TripItinerary = {
    summary: 'A short city break',
    total_days: 1,
    generation_status: { state: 'degraded', source: 'mock', reasons: ['provider_error'] },
    quality_warnings: [{
      code: 'activity_duration_unknown',
      day: 1,
      message: 'One or more activity durations are unknown for day 1.',
    }],
    days: [{
      day: 1,
      title: 'City day',
      city: 'Bishkek',
      location: 'Ala-Too Square',
      activities: [{ description: 'Explore the square', type: 'sightseeing' }],
    }],
  };

  render(<TripPreview itinerary={itinerary} />);

  expect(screen.queryByRole('navigation', { name: 'Jump to itinerary day' })).toBeNull();
  expect(screen.getByText(/This is a draft/).textContent).toContain('This is a draft');
  expect(screen.getByText('Flexible timing')).toBeTruthy();
  expect(screen.getByText('Duration unknown')).toBeTruthy();
  expect(screen.getByText('One or more activity durations are unknown for day 1.')).toBeTruthy();
});

test('clearly explains when no destination-safe development fallback exists', () => {
  const itinerary: TripItinerary = {
    summary: 'No development mock itinerary is available for Japan.',
    total_days: 2,
    generation_status: {
      state: 'degraded',
      source: 'mock',
      reasons: ['ai_generation_failed', 'mock_unavailable_for_destination'],
    },
    days: [],
  };

  render(<TripPreview itinerary={itinerary} destinationName="Japan" />);

  expect(screen.getByRole('status').textContent).toContain(
    'Development fallback is unavailable for Japan',
  );
  expect(screen.getByRole('status').textContent).toContain('no itinerary was created');
});

test('renders source attribution for fact-level reviewed information', () => {
  const itinerary: TripItinerary = {
    days: [{
      day: 1,
      title: 'Trail day',
      city: 'Karakol',
      location: 'Ala-Kul trail',
      activities: [],
      reviewed_facts: [{
        subject_type: 'route',
        fact_type: 'permit_required',
        value: 'A permit is required for this route.',
        source_name: 'Park authority',
        source_url: 'https://example.com/permits',
        attribution_text: 'Source: Park authority',
        checked_at: '2026-10-20T10:00:00Z',
        verification_status: 'reviewed',
      }],
    }],
  };

  render(<TripPreview itinerary={itinerary} />);

  expect(screen.getByRole('region', { name: 'Source-reviewed facts' })).toBeTruthy();
  expect(screen.getByText('A permit is required for this route.')).toBeTruthy();
  expect(screen.getByRole('link', { name: 'Source: Park authority' }).getAttribute('href'))
    .toBe('https://example.com/permits');
  expect(screen.getByText(/Checked/)).toBeTruthy();
});

test('groups day warnings with their days and keeps unmatched warnings visible', () => {
  const itinerary: TripItinerary = {
    days: [
      { day: 1, title: 'City', city: 'Bishkek', location: 'Center', activities: [] },
      { day: 2, title: 'Lake', city: 'Karakol', location: 'Lake', activities: [],
        route_from_previous: { origin: 'Bishkek', destination: 'Karakol', distance_km: 0, duration_mins: 0, transport_type: 'unknown', status: 'stale' } },
    ],
    route_status: 'unavailable',
    quality_warnings: [
      { code: 'overlap', day: 1, message: 'Day one times may overlap.' },
      { code: 'route', day: 2, message: 'Day two route is stale.' },
      { code: 'pace', day: 2, message: 'Day two may be too long.' },
      { code: 'global', message: 'Review the trip details.' },
      { code: 'missing', day: 7, message: 'An unavailable day needs review.' },
    ],
  };
  render(<TripPreview itinerary={itinerary} />);

  const overview = screen.getByRole('region', { name: 'Days to review' });
  expect(overview.getAttribute('data-print-hide')).toBe('true');
  expect(within(overview).getByRole('link', { name: 'Day 2 · 2 notes' }).getAttribute('href')).toBe('#trip-day-2');
  const dayOne = screen.getByRole('region', { name: 'Review notes for day 1' });
  const dayTwo = screen.getByRole('region', { name: 'Review notes for day 2' });
  expect(within(dayOne).getByText('Day one times may overlap.')).toBeTruthy();
  expect(within(dayTwo).getByText('Day two route is stale.')).toBeTruthy();
  expect(within(dayTwo).getByText('Day two may be too long.')).toBeTruthy();
  expect(screen.getByText('Review the trip details.')).toBeTruthy();
  expect(screen.getByText('An unavailable day needs review.')).toBeTruthy();
  expect(screen.getByText('Route details could not be refreshed for this itinerary.')).toBeTruthy();
  expect(screen.getByText(/transfer details come from before the last itinerary edit/i)).toBeTruthy();
});

test('does not show a review overview when there are no day warnings', () => {
  render(<TripPreview itinerary={{ days: [{ day: 1, title: 'City', city: 'Bishkek', location: 'Center', activities: [] }] }} />);
  expect(screen.queryByRole('region', { name: 'Days to review' })).toBeNull();
});
