from typing import Dict
from .mcp_emissions_tool import get_emission_factor, get_electricity_mix


async def get_electricity_emission_factor(region: str) -> float:
    """
    Compute an effective emission factor for 1 kWh in the given region
    using the (sample) electricity mix.
    """
    mix: Dict[str, float] = await get_electricity_mix(region)
    coal_factor = 0.9
    gas_factor = 0.5
    renewables_factor = 0.05

    return (
            mix.get("coal", 0) * coal_factor
            + mix.get("gas", 0) * gas_factor
            + mix.get("renewables", 0) * renewables_factor
    )


async def calculate_electricity_emissions(kwh: float, region: str) -> float:
    ef = await get_electricity_emission_factor(region)
    return kwh * ef
