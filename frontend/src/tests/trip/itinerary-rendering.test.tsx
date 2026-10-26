import { afterEach, expect, test } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
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
        activities: [{ time: 'morning', description: 'Explore the square', type: 'culture' }],
      },
      {
        day: 2, title: 'Lake shore', city: 'Cholpon-Ata', location: 'Issyk-Kul',
        activities: [{ time: 'afternoon', description: 'Walk along the lake', type: 'nature' }],
        route_from_previous: {
          origin: 'Bishkek', destination: 'Cholpon-Ata', transport_type: 'car',
          distance_km: 260, duration_mins: 240, estimated_cost: 3000,
        },
        place_candidate: {
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
  expect(screen.getByText('Explore the square')).toBeTruthy();
  expect(screen.getByText('Walk along the lake')).toBeTruthy();
  expect(screen.getByText('Transfer snapshot')).toBeTruthy();
  expect(screen.getAllByText('260 km').length).toBeGreaterThan(0);
  expect(screen.getAllByText('Lake Promenade').length).toBeGreaterThan(0);
  expect(screen.getByRole('link', { name: /website/i }).getAttribute('href')).toBe('https://example.com/lake');
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

  expect(screen.getByRole('status').textContent).toContain('This is a draft');
  expect(screen.getByText('Flexible timing')).toBeTruthy();
  expect(screen.getByText('Duration unknown')).toBeTruthy();
  expect(screen.getByText('One or more activity durations are unknown for day 1.')).toBeTruthy();
});
