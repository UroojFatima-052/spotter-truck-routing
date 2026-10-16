from django.test import SimpleTestCase

from .services.risk import (
    HIGH, LOW, MODERATE, NO_TRAVEL, SEVERE,
    classify, rain_level, snow_level, wind_level,
)


def weather(wind=0, rain=0, snow=0):
    return {"wind_mph": wind, "rain_in": rain, "snow_in": snow}


class WindLevelTests(SimpleTestCase):
    def test_thresholds(self):
        self.assertEqual(wind_level(24.9), LOW)
        self.assertEqual(wind_level(25), MODERATE)
        self.assertEqual(wind_level(35), HIGH)
        self.assertEqual(wind_level(45), SEVERE)
        self.assertEqual(wind_level(55), NO_TRAVEL)


class RainLevelTests(SimpleTestCase):
    def test_thresholds(self):
        self.assertEqual(rain_level(0.09), LOW)
        self.assertEqual(rain_level(0.10), MODERATE)
        self.assertEqual(rain_level(0.25), HIGH)
        self.assertEqual(rain_level(0.50), SEVERE)
        self.assertEqual(rain_level(1.00), SEVERE)
        self.assertEqual(rain_level(1.01), NO_TRAVEL)


class SnowLevelTests(SimpleTestCase):
    def test_thresholds(self):
        self.assertEqual(snow_level(0.4), LOW)
        self.assertEqual(snow_level(0.5), MODERATE)
        self.assertEqual(snow_level(1.0), HIGH)
        self.assertEqual(snow_level(2.0), SEVERE)
        self.assertEqual(snow_level(3.0), SEVERE)
        self.assertEqual(snow_level(3.1), NO_TRAVEL)


class LoadRuleTests(SimpleTestCase):
    def test_55_mph_is_no_travel_for_any_load(self):
        self.assertEqual(classify(weather(wind=55), 5000)["level"], "No Travel")

    def test_45_mph_heavy_truck_is_no_travel(self):
        self.assertEqual(classify(weather(wind=50), 30001)["level"], "No Travel")

    def test_45_mph_light_truck_stays_severe(self):
        self.assertEqual(classify(weather(wind=50), 30000)["level"], "Severe")

    def test_35_mph_very_heavy_truck_is_severe(self):
        self.assertEqual(classify(weather(wind=40), 40001)["level"], "Severe")

    def test_35_mph_lighter_truck_stays_high(self):
        self.assertEqual(classify(weather(wind=40), 40000)["level"], "High")


class ClassifyTests(SimpleTestCase):
    def test_worst_condition_wins(self):
        result = classify(weather(wind=20, rain=0.3, snow=0), 10000)
        self.assertEqual(result["level"], "High")
        self.assertEqual(result["cause"], "rain")

    def test_calm_weather_is_low_with_no_cause(self):
        result = classify(weather(), 10000)
        self.assertEqual(result["level"], "Low")
        self.assertIsNone(result["cause"])

    def test_missing_weather_is_unknown(self):
        self.assertEqual(classify(None, 10000)["level"], "Unknown")

from .services.scoring import rank_routes, summarize_risk


def stop(score, miles=25):
    level = "Unknown" if score is None else ["Low", "Moderate", "High", "Severe", "No Travel"][score]
    return {"covers_miles": miles, "risk": {"level": level, "score": score, "cause": None}}


def route(route_id, scores, duration_s=3600):
    return {
        "id": route_id,
        "duration_s": duration_s,
        "risk_summary": summarize_risk([stop(score) for score in scores]),
    }


class SummarizeRiskTests(SimpleTestCase):
    def test_counts_miles_per_level(self):
        summary = summarize_risk([stop(0), stop(3), stop(3), stop(2)])
        self.assertEqual(summary["severe_miles"], 50)
        self.assertEqual(summary["high_miles"], 25)

    def test_average_is_weighted_by_miles(self):
        summary = summarize_risk([stop(0, miles=30), stop(4, miles=10)])
        self.assertEqual(summary["average_risk"], 1.0)

    def test_unknown_stops_are_left_out_of_average(self):
        summary = summarize_risk([stop(2), stop(None)])
        self.assertEqual(summary["average_risk"], 2.0)
        self.assertEqual(summary["unknown_miles"], 25)


class RankRoutesTests(SimpleTestCase):
    def best(self, routes):
        return rank_routes(routes)[0]["id"]

    def test_fewer_severe_miles_wins_even_if_slower(self):
        fast = route("fast", [3, 0], duration_s=3600)
        safe = route("safe", [0, 0], duration_s=7200)
        self.assertEqual(self.best([fast, safe]), "safe")

    def test_tie_on_severe_goes_to_fewer_high_miles(self):
        self.assertEqual(self.best([route("a", [3, 2]), route("b", [3, 1])]), "b")

    def test_tie_on_high_goes_to_lower_average(self):
        self.assertEqual(self.best([route("a", [1, 1]), route("b", [1, 0])]), "b")

    def test_full_tie_goes_to_faster_route(self):
        slow = route("slow", [0, 0], duration_s=7200)
        quick = route("quick", [0, 0], duration_s=3600)
        self.assertEqual(self.best([slow, quick]), "quick")

    def test_no_travel_ranks_below_severe(self):
        blocked = route("blocked", [4, 0])
        severe = route("severe", [3, 3])
        self.assertEqual(self.best([blocked, severe]), "severe")