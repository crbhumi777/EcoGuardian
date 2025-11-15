from typing import Dict, Any, List
import re

from tools.mcp_emissions_tool import get_travel_distance, get_emission_factor, get_electricity_mix


class DataFetcherAgent:
    """
    DataFetcherAgent

    For robustness, this implementation uses a simple rule-based parser on the user text
    to extract:

    - number of flights
    - car distance in km
    - electricity usage in kWh
    - meat consumption frequency

    """

    async def fetch(self, session_id: str, user_input: str) -> Dict[str, Any]:
        parsed = self._parse_activities_rule_based(user_input)

        enriched: Dict[str, Any] = {}

        # ----- TRAVEL -----
        trips = parsed.get("trips", [])
        enriched_trips: List[Dict] = []
        for t in trips:
            # For now, we just fake origin/destination labels; our distance stub uses string length anyway.
            origin = t.get("origin", "CityA")
            destination = t.get("destination", "CityB")

            distance_km = await get_travel_distance(origin, destination)
            mode = t.get("mode", "car")
            ef = await get_emission_factor("flight_short" if mode == "flight" else mode)

            enriched_trips.append(
                {
                    "mode": mode,
                    "origin": origin,
                    "destination": destination,
                    "distance_km": distance_km,
                    "emission_factor": ef,
                }
            )

        if enriched_trips:
            enriched["travel"] = enriched_trips

        # ----- ELECTRICITY -----
        if "electricity_kwh" in parsed and "region" in parsed:
            mix = await get_electricity_mix(parsed["region"])
            enriched["electricity"] = {
                "kwh": parsed["electricity_kwh"],
                "region": parsed["region"],
                "mix": mix,
            }

        # ----- FOOD -----
        if "meals" in parsed:
            enriched["food"] = parsed["meals"]

        return enriched

    # ------------------------------------------------------------------ #
    # Simple rule-based parser
    # ------------------------------------------------------------------ #
    def _parse_activities_rule_based(self, text: str) -> Dict[str, Any]:
        """
        Extract a minimal structured representation from free text.

        Examples it should handle:
        - "I took 3 domestic flights"
        - "drove 200 km by car"
        - "used about 150 kWh of electricity"
        - "I eat meat 3 times a week"
        """
        text_lower = text.lower()
        result: Dict[str, Any] = {}

        # ---- Flights ----
        flights_match = re.search(r"(\d+)\s+(?:domestic\s+)?flights?", text_lower)
        trips: List[Dict[str, Any]] = []
        if flights_match:
            num_flights = int(flights_match.group(1))
            for _ in range(num_flights):
                trips.append(
                    {
                        "mode": "flight",
                        "origin": "domestic_city_a",
                        "destination": "domestic_city_b",
                    }
                )

        # ---- Car distance ----
        # Look for "drove 200 km" or "drive 200 km"
        car_match = re.search(
            r"(drove|drive|driven)[^\d]*(\d+)\s*km", text_lower
        )
        if car_match:
            distance_km = float(car_match.group(2))
            trips.append(
                {
                    "mode": "car",
                    "origin": "local_area_a",
                    "destination": "local_area_b",
                    "distance_km": distance_km,  # we will still override with get_travel_distance stub
                }
            )

        if trips:
            result["trips"] = trips

        # ---- Electricity usage ----
        elec_match = re.search(r"(\d+)\s*(kwh|kwh|kilowatt[- ]hours?)", text_lower)
        if elec_match:
            kwh = float(elec_match.group(1))
            result["electricity_kwh"] = kwh

        # Region – very rough guess; for demo, assume "in" (India) if not found
        region_match = re.search(r"in\s+([a-zA-Z]+)", text_lower)
        if region_match:
            region = region_match.group(1)
        else:
            region = "IN"  # default region
        result["region"] = region

        # ---- Meat consumption ----
        # e.g. "I eat meat 3 times a week"
        meat_match = re.search(r"meat\s+(\d+)\s+times\s+a\s+week", text_lower)
        meals = []
        if meat_match:
            times_per_week = int(meat_match.group(1))
            # approximate to monthly meals
            times_per_month = times_per_week * 4
            meals.append({"type": "fish", "count": times_per_month})

        if meals:
            result["meals"] = meals

        return result
