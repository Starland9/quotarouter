"""
Example: QuotaRouter Autonomous Agent with Autopilot

This example demonstrates how to use the autonomous development agent
with the --autopilot flag for fully autonomous project development.

Installation:
    pip install quotarouter

Running the agent:
    # Interactive mode (asks for approval)
    quotarouter agent . --new

    # Autonomous mode (no prompts, full automation)
    quotarouter agent . --new --autopilot

    # Custom system prompt
    quotarouter agent . --autopilot --system "You are a Python expert"

    # Limited iterations
    quotarouter agent . --autopilot --max-iterations 50
"""

from quotarouter.agents.autonomous import AutopilotAgent
from quotarouter.core.router import FreeRouter
import asyncio


async def main():
    """Run autonomous agent on a project."""

    # Initialize agent
    router = FreeRouter(verbose=False)
    agent = AutopilotAgent(
        project_dir=".",
        router=router,
        max_iterations=100,
        auto_approve=True,  # Full autopilot mode
    )

    # Optional: customize system prompt
    agent.system_prompt = """You are an expert Python developer. Your role is to:
1. Analyze codebases and identify improvements
2. Write clean, well-tested code
3. Follow Python best practices (PEP 8, type hints)
4. Create comprehensive documentation
5. Fix bugs and optimize performance

Be methodical and thorough in your approach."""

    # Run the autopilot agent
    await agent.run_autopilot(create_new_plan=True)


if __name__ == "__main__":
    asyncio.run(main())
