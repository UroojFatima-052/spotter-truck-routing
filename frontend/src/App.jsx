import { useState } from 'react'
import { planTrip } from './api'
import TripForm from './components/TripForm'

export default function App() {
  const [trip, setTrip] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handlePlan(request) {
    setLoading(true)
    setError('')
    try {
      const result = await planTrip(request)
      setTrip(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <header className="brand">
          <div className="brand-mark">🚚</div>
          <div>
            <h1 className="brand-name">Driftline</h1>
            <p className="brand-tagline">Weather-aware truck routing</p>
          </div>
        </header>

        <TripForm onSubmit={handlePlan} loading={loading} error={error} />

        {trip && <p style={{ padding: '0 24px' }}>{trip.routes.length} routes found</p>}
      </aside>

      <main className="map-area"></main>
    </div>
  )
}