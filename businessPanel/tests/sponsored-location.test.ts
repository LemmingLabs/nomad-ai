import { expect, test } from 'vitest';

import { extractCityFromAddressComponents, formatKyrgyzPhoneInput, isWithinKyrgyzstan } from '../src/features/business/sponsored-places/model/sponsoredPlaces.utils.ts';

test('normalizes a Kyrgyz phone number for the sponsored place form', () => {
  expect(formatKyrgyzPhoneInput('996555123456')).toBe('+996 555 123 456');
});

test('accepts a location inside Kyrgyzstan and rejects one outside', () => {
  expect(isWithinKyrgyzstan(42.8746, 74.5698)).toBe(true);
  expect(isWithinKyrgyzstan(48.8566, 2.3522)).toBe(false);
});

test('uses the city before administrative fallbacks in a selected place', () => {
  const components = [
    { long_name: 'Chuy Region', types: ['administrative_area_level_1'] },
    { long_name: 'Bishkek', types: ['locality'] },
  ] as google.maps.GeocoderAddressComponent[];
  expect(extractCityFromAddressComponents(components)).toBe('Bishkek');
  expect(extractCityFromAddressComponents([])).toBe('');
});
