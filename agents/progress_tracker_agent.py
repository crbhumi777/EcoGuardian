from typing import Dict, Any
from memory.memory_service import get_memory_service


class ProgressTrackerAgent:
    def __init__(self):
        self.memory = get_memory_service()

    async def update_and_summarize(self, session_id: str, emissions: Dict[str, Any]) -> str:
        await self.memory.append_session_emissions(session_id, emissions)
        history = await self.memory.get_history(session_id)
        return self._summarize(history)

    async def summary(self, session_id: str) -> str:
        history = await self.memory.get_history(session_id)
        return self._summarize(history)

    def _summarize(self, history):
        if not history:
            return "No previous emissions data saved yet. Start by estimating your footprint once."

        if len(history) == 1:
            return "I’ve saved your first emissions estimate. We’ll track trends as you use me more."

        last = history[-1]["total"]
        prev = history[-2]["total"]

        if prev <= 0:
            return "I’ve saved your latest emissions. Trends will improve as I get more data."

        change_pct = (last - prev) / prev * 100.0
        if change_pct < 0:
            return f"Great job! Your latest emissions are about {abs(change_pct):.1f}% lower than the previous period."
        else:
            return f"Your latest emissions are about {change_pct:.1f}% higher than before. Let's work on reducing them with the recommended actions."
