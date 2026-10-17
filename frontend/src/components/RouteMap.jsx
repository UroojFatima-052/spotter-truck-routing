import { useEffect } from 'react'
import { CircleMarker, MapContainer, Polyline, Popup, TileLayer, ZoomControl, useMap } from 'react-leaflet'
import { formatDateTime } from '../format'
import { RISK_COLORS } from '../risk'
import HeatmapLayer from './HeatmapLayer'
import './RouteMap.css'

const US_CENTER = [39.5, -98.35]
const SALMON = '#ff7f70'
const SALMON_GLOW = '#ff9a8d'
const NAVY = '#4a536b'

function FitToTrip({ trip }) {
  const map = useMap()

  useEffect(() => {
    if (!trip) return
    const allPoints = trip.routes.flatMap((route) => route.points)
    // On wide screens the glass sidebar covers the left 420px, so keep routes clear of it
    const padding =
      window.innerWidth > 900
        ? { paddingTopLeft: [440, 90], paddingBottomRight: [60, 60] }
        : { padding: [24, 24] }
    map.fitBounds(allPoints, padding)
  }, [trip, map])

  return null
}

function StopDetails({ stop }) {
  const { weather, risk } = stop
  return (
    <div className="stop-popup">
      <div className="stop-head">
        <span className="stop-badge" style={{ background: RISK_COLORS[risk.level] }}>
          {risk.level}
        </span>
        <span className="stop-mile">Mile {stop.mile}</span>
      </div>
      <div className="stop-eta">Arrives {formatDateTime(stop.eta)}</div>
      {weather ? (
        <div className="stop-weather">
          <span>Wind {weather.wind_mph} mph</span>
          <span>Rain {weather.rain_in}</span>
          <span>Snow {weather.snow_in}</span>
        </div>
      ) : (
        <div className="stop-weather">No forecast for this time yet</div>
      )}
      {risk.cause && <div className="stop-cause">Main factor: {risk.cause}</div>}
    </div>
  )
}

export default function RouteMap({ trip, selectedRouteId, onSelectRoute, heatmap, hourIndex, showHeatmap, heatmapMetric }) {
  const routes = trip?.routes ?? []
  const selected = routes.find((route) => route.id === selectedRouteId)
  const others = routes.filter((route) => route.id !== selectedRouteId)

  return (
    <MapContainer center={US_CENTER} zoom={4} zoomControl={false} preferCanvas className="route-map">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <ZoomControl position="topright" />
      <FitToTrip trip={trip} />

      {heatmap && showHeatmap && <HeatmapLayer heatmap={heatmap} hourIndex={hourIndex} metric={heatmapMetric} />}

      {others.map((route) => (
        <Polyline
          key={`other-${route.id}`}
          positions={route.points}
          pathOptions={{ color: NAVY, weight: 4, opacity: 0.4 }}
          eventHandlers={{ click: () => onSelectRoute(route.id) }}
        />
      ))}

      {selected && (
        <>
          <Polyline
            key={`glow-${selected.id}`}
            positions={selected.points}
            interactive={false}
            pathOptions={{ color: SALMON_GLOW, weight: 16, opacity: 0.35 }}
          />
          <Polyline
            key={`main-${selected.id}`}
            positions={selected.points}
            pathOptions={{ color: SALMON, weight: 4.5, opacity: 1 }}
          />
        </>
      )}

      {selected?.checkpoints.map((stop) => (
        <CircleMarker
          key={stop.mile}
          center={[stop.lat, stop.lon]}
          radius={stop.risk.score ? 6.5 : 5}
          pathOptions={{ color: '#ffffff', weight: 2.5, fillColor: RISK_COLORS[stop.risk.level], fillOpacity: 1 }}
        >
          <Popup>
            <StopDetails stop={stop} />
          </Popup>
        </CircleMarker>
      ))}

      {trip &&
        [trip.origin, trip.destination].map((place, index) => (
          <CircleMarker
            key={place.name}
            center={[place.lat, place.lon]}
            radius={9}
            pathOptions={{ color: '#ffffff', weight: 3, fillColor: index === 0 ? NAVY : SALMON, fillOpacity: 1 }}
          >
            <Popup>
              {index === 0 ? 'Start' : 'Destination'}: {place.name}
            </Popup>
          </CircleMarker>
        ))}
    </MapContainer>
  )
}