"""Agentic wrapper for Qwen Code integration."""

import asyncio
import logging
from typing import Any, Optional

from quotarouter.core.router import FreeRouter
from quotarouter.mcp.qwen_code_server import QwenCodeMCPServer

logger = logging.getLogger(__name__)


class QwenAgent:
    """Agentic wrapper for Qwen Code with routing and quota management."""

    def __init__(self, router: Optional[FreeRouter] = None):
        """Initialize Qwen agent.

        Args:
            router: FreeRouter instance for quota management
        """
        self.router = router
        self.mcp = QwenCodeMCPServer(router)
        self.session_messages: list[dict[str, str]] = []
        self.model: Optional[str] = None

    async def chat(
        self,
        user_message: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> str:
        """Send a chat message and get response.

        Args:
            user_message: User input
            model: Model to use
            system_prompt: System prompt override
            max_tokens: Max response tokens

        Returns:
            Assistant response
        """
        self.session_messages.append({"role": "user", "content": user_message})

        response = await self.mcp.complete(
            prompt=user_message,
            model=model or self.model,
            system=system_prompt or "You are a helpful coding assistant.",
            max_tokens=max_tokens,
        )

        if "error" in response:
            return f"Error: {response['error']}"

        assistant_message = response.get("text", "")
        self.session_messages.append(
            {"role": "assistant", "content": assistant_message}
        )

        return assistant_message

    async def chat_stream(
        self,
        user_message: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
    ):
        """Stream a chat response.

        Args:
            user_message: User input
            model: Model to use
            system_prompt: System prompt override
            max_tokens: Max response tokens

        Yields:
            Response chunks
        """
        self.session_messages.append({"role": "user", "content": user_message})

        full_response = ""

        async for chunk in self.mcp.stream(
            prompt=user_message,
            model=model or self.model,
            system=system_prompt or "You are a helpful coding assistant.",
            max_tokens=max_tokens,
        ):
            if "error" in chunk:
                yield f"Error: {chunk['error']}"
            elif not chunk.get("is_final", False):
                text = chunk.get("text", "")
                full_response += text
                yield text

        self.session_messages.append({"role": "assistant", "content": full_response})

    def set_model(self, model: str) -> bool:
        """Set default model."""
        if self.mcp.set_provider(model):
            self.model = model
            return True
        return False

    def get_session_history(self) -> list[dict[str, str]]:
        """Get session message history."""
        return self.session_messages.copy()

    def clear_session(self) -> None:
        """Clear session history."""
        self.session_messages = []

    def get_available_models(self) -> list[dict[str, str]]:
        """Get available models."""
        return self.mcp.get_available_providers()

    async def analyze_code(
        self,
        code: str,
        language: str = "python",
        analysis_type: str = "general",
    ) -> str:
        """Analyze code snippet.

        Args:
            code: Code to analyze
            language: Programming language
            analysis_type: Type of analysis (general, bugs, performance, security)

        Returns:
            Analysis result
        """
        prompt = f"""Analyze the following {language} code for {analysis_type} issues:

```{language}
{code}
```

Provide:
1. Summary of what the code does
2. Identified {analysis_type} issues
3. Recommendations for improvement
4. Example fix if applicable"""

        return await self.chat(prompt)

    async def generate_tests(
        self,
        code: str,
        language: str = "python",
        framework: Optional[str] = None,
    ) -> str:
        """Generate tests for code.

        Args:
            code: Code to test
            language: Programming language
            framework: Testing framework

        Returns:
            Generated test code
        """
        framework_str = f" using {framework}" if framework else ""
        prompt = f"""Generate unit tests for the following {language} code{framework_str}:

```{language}
{code}
```

Include:
1. Test cases covering main functionality
2. Edge cases
3. Error handling tests
4. Well-documented test descriptions"""

        return await self.chat(prompt)

    async def refactor_code(
        self,
        code: str,
        language: str = "python",
        improvements: Optional[list[str]] = None,
    ) -> str:
        """Refactor code.

        Args:
            code: Code to refactor
            language: Programming language
            improvements: List of specific improvements to make

        Returns:
            Refactored code
        """
        improvements_str = (
            "\n".join(f"- {imp}" for imp in improvements) if improvements else ""
        )

        prompt = f"""Refactor the following {language} code:

```{language}
{code}
```

{f"Focus on: {improvements_str}" if improvements_str else "Improve readability, performance, and maintainability."}

Provide:
1. Refactored code
2. Explanation of changes
3. Benefits of the refactoring"""

        return await self.chat(prompt)

    async def explain_code(
        self,
        code: str,
        language: str = "python",
        detail_level: str = "medium",
    ) -> str:
        """Explain code functionality.

        Args:
            code: Code to explain
            language: Programming language
            detail_level: Level of detail (simple, medium, detailed)

        Returns:
            Code explanation
        """
        prompt = f"""Explain the following {language} code in {detail_level} detail:

```{language}
{code}
```

Cover:
1. Overall purpose and functionality
2. Key algorithm/logic
3. Important variables and their roles
4. Potential gotchas or considerations"""

        return await self.chat(prompt)


class AgentSessionManager:
    """Manage multiple agent sessions."""

    def __init__(self):
        """Initialize session manager."""
        self.sessions: dict[str, QwenAgent] = {}
        self.current_session: Optional[str] = None

    def create_session(
        self, session_id: str, router: Optional[FreeRouter] = None
    ) -> QwenAgent:
        """Create new session."""
        agent = QwenAgent(router)
        self.sessions[session_id] = agent
        if not self.current_session:
            self.current_session = session_id
        return agent

    def get_session(self, session_id: str) -> Optional[QwenAgent]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.current_session == session_id:
                self.current_session = None
            return True
        return False

    def list_sessions(self) -> list[str]:
        """List all session IDs."""
        return list(self.sessions.keys())

    def switch_session(self, session_id: str) -> bool:
        """Switch to session."""
        if session_id in self.sessions:
            self.current_session = session_id
            return True
        return False

    def get_current_session(self) -> Optional[QwenAgent]:
        """Get current session."""
        if self.current_session:
            return self.sessions.get(self.current_session)
        return None
