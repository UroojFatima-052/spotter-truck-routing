import { formatDateTime, formatDuration } from '../format'
import { RISK_COLORS, RISK_LEVELS } from '../risk'
import './RouteCards.css'

const LETTERS = ['A', 'B', 'C']

// Same order the backend ranks by
const RANKING_REASONS = [
  ['no_travel_miles', 'Avoids No Travel zones'],
  ['severe_miles', 'Fewest Severe miles'],
  ['high_miles', 'Fewest High miles'],
  ['average_risk', 'Lowest overall risk'],
]

function recommendationReason(routes) {
  const [best, runnerUp] = routes
  if (!runnerUp) return 'Only route available'

  for (const [key, label] of RANKING_REASONS) {
    const bestValue = best.risk_summary[key] ?? Infinity
    const otherValue = runnerUp.risk_summary[key] ?? Infinity
    if (bestValue < otherValue) return label
  }
  return 'Fastest of the equally safe routes'
}

function RiskBar({ summary }) {
  const total =
    Object.values(summary.miles_by_level).reduce((sum, miles) => sum + miles, 0) + summary.unknown_miles

  return (
    <div className="risk-bar">
      {RISK_LEVELS.map((level) => {
        const miles = summary.miles_by_level[level]
        if (!miles) return null
        return (
          <span
            key={level}
            style={{ width: `${(miles / total) * 100}%`, background: RISK_COLORS[level] }}
            title={`${level}: ${miles} mi`}
          />
        )
      })}
      {summary.unknown_miles > 0 && (
        <span
          style={{ width: `${(summary.unknown_miles / total) * 100}%`, background: RISK_COLORS.Unknown }}
          title={`No forecast yet: ${summary.unknown_miles} mi`}
        />
      )}
    </div>
  )
}

export default function RouteCards({ routes, selectedRouteId, onSelect }) {
  return (
    <section className="route-cards">
      <div className="cards-header">
        <h2>Routes</h2>
        <p>
          Route A recommended: <strong>{recommendationReason(routes)}</strong>
        </p>
      </div>

      {routes.map((route, index) => {
        const summary = route.risk_summary
        const isSelected = route.id === selectedRouteId

        return (
          <button
            key={route.id}
            type="button"
            className={`route-card ${isSelected ? 'selected' : ''}`}
            onClick={() => onSelect(route.id)}
          >
            <div className="card-top">
              <span className="route-name">Route {LETTERS[index]}</span>
              {route.recommended && <span className="badge recommended">Recommended</span>}
              {summary.blocked && <span className="badge blocked">Crosses No Travel zone</span>}
            </div>

            <div className="stats">
              <div>
                <span className="stat-value">{formatDuration(route.duration_s)}</span>
                <span className="stat-label">Drive time</span>
              </div>
              <div>
                <span className="stat-value">{route.distance_miles} mi</span>
                <span className="stat-label">Distance</span>
              </div>
              <div>
                <span className="stat-value">{formatDateTime(route.arrival_time)}</span>
                <span className="stat-label">Arrives</span>
              </div>
            </div>

            <RiskBar summary={summary} />

            <div className="risk-figures">
              <span>Severe: {summary.severe_miles} mi</span>
              <span>High: {summary.high_miles} mi</span>
              <span>Avg risk: {summary.average_risk ?? 'n/a'} / 4</span>
            </div>

            {summary.unknown_miles > 0 && (
              <p className="note">{summary.unknown_miles} mi are beyond the forecast range</p>
            )}
          </button>
        )
      })}
    </section>
  )
}