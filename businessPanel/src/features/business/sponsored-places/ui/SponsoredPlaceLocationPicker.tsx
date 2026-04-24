import { useEffect, useMemo, useRef, useState } from 'react'
import {
  AdvancedMarker,
  APIProvider,
  Map,
  type MapCameraChangedEvent,
  type MapMouseEvent,
  useApiIsLoaded,
  useMap,
  useMapsLibrary,
} from '@vis.gl/react-google-maps'

import { env } from '../../../../shared/config/env'
import type { SponsoredPlaceLocationValue } from '../model/sponsoredPlaces.types'
import {
  BISHKEK_CENTER,
  extractCityFromAddressComponents,
  isWithinKyrgyzstan,
  KYRGYZSTAN_BOUNDS,
} from '../model/sponsoredPlaces.utils'

const defaultCenter = BISHKEK_CENTER
const defaultZoom = 7
const selectedZoom = 15

type SponsoredPlaceLocationPickerProps = {
  value: SponsoredPlaceLocationValue
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
  const [center, setCenter] = useState(defaultCenter)
  const [zoom, setZoom] = useState(defaultZoom)
  const [isMapReady, setIsMapReady] = useState(false)

  const position = useMemo(() => getPosition(value), [value])

  useEffect(() => {
    if (autocompleteRef.current) {
      autocompleteRef.current.value = value.address
    }
  }, [value.address])

  useEffect(() => {
    if (position) {
      setCenter(position)
      setZoom(selectedZoom)
    }
  }, [position])

  useEffect(() => {
    if (!apiIsLoaded) {
      setIsMapReady(false)
    }
  }, [apiIsLoaded])

  useEffect(() => {
    if (
      !placesLibrary ||
      !autocompleteContainerRef.current ||
      autocompleteRef.current
    ) {
      return
    }

    try {
      const autocomplete = new google.maps.places.PlaceAutocompleteElement({
        includedRegionCodes: ['kg'],
        locationRestriction: KYRGYZSTAN_BOUNDS,
        requestedRegion: 'kg',
        value: value.address,
      })
      autocomplete.placeholder = 'Search address in Kyrgyzstan'

      autocompleteRef.current = autocomplete
      autocompleteContainerRef.current.replaceChildren(autocomplete)
      setSearchInitError(null)

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

        if (!isWithinKyrgyzstan(lat, lng)) {
          setPickerError('Please select a location in Kyrgyzstan.')
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
        })

        map?.panTo({ lat, lng })
        map?.setZoom(selectedZoom)
        setCenter({ lat, lng })
        setZoom(selectedZoom)
        setPickerError(null)
      }

      autocomplete.addEventListener('gmp-select', handlePlaceSelect)

      return () => {
        autocomplete.removeEventListener('gmp-select', handlePlaceSelect)
        autocompleteContainerRef.current?.replaceChildren()
        autocompleteRef.current = null
      }
    } catch {
      setSearchInitError('Search is unavailable. You can select location on map.')
      autocompleteContainerRef.current.replaceChildren()
      autocompleteRef.current = null
    }
  }, [onChange, placesLibrary, shouldAutofillCity, value.address, value.city])

  const handleMapClick = async (event: MapMouseEvent) => {
    const latLng = event.detail.latLng
    if (!latLng) return

    const lat = latLng.lat
    const lng = latLng.lng

    if (!isWithinKyrgyzstan(lat, lng)) {
      setPickerError('Please select a location in Kyrgyzstan.')
      return
    }

    setIsResolvingAddress(true)
    onChange({
      lat: String(lat),
      lng: String(lng),
      address: value.address,
      city: value.city,
    })

    map?.panTo({ lat, lng })
    map?.setZoom(selectedZoom)
    setCenter({ lat, lng })
    setZoom(selectedZoom)

    try {
      const geocoder = new google.maps.Geocoder()
      const response = await geocoder.geocode({
        location: { lat, lng },
      })

      const result = response.results?.[0]
      const extractedCity = extractCityFromAddressComponents(
        result?.address_components,
      )

      onChange({
        lat: String(lat),
        lng: String(lng),
        address: result?.formatted_address ?? value.address,
        city: extractedCity || value.city,
      })

      setPickerError(null)
    } catch {
      setPickerError('Location selected. Please confirm address manually.')
    } finally {
      setIsResolvingAddress(false)
    }
  }

  const handleCameraChanged = (event: MapCameraChangedEvent) => {
    setCenter(event.detail.center)
    setZoom(event.detail.zoom)
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
          Search a place, then click the map to fine-tune the exact point.
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
          defaultCenter={position ?? defaultCenter}
          center={center}
          defaultZoom={position ? selectedZoom : defaultZoom}
          zoom={zoom}
          draggable
          minZoom={6}
          gestureHandling="greedy"
          disableDefaultUI={false}
          restriction={{
            latLngBounds: KYRGYZSTAN_BOUNDS,
            strictBounds: false,
          }}
          onClick={handleMapClick}
          onCameraChanged={handleCameraChanged}
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
