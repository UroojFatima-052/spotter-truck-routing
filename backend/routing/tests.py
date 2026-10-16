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