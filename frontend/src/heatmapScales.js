import { RISK_COLORS, RISK_LEVELS } from './risk'

// Weather metrics use a color gradient: [value, color] stops.
// Risk uses the same 5 level colors as the stops and cards.
export const HEATMAP_METRICS = {
  risk: { label: 'Risk', unit: '' },
  wind: {
    label: 'Wind',
    unit: 'mph',
    stops: [
      [0, '#eef7fc'],
      [15, '#9fd0ef'],
      [25, '#4fa3e0'],
      [35, '#2a62c9'],
      [45, '#5b2fc0'],
      [55, '#a3157a'],
    ],
  },
  rain: {
    label: 'Rain',
    unit: 'in/hr',
    stops: [
      [0, '#f1f8ee'],
      [0.1, '#7ccf6e'],
      [0.25, '#f2d13a'],
      [0.5, '#f08a24'],
      [1, '#d7263d'],
    ],
  },
  snow: {
    label: 'Snow',
    unit: 'in/hr',
    stops: [
      [0, '#f3f4ff'],
      [0.5, '#a9b8ff'],
      [1, '#6f7ff0'],
      [2, '#4b3fd1'],
      [3, '#2a1580'],
    ],
  },
}

export function colorFor(metric, value) {
  if (value === null || value === undefined) return RISK_COLORS.Unknown
  if (metric === 'risk') return RISK_COLORS[RISK_LEVELS[value]]

  const { stops } = HEATMAP_METRICS[metric]
  if (value <= stops[0][0]) return stops[0][1]

  for (let i = 1; i < stops.length; i++) {
    const [lowValue, lowColor] = stops[i - 1]
    const [highValue, highColor] = stops[i]
    if (value <= highValue) {
      return mixColors(lowColor, highColor, (value - lowValue) / (highValue - lowValue))
    }
  }
  return stops[stops.length - 1][1]
}

// Blend two hex colors. share = 0 gives colorA, 1 gives colorB.
function mixColors(colorA, colorB, share) {
  const a = hexToRgb(colorA)
  const b = hexToRgb(colorB)
  const mixed = a.map((channel, i) => Math.round(channel + (b[i] - channel) * share))
  return `rgb(${mixed.join(', ')})`
}

function hexToRgb(hex) {
  const number = parseInt(hex.slice(1), 16)
  return [(number >> 16) & 255, (number >> 8) & 255, number & 255]
}