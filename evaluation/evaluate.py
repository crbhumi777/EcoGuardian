"""
LLM-as-a-Judge evaluation.

This script:
- Sends a few fixed prompts through the system
- Asks Gemini to rate the quality of EcoGuardian's responses
"""

import asyncio
from main_demo import AgentRuntime


EVAL_SCENARIOS = [
    "Last month I flew from Delhi to Mumbai twice, drove 200 km by car and used 150 kWh of electricity. Estimate my emissions and suggest what to change.",
    "I eat fish 4 times a week, take short flights often, and keep my AC on all night. Where should I focus to reduce my footprint?",
]


async def judge_response(model, user_input: str, agent_output: str) -> str:
    prompt = (
        "You are evaluating the quality of a sustainability assistant's answer.\n"
        "Rate the answer on a scale of 1 to 10 for clarity, correctness and actionability, "
        "then explain briefly.\n\n"
        f"User input:\n{user_input}\n\n"
        f"Assistant output:\n{agent_output}"
    )
    result = await model.generate_content_async(prompt)
    return result.text


async def main():
    runtime = AgentRuntime()
    model = runtime.orchestrator_agent.model

    for i, scenario in enumerate(EVAL_SCENARIOS, start=1):
        print(f"\n=== Scenario {i} ===")
        resp = await runtime.handle_user("eval_session", scenario)
        print("AGENT RESPONSE:\n", resp)

        score = await judge_response(model, scenario, resp)
        print("\nLLM-AS-JUDGE:\n", score)


if __name__ == "__main__":
    asyncio.run(main())
