import math
from bisect import bisect_left
from datetime import datetime, timedelta, timezone

EARTH_RADIUS_MILES = 3958.8
METERS_PER_MILE = 1609.344


def build_checkpoints(route, interval_miles):
    """Place a stop every `interval_miles` along the route, with its ETA."""
    points = route["points"]
    total_miles = route["distance_m"] / METERS_PER_MILE
    cumulative = _cumulative_miles(points, total_miles)
    markers = _marker_miles(total_miles, interval_miles)
    departure = datetime.fromisoformat(route["departure_time"])

    checkpoints = []
    for i, mile in enumerate(markers):
        lat, lon = _point_at_mile(points, cumulative, mile)
        seconds = _seconds_at_mile(route, mile)
        eta = (departure + timedelta(seconds=seconds)).astimezone(timezone.utc)

        previous_mile = markers[i - 1] if i > 0 else mile
        next_mile = markers[i + 1] if i < len(markers) - 1 else mile

        checkpoints.append({
            "mile": round(mile, 1),
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "eta": eta.isoformat(),
            "covers_miles": round((next_mile - previous_mile) / 2, 2),
        })
    return checkpoints


def distance_miles(a, b):
    """Straight-line distance between two [lat, lon] points (haversine formula)."""
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    h = (
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    )
    return 2 * EARTH_RADIUS_MILES * math.asin(math.sqrt(h))


def _cumulative_miles(points, total_miles):
    """Miles driven at each point, scaled to match TomTom's total."""
    running = [0.0]
    for a, b in zip(points, points[1:]):
        running.append(running[-1] + distance_miles(a, b))

    scale = total_miles / running[-1] if running[-1] else 1
    return [miles * scale for miles in running]


def _marker_miles(total_miles, interval_miles):
    """Mile markers for stops: 0, interval, 2x interval, ..., destination."""
    markers = [0.0]
    mile = interval_miles
    while mile < total_miles:
        markers.append(mile)
        mile += interval_miles
    markers.append(total_miles)
    return markers


def _point_at_mile(points, cumulative, mile):
    """Find the exact lat/lon at a mile marker, between two route points."""
    i = bisect_left(cumulative, mile)
    if i == 0:
        return points[0]
    if i >= len(points):
        return points[-1]

    start, end = cumulative[i - 1], cumulative[i]
    share = (mile - start) / (end - start) if end > start else 0
    (lat1, lon1), (lat2, lon2) = points[i - 1], points[i]
    return lat1 + (lat2 - lat1) * share, lon1 + (lon2 - lon1) * share


def _seconds_at_mile(route, mile):
    """How many seconds after departure the truck reaches this mile."""
    table = [(0, 0)]
    table += [(step["distance_m"], step["time_s"]) for step in route["progress"]]
    table.append((route["distance_m"], route["duration_s"]))
    table.sort()

    meters = mile * METERS_PER_MILE
    distances = [row[0] for row in table]
    i = bisect_left(distances, meters)
    if i == 0:
        return 0
    if i >= len(table):
        return route["duration_s"]

    (d1, t1), (d2, t2) = table[i - 1], table[i]
    share = (meters - d1) / (d2 - d1) if d2 > d1 else 0
    return t1 + (t2 - t1) * share