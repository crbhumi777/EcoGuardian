from typing import Dict, Any, List
from config import get_gemini_model


class RecommendationAgent:
    def __init__(self):
        self.model = get_gemini_model()

    async def recommend(self, session_id: str, emissions: Dict[str, Any]) -> Dict[str, List[str]]:
        prompt = (
            "You are a sustainability coach.\n"
            "Given this emissions breakdown, produce 5 practical, high-impact "
            "recommendations for reducing emissions. "
            "Be concise, numbered, and specific.\n\n"
            f"Emissions data:\n{emissions}"
        )
        result = await self.model.generate_content_async(prompt)
        text = result.text or ""
        actions = self._extract_bullets(text)
        return {"actions": actions[:5]}

    def _extract_bullets(self, text: str) -> List[str]:
        lines = [l.strip(" -") for l in text.splitlines() if l.strip()]
        # keep lines that look like bullet/numbered
        out = []
        for line in lines:
            if line[0].isdigit() or line.startswith("-"):
                out.append(line.lstrip("0123456789.-) ").strip())
            else:
                out.append(line)
        return out
