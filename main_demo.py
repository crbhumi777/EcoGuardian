import asyncio
from typing import Optional

from observability.logging_config import setup_logging
from observability.logging_config import logger
from observability.metrics import metrics

from agents.orchestrator_agent import OrchestratorAgent
from agents.data_fetcher_agent import DataFetcherAgent
from agents.carbon_calculator_agent import CarbonCalculatorAgent
from agents.recommendation_agent import RecommendationAgent
from agents.progress_tracker_agent import ProgressTrackerAgent


class AgentRuntime:
    """
    Very simple "runtime" to mimic ADK-style wiring.
    All agents are attributes; orchestrator calls them.
    """

    def __init__(self):
        self.data_fetcher_agent = DataFetcherAgent()
        self.carbon_calculator_agent = CarbonCalculatorAgent()
        self.recommendation_agent = RecommendationAgent()
        self.progress_tracker_agent = ProgressTrackerAgent()
        self.orchestrator_agent = OrchestratorAgent(runtime=self)

    async def handle_user(self, session_id: str, user_input: str) -> str:
        return await self.orchestrator_agent.handle_request(session_id, user_input)


async def run_cli():
    setup_logging()
    runtime = AgentRuntime()
    session_id = "cli_session"

    print("EcoGuardian – Multi-Agent Sustainability Assistant")
    print("Type 'quit' to exit.\n")

    while True:
        text = input("You: ")
        if text.strip().lower() in ["quit", "exit"]:
            break
        reply = await runtime.handle_user(session_id, text)
        print("\nEcoGuardian:\n", reply, "\n")

    print("\nMetrics snapshot:", metrics.snapshot())
    logger.info("Session ended.")


if __name__ == "__main__":
    asyncio.run(run_cli())
