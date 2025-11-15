from typing import List, Dict
from .mcp_emissions_tool import get_emission_factor
from .electricity_tool import calculate_electricity_emissions


async def calc_travel_emissions(trips: List[Dict]) -> float:
    total = 0.0
    for t in trips:
        mode = t.get("mode", "car")
        if mode == "flight":
            key = "flight_short"
        else:
            key = mode
        ef = t.get("emission_factor")
        if ef is None:
            ef = await get_emission_factor(key)
        distance_km = t.get("distance_km", 0)
        total += distance_km * ef
    return total


async def calc_electricity_emissions(electricity_data: Dict) -> float:
    kwh = electricity_data.get("kwh", 0.0)
    region = electricity_data.get("region", "default")
    return await calculate_electricity_emissions(kwh, region)


async def calc_food_emissions(meals: List[Dict]) -> float:
    """
    meals: list of {type: "fish"|"chicken"|"veg", count: int}
    """
    total = 0.0
    for m in meals:
        t = m.get("type", "veg")
        count = m.get("count", 1)
        if t == "fish":
            key = "fish_meal"
        elif t == "chicken":
            key = "chicken_meal"
        else:
            key = "veg_meal"
        ef = await get_emission_factor(key)
        total += ef * count
    return total
