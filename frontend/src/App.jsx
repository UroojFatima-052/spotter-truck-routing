import { useState } from 'react'
import { planTrip } from './api'
import RouteMap from './components/RouteMap'
import TripForm from './components/TripForm'
import RouteCards from './components/RouteCards'

export default function App() {
  const [trip, setTrip] = useState(null)
  const [selectedRouteId, setSelectedRouteId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handlePlan(request) {
    setLoading(true)
    setError('')
    try {
      const result = await planTrip(request)
      setTrip(result)
      setSelectedRouteId(result.recommended_route_id)
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

        {trip && (
          <RouteCards routes={trip.routes} selectedRouteId={selectedRouteId} onSelect={setSelectedRouteId} />
        )}
      </aside>

      <main className="map-area">
        <RouteMap trip={trip} selectedRouteId={selectedRouteId} onSelectRoute={setSelectedRouteId} />
      </main>
    </div>
  )
}