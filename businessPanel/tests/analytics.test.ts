import { expect, test } from 'vitest';

import { calculateCTR, formatCTR, mapInteractionBreakdownToChartData } from '../src/shared/lib/analytics.ts';

test('calculates click-through rate from interactions and impressions', () => {
  expect(calculateCTR(5, 20)).toBe(25);
  expect(calculateCTR(5, 0)).toBe(0);
});

test('formats a finite rate for the dashboard', () => {
  expect(formatCTR(12.34)).toBe('12.3%');
  expect(formatCTR(Number.NaN)).toBe('0%');
});

test('omits invalid counts and sorts interaction types', () => {
  expect(mapInteractionBreakdownToChartData({ save: 2, call: 5, map: 0 })).toEqual([
    { type: 'call', count: 5 },
    { type: 'save', count: 2 },
  ]);
});
