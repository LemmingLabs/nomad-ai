import { afterEach, expect, test } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import type { TripDay } from '../../entities/trip';
import { DayHero } from '../../widgets/trip-day-card/DayHero';

afterEach(cleanup);

const day: TripDay = {
  day: 1, title: 'A long day exploring the mountains', city: 'Karakol', location: 'Mountain valley', activities: [],
};

test('labels and credits an unverified inspiration photo, then recovers from a broken URL', () => {
  const withImage: TripDay = { ...day, images: { hero: {
    url: 'https://example.com/photo.jpg', source: 'pexels', photo_id: '12345',
    photographer: 'A Photographer', photographer_url: 'https://example.com/photographer', alt: 'Mountains at sunrise',
  } } };
  const { rerender } = render(<DayHero day={withImage} />);

  const image = screen.getByRole('img', { name: 'Mountains at sunrise' });
  expect(screen.getByText('Inspiration photo · location not verified')).toBeTruthy();
  expect(screen.getByRole('link', { name: 'Photo by A Photographer' }).getAttribute('href')).toBe('https://example.com/photographer');
  expect(screen.getByRole('link', { name: 'Pexels' }).getAttribute('href')).toBe('https://www.pexels.com/photo/12345/');
  fireEvent.error(image);
  expect(screen.queryByRole('img')).toBeNull();
  expect(screen.getByRole('heading', { name: day.title })).toBeTruthy();
  expect(screen.queryByText('Inspiration photo · location not verified')).toBeNull();

  rerender(<DayHero day={{ ...day, images: { hero: { url: 'https://example.com/new.jpg' } } }} />);
  expect(screen.getByRole('img', { name: 'Travel inspiration photo; exact location not verified' })).toBeTruthy();
});

test('renders the day without photo metadata or an image', () => {
  render(<DayHero day={day} />);
  expect(screen.queryByRole('img')).toBeNull();
  expect(screen.getByRole('heading', { name: day.title })).toBeTruthy();
  expect(screen.getByText('Karakol • Mountain valley')).toBeTruthy();
});
