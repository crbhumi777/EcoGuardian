from typing import Dict, Any, Optional

from memory.memory_service import get_memory_service
from observability.logging_config import logger
from observability.metrics import metrics
from config import get_gemini_model


class OrchestratorAgent:
    def __init__(self, runtime: "AgentRuntime"):
        self.runtime = runtime
        self.memory = get_memory_service()
        self.model = get_gemini_model()

    async def handle_request(self, session_id: str, user_input: str) -> str:
        """
        Main entry point from the UI.

        Flow:
        - Log + count request
        - Save user message in session history
        - Load any stored user profile
        - Classify intent (calculate emissions / view progress / tips only)
        - Route to appropriate agents
        """
        logger.info("Orchestrator received input: %s", user_input)
        metrics.inc("requests_total")

        # Store user message in conversation history
        await self.memory.append_session_message(session_id, "user", user_input)

        # Load any profile / context we may have stored
        user_profile = await self.memory.load_user_profile(session_id)

        # Figure out what the user wants
        intent = await self._classify_intent(user_input, user_profile)

        # --- Intent: view progress ---
        if intent == "view_progress":
            msg = (
                "Here’s how I handle your progress 📈:\n\n"
                "- Every time you ask me to estimate your footprint, I store that run.\n"
                "- The **Trends & Insights** view in the UI visualizes your history over time.\n\n"
                "Right now, I don’t have a separate text-only progress summary agent wired in this runtime, "
                "but you can:\n\n"
                "- Ask something like *“Estimate my footprint for this month”* to add a new run, then\n"
                "- Open the **Trends & Insights** tab to compare runs.\n"
            )
            await self.memory.append_session_message(session_id, "assistant", msg)
            return msg

        # --- Consent gating for very sensitive inputs ---
        if self._needs_sensitive_confirmation(user_input):
            await self.memory.save_pending_request(session_id, user_input)
            msg = (
                "To estimate your emissions I’ll need to use some personal details "
                "you shared (like location or lifestyle). "
                "Do you consent to proceed? (yes/no)"
            )
            await self.memory.append_session_message(session_id, "assistant", msg)
            return msg

        # --- Default / main flow ---
        # Full flow: fetch data → calculate → recommend → update progress
        enriched = await self.runtime.data_fetcher_agent.fetch(session_id, user_input)
        emissions = await self.runtime.carbon_calculator_agent.calculate(
            session_id, enriched
        )
        recs = await self.runtime.recommendation_agent.recommend(
            session_id, emissions
        )
        trend = await self.runtime.progress_tracker_agent.update_and_summarize(
            session_id, emissions
        )

        response = self._format_response(emissions, recs, trend)
        await self.memory.append_session_message(session_id, "assistant", response)
        return response

    async def _classify_intent(
            self,
            user_input: str,
            user_profile: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Extremely simple intent classifier using Gemini.

        Returns one of:
        - 'calculate_emissions'
        - 'view_progress'
        - 'tips_only'
        (We treat unknowns as 'calculate_emissions' by default.)
        """
        prompt = (
            "You are an intent classifier for a sustainability assistant.\n"
            "User message:\n"
            f"{user_input}\n\n"
            "Answer with exactly one label: [calculate_emissions, view_progress, tips_only]"
        )
        result = await self.model.generate_content_async(prompt)
        text = (result.text or "").strip().lower()

        if "view" in text or "progress" in text:
            return "view_progress"
        if "tip" in text:
            return "tips_only"
        if "calculate" in text or "emissions" in text:
            return "calculate_emissions"
        return "calculate_emissions"

    def _needs_sensitive_confirmation(self, user_input: str) -> bool:
        sensitive_keywords = ["address", "income", "exact location", "phone number"]
        return any(k in user_input.lower() for k in sensitive_keywords)

    def _format_response(self, emissions, recs, trend: str) -> str:
        lines = []
        lines.append("### Your approximate carbon footprint\n")
        lines.append(f"Total: ~{emissions['total']:.2f} kg CO₂e\n")
        lines.append("By category:")
        for cat, value in emissions["by_category"].items():
            lines.append(f"- {cat}: ~{value:.2f} kg CO₂e")

        lines.append("\n### Recommended next actions")
        for i, r in enumerate(recs["actions"], start=1):
            lines.append(f"{i}. {r}")

        lines.append("\n### Progress")
        lines.append(trend)

        return "\n".join(lines)
