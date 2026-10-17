import { useEffect } from 'react'
import { CircleMarker, MapContainer, Polyline, Popup, TileLayer, useMap } from 'react-leaflet'
import { formatDateTime } from '../format'
import { RISK_COLORS } from '../risk'
import './RouteMap.css'

const US_CENTER = [39.5, -98.35]

function FitToTrip({ trip }) {
  const map = useMap()

  useEffect(() => {
    if (!trip) return
    const allPoints = trip.routes.flatMap((route) => route.points)
    map.fitBounds(allPoints, { padding: [40, 40] })
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
          <span>💨 {weather.wind_mph} mph</span>
          <span>🌧 {weather.rain_in} in/hr</span>
          <span>❄ {weather.snow_in} in/hr</span>
        </div>
      ) : (
        <div className="stop-weather">No forecast for this time yet</div>
      )}
      {risk.cause && <div className="stop-cause">Main factor: {risk.cause}</div>}
    </div>
  )
}

export default function RouteMap({ trip, selectedRouteId, onSelectRoute }) {
  const routes = trip?.routes ?? []
  const selected = routes.find((route) => route.id === selectedRouteId)

  return (
    <MapContainer center={US_CENTER} zoom={4} preferCanvas className="route-map">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <FitToTrip trip={trip} />

      {routes.map((route) => {
        const isSelected = route.id === selectedRouteId
        return (
          <Polyline
            key={`${route.id}-${isSelected}`}
            positions={route.points}
            pathOptions={{
              color: isSelected ? '#0b3b4a' : '#8fa3aa',
              weight: isSelected ? 6 : 4,
              opacity: isSelected ? 0.95 : 0.55,
            }}
            eventHandlers={{ click: () => onSelectRoute(route.id) }}
          />
        )
      })}

      {selected?.checkpoints.map((stop) => (
        <CircleMarker
          key={stop.mile}
          center={[stop.lat, stop.lon]}
          radius={6}
          pathOptions={{ color: '#ffffff', weight: 2, fillColor: RISK_COLORS[stop.risk.level], fillOpacity: 1 }}
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
            radius={10}
            pathOptions={{ color: '#ffffff', weight: 3, fillColor: index === 0 ? '#0b3b4a' : '#f5a524', fillOpacity: 1 }}
          >
            <Popup>{index === 0 ? 'Start' : 'Destination'}: {place.name}</Popup>
          </CircleMarker>
        ))}
    </MapContainer>
  )
}