import { useEffect, useMemo, useRef, useState } from 'react'
import {
  AdvancedMarker,
  APIProvider,
  Map,
  type MapMouseEvent,
  useApiIsLoaded,
  useMap,
  useMapsLibrary,
} from '@vis.gl/react-google-maps'

import { env } from '../../../../shared/config/env'
import type {
  EnabledDestination,
  SponsoredPlaceLocationValue,
} from '../model/sponsoredPlaces.types'
import {
  extractCountryCodeFromAddressComponents,
  extractCityFromAddressComponents,
  extractRegionFromAddressComponents,
  isWithinBounds,
} from '../model/sponsoredPlaces.utils'

const defaultZoom = 7
const selectedZoom = 15

type SponsoredPlaceLocationPickerProps = {
  value: SponsoredPlaceLocationValue
  destination?: EnabledDestination
  disabled?: boolean
  shouldAutofillCity?: boolean
  onChange: (value: SponsoredPlaceLocationValue) => void
}

function isFiniteCoordinate(value: string) {
  const parsed = Number(value)
  return value.trim() !== '' && Number.isFinite(parsed)
}

function getPosition(value: SponsoredPlaceLocationValue) {
  if (!isFiniteCoordinate(value.lat) || !isFiniteCoordinate(value.lng)) {
    return null
  }

  return {
    lat: Number(value.lat),
    lng: Number(value.lng),
  }
}

function LocationPickerInner({
  value,
  destination,
  disabled,
  shouldAutofillCity = true,
  onChange,
}: SponsoredPlaceLocationPickerProps) {
  const apiIsLoaded = useApiIsLoaded()
  const placesLibrary = useMapsLibrary('places')
  const map = useMap()
  const autocompleteContainerRef = useRef<HTMLDivElement | null>(null)
  const autocompleteRef =
    useRef<google.maps.places.PlaceAutocompleteElement | null>(null)
  const [pickerError, setPickerError] = useState<string | null>(null)
  const [searchInitError, setSearchInitError] = useState<string | null>(null)
  const [isResolvingAddress, setIsResolvingAddress] = useState(false)
  const [isMapReady, setIsMapReady] = useState(false)

  const position = useMemo(() => getPosition(value), [value])
  const center = destination
    ? { lat: destination.center_latitude, lng: destination.center_longitude }
    : { lat: 42.8746, lng: 74.5698 }

  useEffect(() => {
    if (autocompleteRef.current) {
      autocompleteRef.current.value = value.address
    }
  }, [value.address])

  useEffect(() => {
    if (!position || !map) return
    map.panTo(position)
    map.setZoom(selectedZoom)
  }, [position, map])

  useEffect(() => {
    if (position || !map || !destination) return
    map.panTo(center)
    map.setZoom(defaultZoom)
  }, [center.lat, center.lng, destination?.country_code, map, position])

  useEffect(() => {
    if (
      !placesLibrary ||
      !destination ||
      !autocompleteContainerRef.current ||
      autocompleteRef.current
    ) {
      return
    }

    const autocompleteContainer = autocompleteContainerRef.current
    try {
      const autocomplete = new google.maps.places.PlaceAutocompleteElement({
        includedRegionCodes: [destination.country_code.toLowerCase()],
        locationRestriction: destination.bounds,
        requestedRegion: destination.country_code.toLowerCase(),
        value: value.address,
      })
      autocomplete.placeholder = `Search address in ${destination.country_name}`

      autocompleteRef.current = autocomplete
      autocompleteContainer.replaceChildren(autocomplete)

      const handlePlaceSelect: EventListener = async (rawEvent) => {
        const event = rawEvent as google.maps.places.PlacePredictionSelectEvent
        const place = event.placePrediction.toPlace()
        await place.fetchFields({
          fields: ['displayName', 'formattedAddress', 'location', 'addressComponents'],
        })

        const location = place.location

        if (!location) {
          setPickerError('Could not resolve this place location.')
          return
        }

        const lat = location.lat()
        const lng = location.lng()
        const selectedCountryCode = extractCountryCodeFromAddressComponents(
          place.addressComponents,
        )

        if (
          selectedCountryCode !== destination.country_code ||
          !isWithinBounds(lat, lng, destination.bounds)
        ) {
          setPickerError(`Please select a location in ${destination.country_name}.`)
          return
        }

        onChange({
          lat: String(lat),
          lng: String(lng),
          address: place.formattedAddress ?? value.address,
          city:
            shouldAutofillCity && value.city.trim() === ''
              ? extractCityFromAddressComponents(place.addressComponents)
              : value.city,
          region: extractRegionFromAddressComponents(place.addressComponents),
        })

        map?.panTo({ lat, lng })
        map?.setZoom(selectedZoom)
        setPickerError(null)
      }

      autocomplete.addEventListener('gmp-select', handlePlaceSelect)

      return () => {
        autocomplete.removeEventListener('gmp-select', handlePlaceSelect)
        autocompleteContainer.replaceChildren()
        autocompleteRef.current = null
      }
    } catch {
      const errorFrame = requestAnimationFrame(() => {
        setSearchInitError('Search is unavailable. You can select location on map.')
      })
      autocompleteContainer.replaceChildren()
      autocompleteRef.current = null
      return () => cancelAnimationFrame(errorFrame)
    }
  }, [destination, map, onChange, placesLibrary, shouldAutofillCity, value.address, value.city])

  const handleMapClick = async (event: MapMouseEvent) => {
    const latLng = event.detail.latLng
    if (!latLng) return

    const lat = latLng.lat
    const lng = latLng.lng

    if (!destination || !isWithinBounds(lat, lng, destination.bounds)) {
      setPickerError(`Please select a location in ${destination?.country_name ?? 'the selected country'}.`)
      return
    }

    setIsResolvingAddress(true)
    map?.panTo({ lat, lng })
    map?.setZoom(selectedZoom)

    try {
      const geocoder = new google.maps.Geocoder()
      const response = await geocoder.geocode({
        location: { lat, lng },
      })

      const result = response.results?.[0]
      if (
        extractCountryCodeFromAddressComponents(result?.address_components) !==
        destination.country_code
      ) {
        setPickerError(`Please select a location in ${destination.country_name}.`)
        return
      }
      const extractedCity = extractCityFromAddressComponents(
        result?.address_components,
      )

      onChange({
        lat: String(lat),
        lng: String(lng),
        address: result?.formatted_address ?? value.address,
        city: extractedCity || value.city,
        region:
          extractRegionFromAddressComponents(result?.address_components) || value.region,
      })

      setPickerError(null)
    } catch {
      setPickerError('Location selected. Please confirm address manually.')
    } finally {
      setIsResolvingAddress(false)
    }
  }

  return (
    <div className="space-y-3 rounded-lg border border-neutral-200 bg-neutral-50 p-4">
      <div className="space-y-1">
        <label className="block text-sm font-medium text-neutral-700">
          Location picker
        </label>
        <div
          ref={autocompleteContainerRef}
          className="relative z-50 rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-900"
          aria-disabled={disabled}
        />
        {!placesLibrary ? (
          <p className="text-xs text-neutral-500">Loading search...</p>
        ) : null}
        {searchInitError ? (
          <p className="text-xs text-red-600">{searchInitError}</p>
        ) : null}
        <p className="text-xs text-neutral-500">
          {destination
            ? `Search a place in ${destination.country_name}, then click the map to fine-tune the point.`
            : 'Select a country to load its location picker.'}
        </p>
      </div>

      <div className="relative h-[320px] overflow-hidden rounded-lg border border-neutral-200 bg-white">
        {!apiIsLoaded || !isMapReady ? (
          <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/90 text-sm text-neutral-600">
            Loading map...
          </div>
        ) : null}
        <Map
          mapId={env.googleMapsMapId}
          style={{ width: '100%', height: 320 }}
          defaultCenter={position ?? center}
          defaultZoom={position ? selectedZoom : defaultZoom}
          draggable
          minZoom={6}
          gestureHandling="greedy"
          disableDefaultUI={false}
          restriction={destination
            ? { latLngBounds: destination.bounds, strictBounds: true }
            : undefined}
          onClick={handleMapClick}
          onTilesLoaded={() => setIsMapReady(true)}
        >
          {position ? <AdvancedMarker position={position} /> : null}
        </Map>
      </div>

      {isResolvingAddress ? (
        <p className="text-sm text-neutral-600">Resolving address...</p>
      ) : null}
      {pickerError ? <p className="text-sm text-red-600">{pickerError}</p> : null}
    </div>
  )
}

export function SponsoredPlaceLocationPicker(
  props: SponsoredPlaceLocationPickerProps,
) {
  if (!env.googleMapsApiKey) {
    return (
      <div className="rounded-lg border border-dashed border-neutral-200 bg-neutral-50 p-4 text-sm text-neutral-600">
        Google Maps is not configured. You can enter coordinates manually.
      </div>
    )
  }

  if (!env.googleMapsMapId) {
    return (
      <div className="rounded-lg border border-dashed border-neutral-200 bg-neutral-50 p-4 text-sm text-neutral-600">
        Google Maps Map ID is not configured.
      </div>
    )
  }

  return (
    <APIProvider apiKey={env.googleMapsApiKey} libraries={['places']}>
      <LocationPickerInner {...props} />
    </APIProvider>
  )
}
