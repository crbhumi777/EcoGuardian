"""
This is a simple 'recommend alternative' tool.
In a real project, we'd call an API or use Google Search.
"""

from typing import List, Dict


async def suggest_greener_alternatives(product_name: str) -> List[Dict]:
    mapping = {
        "car": ["public transit", "bike", "carpool"],
        "fish": ["chicken", "tofu", "lentils"],
        "ac": ["fan", "energy-efficient AC", "smart thermostat"],
    }
    for key, options in mapping.items():
        if key in product_name.lower():
            return [{"original": product_name, "alternative": o} for o in options]

    # Fallback generic
    return [
        {"original": product_name, "alternative": "lower-impact alternative"},
    ]
