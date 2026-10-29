import { expect, test } from 'vitest';
import { getSubsolarPoint, getSunView } from '../../widgets/home-globe/solar';

test('places the subsolar point near the equator and Greenwich at equinox noon UTC', () => {
  const sun = getSubsolarPoint(new Date('2026-03-20T12:00:00Z'));
  expect(Math.abs(sun.lat)).toBeLessThan(2);
  expect(Math.abs(sun.lng)).toBeLessThan(4);
});

test('moves the sunny side with UTC time and changes the glow when Earth rotates', () => {
  const sun = getSubsolarPoint(new Date('2026-03-20T06:00:00Z'));
  expect(sun.lng).toBeGreaterThan(80);
  expect(sun.lng).toBeLessThan(100);
  expect(getSunView(sun, sun).facing).toBeCloseTo(1, 5);
  expect(getSunView({ lat: -sun.lat, lng: sun.lng - 180 }, sun).facing).toBe(0);
});
