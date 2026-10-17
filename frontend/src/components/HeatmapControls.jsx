import { formatDateTime } from '../format'
import { HEATMAP_METRICS } from '../heatmapScales'
import { RISK_COLORS, RISK_LEVELS } from '../risk'
import './HeatmapControls.css'

function Legend({ metric }) {
  if (metric === 'risk') {
    return (
      <div className="legend-levels">
        {RISK_LEVELS.map((level) => (
          <span key={level}>
            <i style={{ background: RISK_COLORS[level] }} />
            {level}
          </span>
        ))}
      </div>
    )
  }

  const { stops, unit, none } = HEATMAP_METRICS[metric]
  const gradient = `linear-gradient(to right, ${stops.map(([, color]) => color).join(', ')})`

  return (
    <div className="legend-scale">
      <div className="legend-row">
        {none && (
          <span className="legend-none">
            <i style={{ background: none }} />
            None
          </span>
        )}
        <div className="legend-bar" style={{ background: gradient }} />
      </div>
      <div className="legend-labels">
        {stops.map(([value]) => (
          <span key={value}>{value}</span>
        ))}
      </div>
      <span className="legend-unit">{unit}</span>
    </div>
  )
}

export default function HeatmapControls({
  heatmap,
  loading,
  error,
  hourIndex,
  onHourChange,
  metric,
  onMetricChange,
  visible,
  onToggle,
}) {
  if (!loading && !error && !heatmap) return null

  return (
    <div className="heatmap-controls">
      <div className="hc-top">
        <span className="hc-title">Weather forecast</span>
        <label className="hc-toggle">
          <input type="checkbox" checked={visible} onChange={(e) => onToggle(e.target.checked)} />
          Show
        </label>
      </div>

      {loading && <p className="hc-status">Loading 48-hour forecast…</p>}
      {error && <p className="hc-status error">{error}</p>}

      {heatmap && (
        <>
          <div className="hc-metrics">
            {Object.entries(HEATMAP_METRICS).map(([key, { label }]) => (
              <button
                key={key}
                type="button"
                className={key === metric ? 'active' : ''}
                onClick={() => onMetricChange(key)}
              >
                {label}
              </button>
            ))}
          </div>

          <div className="hc-time">
            <strong>{hourIndex === 0 ? 'Departure' : `+${hourIndex}h`}</strong>
            <span>{formatDateTime(heatmap.hours[hourIndex])}</span>
          </div>

          <input
            type="range"
            className="hc-slider"
            min="0"
            max={heatmap.hours.length - 1}
            value={hourIndex}
            onChange={(e) => onHourChange(Number(e.target.value))}
          />
          <div className="hc-ticks">
            <span>0h</span>
            <span>12h</span>
            <span>24h</span>
            <span>36h</span>
            <span>48h</span>
          </div>

          <Legend metric={metric} />
        </>
      )}
    </div>
  )
}