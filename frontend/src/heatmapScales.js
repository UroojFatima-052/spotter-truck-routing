import { RISK_COLORS, RISK_LEVELS } from './risk'

// Weather metrics use a color gradient: [value, color] stops.
// "none" (optional) = the color for values below the first stop, e.g. no rain at all.
// Risk uses the same 5 level colors as the stops and cards.
export const HEATMAP_METRICS = {
  risk: { label: 'Risk', unit: '' },
  wind: {
    label: 'Wind',
    unit: 'mph',
    stops: [
      [0, '#d4ebf8'],
      [15, '#8cc6ec'],
      [25, '#4fa3e0'],
      [35, '#2a62c9'],
      [45, '#5b2fc0'],
      [55, '#a3157a'],
    ],
  },
  rain: {
    label: 'Rain',
    unit: 'in/hr',
    none: '#b8c4c9',
    stops: [
      [0.01, '#9fd89a'],
      [0.1, '#4caf50'],
      [0.25, '#f2c12e'],
      [0.5, '#f07f1a'],
      [1, '#d7263d'],
    ],
  },
  snow: {
    label: 'Snow',
    unit: 'in/hr',
    none: '#b8c4c9',
    stops: [
      [0.01, '#c3ccff'],
      [0.5, '#8f9dff'],
      [1, '#5f6cf0'],
      [2, '#4130c9'],
      [3, '#25107a'],
    ],
  },
}

export function colorFor(metric, value) {
  if (value === null || value === undefined) return RISK_COLORS.Unknown
  if (metric === 'risk') return RISK_COLORS[RISK_LEVELS[value]]

  const { stops, none } = HEATMAP_METRICS[metric]
  if (none && value < stops[0][0]) return none
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