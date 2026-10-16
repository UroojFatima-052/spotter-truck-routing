LOW, MODERATE, HIGH, SEVERE, NO_TRAVEL = 0, 1, 2, 3, 4
LEVEL_NAMES = ["Low", "Moderate", "High", "Severe", "No Travel"]


def wind_level(mph):
    if mph >= 55:
        return NO_TRAVEL
    if mph >= 45:
        return SEVERE
    if mph >= 35:
        return HIGH
    if mph >= 25:
        return MODERATE
    return LOW


def rain_level(inches_per_hour):
    if inches_per_hour > 1.0:
        return NO_TRAVEL
    if inches_per_hour >= 0.5:
        return SEVERE
    if inches_per_hour >= 0.25:
        return HIGH
    if inches_per_hour >= 0.10:
        return MODERATE
    return LOW


def snow_level(inches_per_hour):
    if inches_per_hour > 3.0:
        return NO_TRAVEL
    if inches_per_hour >= 2.0:
        return SEVERE
    if inches_per_hour >= 1.0:
        return HIGH
    if inches_per_hour >= 0.5:
        return MODERATE
    return LOW


def apply_load_rules(wind_mph, weight_lb, level):
    """Heavy trucks are more dangerous in strong wind."""
    if 45 <= wind_mph < 55 and weight_lb > 30000:
        return NO_TRAVEL
    if 35 <= wind_mph < 45 and weight_lb > 40000:
        return max(level, SEVERE)
    return level


def classify(weather, weight_lb):
    """Risk level for one stop: the worst of wind, rain and snow."""
    if weather is None:
        return {"level": "Unknown", "score": None, "cause": None}

    levels = {
        "wind": apply_load_rules(weather["wind_mph"], weight_lb, wind_level(weather["wind_mph"])),
        "rain": rain_level(weather["rain_in"]),
        "snow": snow_level(weather["snow_in"]),
    }
    cause = max(levels, key=levels.get)
    score = levels[cause]

    return {
        "level": LEVEL_NAMES[score],
        "score": score,
        "cause": cause if score > LOW else None,
    }