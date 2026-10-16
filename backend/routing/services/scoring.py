from .risk import LEVEL_NAMES


def summarize_risk(checkpoints):
    """Add up how many miles of the route fall in each risk level."""
    miles = {name: 0.0 for name in LEVEL_NAMES}
    weighted_total = 0.0
    known_miles = 0.0
    unknown_miles = 0.0

    for stop in checkpoints:
        score = stop["risk"]["score"]
        covered = stop["covers_miles"]
        if score is None:
            unknown_miles += covered
            continue
        miles[LEVEL_NAMES[score]] += covered
        weighted_total += score * covered
        known_miles += covered

    return {
        "miles_by_level": {name: round(value, 1) for name, value in miles.items()},
        "no_travel_miles": round(miles["No Travel"], 1),
        "severe_miles": round(miles["Severe"], 1),
        "high_miles": round(miles["High"], 1),
        "average_risk": round(weighted_total / known_miles, 2) if known_miles else None,
        "unknown_miles": round(unknown_miles, 1),
        "blocked": miles["No Travel"] > 0,
    }

def rank_routes(routes):
    """Best route first."""
    return sorted(routes, key=_ranking_key)


def _ranking_key(route):
    summary = route["risk_summary"]
    average = summary["average_risk"]
    return (
        summary["no_travel_miles"],
        summary["severe_miles"],
        summary["high_miles"],
        average if average is not None else float("inf"),
        route["duration_s"],
    )