import { expect, test } from 'vitest';

import { generateTripSchema } from '../../features/trip/generate-trip/model/schema.ts';

const validTrip = {
  budget: 'medium',
  days: 5,
  interests: 'nature, culture',
  travel_style: 'relaxed',
  prompt: '',
};

void test('accepts a valid trip generation request', () => {
  expect(generateTripSchema.safeParse(validTrip).success).toBe(true);
});

void test('rejects an empty interest list', () => {
  expect(generateTripSchema.safeParse({ ...validTrip, interests: ' , ' }).success).toBe(false);
});

void test('rejects a trip longer than the supported limit', () => {
  expect(generateTripSchema.safeParse({ ...validTrip, days: 15 }).success).toBe(false);
});

void test('rejects an overly long prompt', () => {
  expect(generateTripSchema.safeParse({ ...validTrip, prompt: 'x'.repeat(1001) }).success).toBe(false);
});
