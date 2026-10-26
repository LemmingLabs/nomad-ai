import { expect, test } from 'vitest';

import { extractCityFromAddressComponents, formatPhoneInput, isWithinBounds } from '../src/features/business/sponsored-places/model/sponsoredPlaces.utils.ts';

test('formats phone input using the selected country calling code', () => {
  expect(formatPhoneInput('996555123456', '996')).toBe('+996 555 123 456');
  expect(formatPhoneInput('14155550123', '1')).toBe('+1 415 555 0123');
});

test('checks coordinates against the selected destination bounds', () => {
  const bounds = { north: 43.3, south: 39.1, east: 80.4, west: 69.2 };
  expect(isWithinBounds(42.8746, 74.5698, bounds)).toBe(true);
  expect(isWithinBounds(48.8566, 2.3522, bounds)).toBe(false);
});

test('uses the city before administrative fallbacks in a selected place', () => {
  const components = [
    { long_name: 'Chuy Region', types: ['administrative_area_level_1'] },
    { long_name: 'Bishkek', types: ['locality'] },
  ] as google.maps.GeocoderAddressComponent[];
  expect(extractCityFromAddressComponents(components)).toBe('Bishkek');
  expect(extractCityFromAddressComponents([])).toBe('');
});
