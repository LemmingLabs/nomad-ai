import assert from 'node:assert/strict';
import test from 'node:test';

import { generateTripSchema } from '../features/trip/generate-trip/model/schema.ts';

const validTrip = {
  budget: 'medium',
  days: 5,
  interests: 'nature, culture',
  travel_style: 'relaxed',
  prompt: '',
};

void test('accepts a valid trip generation request', () => {
  assert.equal(generateTripSchema.safeParse(validTrip).success, true);
});

void test('rejects an empty interest list', () => {
  assert.equal(generateTripSchema.safeParse({ ...validTrip, interests: ' , ' }).success, false);
});

void test('rejects a trip longer than the supported limit', () => {
  assert.equal(generateTripSchema.safeParse({ ...validTrip, days: 15 }).success, false);
});

void test('rejects an overly long prompt', () => {
  assert.equal(generateTripSchema.safeParse({ ...validTrip, prompt: 'x'.repeat(1001) }).success, false);
});
