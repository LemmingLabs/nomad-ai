export function formatPhoneInput(value: string, callingCode: string): string {
  const digits = value.replace(/\D/g, '')

  if (digits === '') {
    return ''
  }

  const normalized = digits.startsWith(callingCode)
    ? digits.slice(callingCode.length)
    : digits
  const localDigits = normalized.slice(0, 15 - callingCode.length)

  let formatted = `+${callingCode}`

  if (localDigits.length > 0) {
    formatted += ` ${localDigits.slice(0, 3)}`
  }

  if (localDigits.length > 3) {
    if (localDigits.length <= 7) {
      formatted += ` ${localDigits.slice(3)}`
    } else {
      formatted += ` ${localDigits.slice(3, 6)} ${localDigits.slice(6)}`
    }
  }

  return formatted
}

export const KYRGYZSTAN_BOUNDS: google.maps.LatLngBoundsLiteral = {
  north: 43.3,
  south: 39.1,
  west: 69.2,
  east: 80.4,
}

export const BISHKEK_CENTER: google.maps.LatLngLiteral = {
  lat: 42.8746,
  lng: 74.5698,
}

export function isWithinKyrgyzstan(lat: number, lng: number) {
  return (
    lat >= KYRGYZSTAN_BOUNDS.south &&
    lat <= KYRGYZSTAN_BOUNDS.north &&
    lng >= KYRGYZSTAN_BOUNDS.west &&
    lng <= KYRGYZSTAN_BOUNDS.east
  )
}

export function isWithinBounds(
  lat: number,
  lng: number,
  bounds: google.maps.LatLngBoundsLiteral,
) {
  return lat >= bounds.south && lat <= bounds.north && lng >= bounds.west && lng <= bounds.east
}

export function extractCityFromAddressComponents(
  components?:
    | google.maps.GeocoderAddressComponent[]
    | google.maps.places.AddressComponent[],
) {
  if (!components?.length) return ''

  const cityComponent =
    components.find((component) => component.types.includes('locality')) ??
    components.find((component) => component.types.includes('postal_town')) ??
    components.find((component) =>
      component.types.includes('administrative_area_level_2'),
    ) ??
    components.find((component) =>
      component.types.includes('administrative_area_level_1'),
    )

  if (!cityComponent) return ''

  if ('long_name' in cityComponent) {
    return cityComponent.long_name ?? ''
  }

  return cityComponent.longText ?? ''
}

export function extractRegionFromAddressComponents(
  components?:
    | google.maps.GeocoderAddressComponent[]
    | google.maps.places.AddressComponent[],
) {
  const component = components?.find((item) =>
    item.types.includes('administrative_area_level_1'),
  )
  if (!component) return ''
  return 'long_name' in component
    ? component.long_name ?? ''
    : component.longText ?? ''
}

export function extractCountryCodeFromAddressComponents(
  components?:
    | google.maps.GeocoderAddressComponent[]
    | google.maps.places.AddressComponent[],
) {
  const component = components?.find((item) => item.types.includes('country'))
  if (!component) return ''
  return 'short_name' in component
    ? component.short_name?.toUpperCase() ?? ''
    : component.shortText?.toUpperCase() ?? ''
}

export const extractCityFromPlace = extractCityFromAddressComponents
