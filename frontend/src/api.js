const API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/api'

async function post(path, body) {
  let response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  } catch {
    throw new Error('Could not reach the server. Is the backend running?')
  }

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(readError(data))
  }
  return data
}

function readError(data) {
  if (data.error) {
    return data.error
  }
  // DRF validation errors look like { "departure": ["Departure time must be in the future."] }
  const first = Object.values(data)[0]
  if (Array.isArray(first)) {
    return first[0]
  }
  return 'Something went wrong. Please try again.'
}

export const planTrip = (trip) => post('/trip/', trip)
export const fetchHeatmap = (request) => post('/heatmap/', request)