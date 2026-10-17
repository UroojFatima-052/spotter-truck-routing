import { useRef, useState } from 'react'
import { fetchHeatmap, planTrip } from './api'
import RouteCards from './components/RouteCards'
import RouteMap from './components/RouteMap'
import TripForm from './components/TripForm'
import HeatmapControls from './components/HeatmapControls'

export default function App() {
  const [trip, setTrip] = useState(null)
  const [selectedRouteId, setSelectedRouteId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [heatmap, setHeatmap] = useState(null)
  const [heatmapLoading, setHeatmapLoading] = useState(false)
  const [heatmapError, setHeatmapError] = useState('')
  const [hourIndex, setHourIndex] = useState(0)
  const [showHeatmap, setShowHeatmap] = useState(true)
  const [heatmapMetric, setHeatmapMetric] = useState('risk')
  const latestHeatmapRequest = useRef(0)

  async function loadHeatmap(result) {
    const requestId = ++latestHeatmapRequest.current
    setHeatmap(null)
    setHourIndex(0)
    setHeatmapError('')
    setHeatmapLoading(true)

    try {
      const points = result.routes.flatMap((route) => route.checkpoints.map((stop) => [stop.lat, stop.lon]))
      const data = await fetchHeatmap({ points, departure: result.departure, weight_lb: result.weight_lb })
      if (requestId === latestHeatmapRequest.current) {
        setHeatmap(data)
      }
    } catch (err) {
      if (requestId === latestHeatmapRequest.current) {
        setHeatmapError(err.message)
      }
    } finally {
      if (requestId === latestHeatmapRequest.current) {
        setHeatmapLoading(false)
      }
    }
  }

  async function handlePlan(request) {
    setLoading(true)
    setError('')
    try {
      const result = await planTrip(request)
      setTrip(result)
      setSelectedRouteId(result.recommended_route_id)
      loadHeatmap(result)
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
        <RouteMap
          trip={trip}
          selectedRouteId={selectedRouteId}
          onSelectRoute={setSelectedRouteId}
          heatmap={heatmap}
          hourIndex={hourIndex}
          showHeatmap={showHeatmap}
          heatmapMetric={heatmapMetric}
        />
        <HeatmapControls
          heatmap={heatmap}
          loading={heatmapLoading}
          error={heatmapError}
          hourIndex={hourIndex}
          onHourChange={setHourIndex}
          metric={heatmapMetric}
          onMetricChange={setHeatmapMetric}
          visible={showHeatmap}
          onToggle={setShowHeatmap}
        />
      </main>
    </div>
  )
}