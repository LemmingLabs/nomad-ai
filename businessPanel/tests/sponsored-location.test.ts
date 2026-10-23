import assert from 'node:assert/strict';
import test from 'node:test';

import { formatKyrgyzPhoneInput, isWithinKyrgyzstan } from '../src/features/business/sponsored-places/model/sponsoredPlaces.utils.ts';

test('normalizes a Kyrgyz phone number for the sponsored place form', () => {
  assert.equal(formatKyrgyzPhoneInput('996555123456'), '+996 555 123 456');
});

test('accepts a location inside Kyrgyzstan and rejects one outside', () => {
  assert.equal(isWithinKyrgyzstan(42.8746, 74.5698), true);
  assert.equal(isWithinKyrgyzstan(48.8566, 2.3522), false);
});
