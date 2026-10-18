import { useState } from 'react'
import './TripForm.css'

const INTERVALS = [10, 25, 50]
const MAX_DAYS_AHEAD = 5

function toLocalInput(date) {
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function nextHourLocal() {
  const date = new Date()
  date.setHours(date.getHours() + 1, 0, 0, 0)
  return toLocalInput(date)
}

function latestDepartureLocal() {
  const date = new Date()
  date.setDate(date.getDate() + MAX_DAYS_AHEAD)
  return toLocalInput(date)
}

function weightHint(weight) {
  if (weight > 40000) return 'Heavy load: 35+ mph wind counts as Severe, 45+ mph is No Travel'
  if (weight > 30000) return 'Mid-heavy load: 45+ mph wind is No Travel'
  return 'Standard wind limits apply'
}

export default function TripForm({ onSubmit, loading, error }) {
  const [origin, setOrigin] = useState('Dallas, TX')
  const [destination, setDestination] = useState('Denver, CO')
  const [departure, setDeparture] = useState(nextHourLocal)
  const [weight, setWeight] = useState(35000)
  const [intervalMiles, setIntervalMiles] = useState(25)

  function swapPlaces() {
    setOrigin(destination)
    setDestination(origin)
  }

  function handleSubmit(event) {
    event.preventDefault()
    onSubmit({
      origin: origin.trim(),
      destination: destination.trim(),
      departure: new Date(departure).toISOString(),
      weight_lb: Number(weight),
      interval_miles: intervalMiles,
    })
  }

  return (
    <form className="trip-form" onSubmit={handleSubmit}>
      <div className="places">
        <label className="field">
          <span className="field-label">From</span>
          <input value={origin} onChange={(e) => setOrigin(e.target.value)} placeholder="City, State" required />
        </label>

        <button type="button" className="swap" onClick={swapPlaces} aria-label="Swap origin and destination">
          ⇅
        </button>

        <label className="field">
          <span className="field-label">To</span>
          <input
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            placeholder="City, State"
            required
          />
        </label>
      </div>

      <div className="row">
        <label className="field">
          <span className="field-label">Departure</span>
          <input
            type="datetime-local"
            value={departure}
            min={toLocalInput(new Date())}
            max={latestDepartureLocal()}
            onChange={(e) => setDeparture(e.target.value)}
            required
          />
        </label>

        <label className="field">
          <span className="field-label">Load weight</span>
          <div className="with-unit">
            <input
              type="number"
              min="1"
              max="200000"
              step="500"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              required
            />
            <span className="unit">lb</span>
          </div>
        </label>
      </div>
      <p className="hint">{weightHint(Number(weight))}</p>

      <div className="field">
        <span className="field-label">Check weather every</span>
        <div className="segmented">
          {INTERVALS.map((miles) => (
            <button
              key={miles}
              type="button"
              className={miles === intervalMiles ? 'active' : ''}
              onClick={() => setIntervalMiles(miles)}
            >
              {miles} mi
            </button>
          ))}
        </div>
      </div>

      {error && <div className="form-error">{error}</div>}

      <button type="submit" className="submit" disabled={loading}>
        {loading ? 'Checking routes and weather…' : 'Find safest route'}
      </button>
    </form>
  )
}