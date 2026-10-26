import { useEffect, useId, useState, type FormEvent } from 'react'
import { offersApi, type OfferDemoItem, type OfferSearchRequest } from '../../entities/offers'
import styles from './OffersSearchPanel.module.scss'

type OffersSearchPanelProps = {
  countryCode?: string
  destinationCity?: string
}

type AirportReference = {
  iata: string
  name: string
  city: string
  country_code: string
}

function dateInputValue(date: Date): string {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000)
  return local.toISOString().slice(0, 10)
}

function futureDate(daysAhead: number): string {
  const value = new Date()
  value.setDate(value.getDate() + daysAhead)
  return dateInputValue(value)
}

function followingDate(value: string): string {
  const result = new Date(`${value}T12:00:00`)
  result.setDate(result.getDate() + 1)
  return dateInputValue(result)
}

function getUnavailableMessage(error: unknown): string {
  if (typeof error === 'object' && error !== null && 'response' in error) {
    const response = (error as { response?: { data?: unknown } }).response
    const data = response?.data
    if (typeof data === 'object' && data !== null && 'message' in data) {
      const message = (data as { message?: unknown }).message
      if (typeof message === 'string' && message.trim()) return message
    }
  }
  return 'Offers could not be checked right now. Your trip plan is unchanged.'
}

export function OffersSearchPanel({ countryCode, destinationCity = '' }: OffersSearchPanelProps) {
  const airportListId = useId()
  const [airportSuggestions, setAirportSuggestions] = useState<AirportReference[]>([])
  const [kind, setKind] = useState<'flight' | 'stay'>('flight')
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState(destinationCity)
  const [departureDate, setDepartureDate] = useState(futureDate(14))
  const [returnDate, setReturnDate] = useState(futureDate(21))
  const [passengers, setPassengers] = useState(1)
  const [checkIn, setCheckIn] = useState(futureDate(14))
  const [checkOut, setCheckOut] = useState(futureDate(17))
  const [adults, setAdults] = useState(1)
  const [rooms, setRooms] = useState(1)
  const [isPending, setIsPending] = useState(false)
  const [unavailableMessage, setUnavailableMessage] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [demoMessage, setDemoMessage] = useState('')
  const [demoOffers, setDemoOffers] = useState<OfferDemoItem[]>([])

  useEffect(() => {
    if (!import.meta.env.DEV) return
    let isCurrent = true
    void import('../../entities/offers/model/airportReference.json').then(({ default: reference }) => {
      if (isCurrent) setAirportSuggestions(reference.airports)
    })
    return () => { isCurrent = false }
  }, [])

  const clearSearchState = () => {
    setUnavailableMessage('')
    setSuccessMessage('')
    setDemoMessage('')
    setDemoOffers([])
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!countryCode) return

    const request: OfferSearchRequest = kind === 'flight'
      ? {
          kind,
          destination_country_code: countryCode.toUpperCase(),
          origin: origin.trim(),
          destination: destination.trim(),
          departure_date: departureDate,
          return_date: returnDate || null,
          passengers,
        }
      : {
          kind,
          destination_country_code: countryCode.toUpperCase(),
          destination_city: destination.trim(),
          check_in: checkIn,
          check_out: checkOut,
          adults,
          rooms,
        }
    clearSearchState()
    setIsPending(true)
    try {
      const response = await offersApi.search(request)
      if (response.state === 'demo') {
        setDemoMessage(response.message)
        setDemoOffers(response.offers)
      } else {
        setSuccessMessage(`${response.message} No current prices are shown until an approved supplier is connected.`)
      }
    } catch (error) {
      setUnavailableMessage(getUnavailableMessage(error))
    } finally {
      setIsPending(false)
    }
  }

  return (
    <section className={styles.panel} aria-labelledby="offers-title">
      <div className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Supplier offers</p>
          <h3 id="offers-title">Search flights and stays</h3>
          <p className={styles.description}>
            Search is separate from your itinerary and never changes its estimates.
          </p>
        </div>
        <span className={styles.readOnly}>{demoMessage ? 'No booking link' : 'External booking'}</span>
      </div>

      <div className={styles.tabs} role="tablist" aria-label="Offer type">
        <button type="button" role="tab" aria-selected={kind === 'flight'} onClick={() => { setKind('flight'); clearSearchState() }}>
          Flights
        </button>
        <button type="button" role="tab" aria-selected={kind === 'stay'} onClick={() => { setKind('stay'); clearSearchState() }}>
          Stays
        </button>
      </div>

      {!countryCode ? (
        <p className={styles.notice} role="status">Offers are not available for this trip yet.</p>
      ) : (
        <form className={styles.form} onSubmit={(event) => { void submit(event) }}>
          {kind === 'flight' ? (
            <>
              <label>Origin airport or city
                <input required list={airportListId} minLength={2} maxLength={120} value={origin} onChange={(event) => setOrigin(event.target.value)} placeholder="e.g. Almaty or ALA" />
              </label>
              <label>Arrival airport or city
                <input required list={airportListId} minLength={2} maxLength={120} value={destination} onChange={(event) => setDestination(event.target.value)} placeholder="Destination city or airport" />
              </label>
              <label>Departure
                <input required type="date" min={futureDate(0)} value={departureDate} onChange={(event) => setDepartureDate(event.target.value)} />
              </label>
              <label>Return (optional)
                <input type="date" min={departureDate} value={returnDate} onChange={(event) => setReturnDate(event.target.value)} />
              </label>
              <label>Passengers
                <input required type="number" min={1} max={9} value={passengers} onChange={(event) => setPassengers(Number(event.target.value))} />
              </label>
              {import.meta.env.DEV && airportSuggestions.length > 0 ? (
                <>
                  <datalist id={airportListId}>
                    {airportSuggestions.map((airport) => (
                      <option
                        key={airport.iata}
                        value={`${airport.iata} — ${airport.city}`}
                        label={`${airport.name} · ${airport.country_code}`}
                      />
                    ))}
                  </datalist>
                  <p className={styles.referenceNote}>
                    Development airport suggestions from OurAirports; schedules and prices are not checked.
                  </p>
                </>
              ) : null}
            </>
          ) : (
            <>
              <label>Destination city
                <input required minLength={2} maxLength={120} value={destination} onChange={(event) => setDestination(event.target.value)} placeholder="City for your stay" />
              </label>
              <label>Check-in
                <input required type="date" min={futureDate(0)} value={checkIn} onChange={(event) => setCheckIn(event.target.value)} />
              </label>
              <label>Check-out
                <input required type="date" min={followingDate(checkIn)} value={checkOut} onChange={(event) => setCheckOut(event.target.value)} />
              </label>
              <label>Adults
                <input required type="number" min={1} max={16} value={adults} onChange={(event) => setAdults(Number(event.target.value))} />
              </label>
              <label>Rooms
                <input required type="number" min={1} max={8} value={rooms} onChange={(event) => setRooms(Number(event.target.value))} />
              </label>
            </>
          )}
          <button className={styles.submit} type="submit" disabled={isPending}>
            {isPending ? 'Checking…' : `Search ${kind === 'flight' ? 'flights' : 'stays'}`}
          </button>
        </form>
      )}

      {unavailableMessage ? (
        <p className={styles.notice} role="status">{unavailableMessage}</p>
      ) : null}
      {successMessage ? (
        <p className={styles.notice} role="status">{successMessage}</p>
      ) : null}
      {demoMessage ? (
        <div className={styles.demoNotice} role="status">
          <strong>DEVELOPMENT DEMO · NOT BOOKABLE</strong>
          <p>{demoMessage}</p>
        </div>
      ) : null}
      {demoOffers.length > 0 ? (
        <ul className={styles.demoOffers} aria-label="Demonstration offer examples">
          {demoOffers.map((offer) => (
            <li className={styles.demoOffer} key={offer.id}>
              <div className={styles.demoOfferHeading}>
                <strong>{offer.title}</strong>
                <span>Example total: {new Intl.NumberFormat(undefined, {
                  style: 'currency',
                  currency: offer.currency,
                }).format(offer.example_total)}</span>
              </div>
              <p>{offer.conditions}</p>
              <small>{offer.source} · no supplier link</small>
            </li>
          ))}
        </ul>
      ) : null}
      <p className={styles.footnote}>
        Prices and availability can change at the supplier. Booking remains external.
      </p>
    </section>
  )
}
