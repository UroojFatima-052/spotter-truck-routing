import { Pane, Rectangle } from 'react-leaflet'
import { RISK_COLORS, RISK_LEVELS } from '../risk'

export default function HeatmapLayer({ heatmap, hourIndex }) {
  const half = heatmap.cell_size / 2
  const riskThisHour = heatmap.risk[hourIndex]

  return (
    <Pane name="heatmap" style={{ zIndex: 350 }}>
      {heatmap.cells.map(([lat, lon], i) => {
        const score = riskThisHour[i]
        const level = score === null ? 'Unknown' : RISK_LEVELS[score]
        return (
          <Rectangle
            key={i}
            bounds={[
              [lat - half, lon - half],
              [lat + half, lon + half],
            ]}
            interactive={false}
            pathOptions={{
              stroke: false,
              fillColor: RISK_COLORS[level],
              fillOpacity: score ? 0.45 : 0.12,
            }}
          />
        )
      })}
    </Pane>
  )
}