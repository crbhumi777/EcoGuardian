"""
MCP-like tools for:
- getting emission factors
- travel distance

Here we just hardcoded some sample values for demo.
"""

from typing import Dict


async def get_emission_factor(activity_type: str) -> float:
    """
    Approximate emission factors in kg CO2e per unit.
    In a real system, will fetch from an API via MCP.
    """
    table = {
        "flight_short": 0.15,  # kg CO2e per km
        "car": 0.18,
        "train": 0.04,
        "bus": 0.08,
        "electricity_kwh": 0.4,  # fallback
        "fish_meal": 7.0,
        "chicken_meal": 2.0,
        "veg_meal": 1.0,
    }
    return table.get(activity_type, 0.1)


async def get_travel_distance(origin: str, destination: str) -> float:
    """
    Stub: in a real setup, this would call Maps API (via MCP).
    Here we just return a dummy distance.
    """
    # Completely fake: just length difference * constant
    pseudo = abs(len(origin) - len(destination)) * 20
    return max(pseudo, 100.0)  # never less than 100 km for demo


async def get_electricity_mix(region: str) -> Dict[str, float]:
    """
    Sample electricity mix. Real version would call an API.
    """
    if region.lower() in ["eu", "europe"]:
        return {"coal": 0.2, "gas": 0.3, "renewables": 0.5}
    if region.lower() in ["us", "usa"]:
        return {"coal": 0.3, "gas": 0.4, "renewables": 0.3}
    return {"coal": 0.5, "gas": 0.3, "renewables": 0.2}
