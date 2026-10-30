import { cleanup, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, it } from 'vitest';
import { TripOverview } from '../../widgets/trip-preview/TripOverview';
import type { TripDay } from '../../entities/trip';

afterEach(cleanup);

const day = (number: number, lat?: number, lng?: number): TripDay => ({
  day: number, title: `Day ${number}`, city: 'City', location: `Place ${number}`, activities: [],
  place_candidate: lat === undefined ? null : { lat, lng },
});

it('shows suggested coordinates and a keyboard-accessible ordered list without fabricating missing routes', async () => {
  const user = userEvent.setup();
  const { container } = render(<TripOverview days={[
    day(1, 42, 74), day(2, 42, 74), day(3, 91, 74), day(4),
    { ...day(5, 43, 75), route_from_previous: { origin: 'A', destination: 'B', distance_km: 0, duration_mins: 0, transport_type: 'car', status: 'stale' } },
  ]} routeStatus="unavailable" />);
  await user.tab();
  expect(document.activeElement).toBe(screen.getByText(/Explore the trip overview/));
  await user.keyboard('{Enter}');
  expect(screen.getByText(/dashed connections are schematic/)).toBeTruthy();
  expect(screen.getByText(/Route details are unavailable/)).toBeTruthy();
  expect(screen.getByText(/3 of 5 locations available/)).toBeTruthy();
  expect(container.querySelectorAll('svg circle')).toHaveLength(2);
  expect(container.querySelector('svg text')?.textContent).toBe('1,2');
  expect(container.querySelectorAll('svg line')).toHaveLength(1);
  const list = screen.getByRole('list');
  expect(within(list).getAllByText('Location coordinates unavailable')).toHaveLength(2);
  expect(within(list).getByText('Route from previous day stale')).toBeTruthy();
  expect(within(list).getByRole('link', { name: 'Day 5: Place 5' }).getAttribute('href')).toBe('#trip-day-5');
});

it('provides a text overview when coordinates are missing, invalid or unresolved', async () => {
  const user = userEvent.setup();
  render(<TripOverview days={[day(1), day(2, NaN, 10), { ...day(3, 10, 10), place_resolution: { status: 'unresolved', provider: 'test', country_code: 'KG' } }]} />);
  await user.click(screen.getByText(/Explore the trip overview/));
  expect(screen.getByText(/No coordinates are available/)).toBeTruthy();
  expect(screen.getAllByText('Location coordinates unavailable')).toHaveLength(3);
  expect(screen.getByRole('link', { name: 'Day 1: Place 1' }).getAttribute('href')).toBe('#trip-day-1');
});
