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
  expect(screen.getByRole('navigation', { name: 'Jump to itinerary day' })).toBeTruthy();
  expect(screen.getByRole('link', { name: 'Day 2: Lake shore, Cholpon-Ata' }).getAttribute('href'))
    .toBe('#trip-day-2');
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

  expect(screen.queryByRole('navigation', { name: 'Jump to itinerary day' })).toBeNull();
  expect(screen.getByText(/This is a draft/).textContent).toContain('This is a draft');
  expect(screen.getByText('Flexible timing')).toBeTruthy();
  expect(screen.getByText('Duration unknown')).toBeTruthy();
  expect(screen.getByText('One or more activity durations are unknown for day 1.')).toBeTruthy();
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
