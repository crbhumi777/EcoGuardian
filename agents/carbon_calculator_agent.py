from typing import Dict, Any
from tools.carbon_calculation_tools import (
    calc_travel_emissions,
    calc_electricity_emissions,
    calc_food_emissions,
)


class CarbonCalculatorAgent:
    async def calculate(self, session_id: str, activity_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Run parallel-ish calculations.
        """
        travel_data = activity_data.get("travel", [])
        electricity_data = activity_data.get("electricity")
        food_data = activity_data.get("food", [])

        travel_em = await calc_travel_emissions(travel_data) if travel_data else 0.0
        elec_em = await calc_electricity_emissions(electricity_data) if electricity_data else 0.0
        food_em = await calc_food_emissions(food_data) if food_data else 0.0

        by_category = {
            "travel": travel_em,
            "electricity": elec_em,
            "food": food_em,
        }
        total = sum(by_category.values())
        return {"total": total, "by_category": by_category}
