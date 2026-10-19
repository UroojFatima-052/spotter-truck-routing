# Driftline

Weather-aware truck routing. Enter a trip, departure time and load weight, and Driftline compares 3 truck routes by forecast weather risk at the time the truck will actually reach each part of the road, then recommends the safest one.

**Live app:** https://driftline-truck.netlify.app
**API health check:** https://spotter-truck-routing-eva2.onrender.com/api/health/
**Walkthrough video:** [Loom link]

> The backend runs on Render's free tier. If the first request is slow, the server may be waking up; give it a few seconds.

## Features

- 3 alternative truck routes with load weight considered
- Weather checkpoints every 10, 25 or 50 miles, each with its own ETA
- Weather pulled for each checkpoint at its ETA hour, not current weather
- Risk per checkpoint (Low, Moderate, High, Severe, No Travel) using the wind, rain and snow table plus the load rules
- Route summaries: drive time, distance, arrival, risk breakdown, Severe and High miles, average risk
- Recommended route with the reason it won
- Weather heatmap around the trip corridor with a 0 to 48 hour slider and Risk, Wind, Rain and Snow layers

## Tech stack

| Part | Choice | Why |
|---|---|---|
| Backend | Django + Django REST Framework | Required stack |
| Frontend | React (Vite) + react-leaflet | Required stack; Leaflet is free and fast with canvas rendering |
| Routing and geocoding | TomTom APIs | Truck mode with vehicle weight, and alternative routes on long trips |
| Weather | Open-Meteo | Free, no key, hourly forecasts in mph and inches, many locations per request |
| Hosting | Render (API), Netlify (frontend) | Free tiers, deploy from GitHub |

## How it works

1. **Geocode** origin and destination with TomTom (US only, since the brief uses miles, mph and pounds).
2. **Routes:** ask TomTom for truck routes with the load weight (converted to kg). If fewer than 3 come back, add the shortest route, then the eco route, then a forced detour through a point beside the main route. Routes within 1% of each other in length are treated as duplicates.
3. **Checkpoints:** walk along each route's geometry and drop a checkpoint every N miles, plus start and destination. Each checkpoint covers half the distance to its neighbours, so all checkpoints add up to the full route length.
4. **ETA:** TomTom's guidance gives distance and elapsed time at many points along the route. The ETA at a checkpoint is interpolated between the two nearest ones and added to the departure time.
5. **Weather:** one batched Open-Meteo request for all checkpoints, then pick the forecast hour closest to each checkpoint's ETA.
6. **Risk:** each of wind, rain and snow gets a level from the table; load rules adjust the wind level; the checkpoint takes the worst of the three.
7. **Scoring and recommendation** (see below).
8. **Heatmap:** a grid of cells around all three routes (cells farther than 60 miles from any route are dropped, max 200 cells), with every hour from departure to +48h fetched in one go. The slider only switches which hour is drawn, so it is instant.

## Risk rules

| Condition | Low | Moderate | High | Severe | No Travel |
|---|---|---|---|---|---|
| Wind (mph) | under 25 | 25 to 34 | 35 to 44 | 45 to 54 | 55+ |
| Rain (in/hr) | under 0.10 | 0.10 to 0.25 | 0.25 to 0.50 | 0.50 to 1.00 | over 1.00 |
| Snow (in/hr) | under 0.5 | 0.5 to 1.0 | 1.0 to 2.0 | 2.0 to 3.0 | over 3.0 |

Load rules:
- Wind 55+ mph is No Travel for any load
- Wind 45 to 54 mph with load over 30,000 lb is No Travel
- Wind 35 to 44 mph with load over 40,000 lb is Severe

## Recommendation

Routes are sorted by these keys in order, each used only to break a tie in the previous one:

1. Fewest No Travel miles
2. Fewest Severe miles
3. Fewest High miles
4. Lowest average risk (mile-weighted, Low = 0 to No Travel = 4)
5. Shortest travel time

## Assumptions and decisions

- **No Travel ranks below Severe.** Any route crossing a No Travel zone is ranked after routes that do not, and is flagged in the UI.
- **Table edges:** where two levels share a boundary (for example rain exactly 0.25), the higher level wins. Top levels use "over", so rain of exactly 1.00 in/hr stays Severe.
- **Rain** is Open-Meteo's `rain` plus `showers`.
- **Forecast window:** Open-Meteo forecasts cover 7 days, so departures are limited to the next 5 days, leaving room for the trip and the 48 hour heatmap. Checkpoints with no forecast are shown as Unknown and left out of the average.
- **Weather locations are snapped to a ~7 mile grid** so nearby checkpoints share one forecast. This keeps requests within Open-Meteo's free limits and is close to the weather model's own resolution.
- **Same origin and destination** (including different spellings of the same place) are rejected.
- Weather responses are cached for 30 minutes.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health/` | Health check |
| GET | `/api/geocode/?q=Dallas, TX` | Place name to coordinates |
| POST | `/api/trip/` | Routes, checkpoints, weather, risk and recommendation |
| POST | `/api/heatmap/` | 0 to 48 hour weather and risk grid around given points |

Example trip request:
```json
{
  "origin": "Dallas, TX",
  "destination": "Denver, CO",
  "departure": "2026-10-20T12:00:00Z",
  "weight_lb": 35000,
  "interval_miles": 25
}
```

## Project structure

```
backend/
  config/                Django settings and URLs
  routing/
    services/
      tomtom.py          Geocoding and truck routes
      checkpoints.py     Checkpoints and ETAs along a route
      weather.py         Open-Meteo forecasts, batching, caching, retries
      risk.py            Weather and load risk rules
      scoring.py         Route risk summary and ranking
      trip.py            Runs the whole trip pipeline
      heatmap.py         0 to 48 hour grid around the trip
    serializers.py       Request validation
    views.py             API endpoints
    tests.py             Tests for risk rules, ranking and validation
frontend/
  src/
    api.js               Calls to the backend
    components/          Trip form, map, route cards, heatmap layer and controls
```

## Run locally

**Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
```
Create `backend/.env`:
```
TOMTOM_API_KEY=your_tomtom_key
```
Then:
```bash
python manage.py migrate
python manage.py runserver
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173. The frontend calls `http://127.0.0.1:8000/api` unless `VITE_API_URL` is set.

**Tests**
```bash
cd backend
python manage.py test routing
```

## Environment variables (production)

| Variable | Where | Example |
|---|---|---|
| `TOMTOM_API_KEY` | Backend | your key |
| `DJANGO_SECRET_KEY` | Backend | long random string |
| `DJANGO_DEBUG` | Backend | `False` |
| `DJANGO_ALLOWED_HOSTS` | Backend | `.onrender.com` |
| `CORS_ALLOWED_ORIGINS` | Backend | `https://driftline-truck.netlify.app` |
| `VITE_API_URL` | Frontend | `https://your-api.onrender.com/api` |

## Limitations

- US routes only.
- Open-Meteo's free API limits requests per IP address. On shared free hosting this can occasionally return a "service unavailable" message; the backend retries before giving up.
- The layout is built for desktop; on phones it stacks but is not fully optimised.