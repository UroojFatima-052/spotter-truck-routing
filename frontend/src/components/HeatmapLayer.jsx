import { Pane, Rectangle } from 'react-leaflet'
import { colorFor } from '../heatmapScales'

export default function HeatmapLayer({ heatmap, hourIndex, metric }) {
  const half = heatmap.cell_size / 2
  const valuesThisHour = heatmap[metric][hourIndex]

  return (
    <Pane name="heatmap" style={{ zIndex: 350 }}>
      {heatmap.cells.map(([lat, lon], i) => (
        <Rectangle
          key={i}
          bounds={[
            [lat - half, lon - half],
            [lat + half, lon + half],
          ]}
          interactive={false}
          pathOptions={{
            color: '#ffffff',
            weight: 1,
            opacity: 0.7,
            fillColor: colorFor(metric, valuesThisHour[i]),
            fillOpacity: 0.5,
          }}
        />
      ))}
    </Pane>
  )
}