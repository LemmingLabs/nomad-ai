import assert from 'node:assert/strict';
import test from 'node:test';

import { calculateCTR, formatCTR, mapInteractionBreakdownToChartData } from '../src/shared/lib/analytics.ts';

test('calculates click-through rate from interactions and impressions', () => {
  assert.equal(calculateCTR(5, 20), 25);
  assert.equal(calculateCTR(5, 0), 0);
});

test('formats a finite rate for the dashboard', () => {
  assert.equal(formatCTR(12.34), '12.3%');
  assert.equal(formatCTR(Number.NaN), '0%');
});

test('omits invalid counts and sorts interaction types', () => {
  assert.deepEqual(mapInteractionBreakdownToChartData({ save: 2, call: 5, map: 0 }), [
    { type: 'call', count: 5 },
    { type: 'save', count: 2 },
  ]);
});
