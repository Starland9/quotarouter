"""Interactive CLI for Qwen Code integration."""

import asyncio
import sys
from typing import Optional

from quotarouter.agents.qwen_agent import AgentSessionManager, QwenAgent
from quotarouter.config.qwen_config import QwenConfig, QwenProvider
from quotarouter.core.router import FreeRouter


class QwenCLI:
    """Interactive CLI for Qwen Code."""

    def __init__(self, router: Optional[FreeRouter] = None):
        """Initialize CLI.

        Args:
            router: FreeRouter instance for quota management
        """
        self.router = router
        self.config = QwenConfig()
        self.config.load_from_file()
        self.session_manager = AgentSessionManager()
        self.current_agent: Optional[QwenAgent] = None

    async def run(self) -> None:
        """Run interactive CLI."""
        print("\n" + "=" * 60)
        print("🦞 Qwen Code Interactive Agent")
        print("=" * 60)

        # Check if providers are configured
        if not self.config.list_providers():
            print("\n⚠️  No providers configured. Running setup...\n")
            await self.setup_provider()

        # Create default session
        self.session_manager.create_session("default", self.router)
        self.current_agent = self.session_manager.get_current_session()

        # Main loop
        await self._main_loop()

    async def _main_loop(self) -> None:
        """Main command loop."""
        while True:
            try:
                # Show current provider/model
                provider = self.current_agent.mcp._get_provider(
                    self.current_agent.model
                )
                if provider:
                    model_str = f" [{provider.id}]"
                else:
                    model_str = " [no model]"

                # Get user input
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: input(f"\n🤖 Qwen{model_str} > ").strip()
                )

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    await self._handle_command(user_input)
                else:
                    # Regular chat
                    await self._chat(user_input)

            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    async def _handle_command(self, command: str) -> None:
        """Handle CLI commands."""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd == "/help":
            self._show_help()
        elif cmd == "/models":
            self._list_models()
        elif cmd == "/select":
            await self._select_model(args)
        elif cmd == "/auth":
            await self.setup_provider()
        elif cmd == "/sessions":
            self._list_sessions()
        elif cmd == "/session":
            await self._manage_session(args)
        elif cmd == "/analyze":
            await self._analyze_code(args)
        elif cmd == "/tests":
            await self._generate_tests(args)
        elif cmd == "/refactor":
            await self._refactor_code(args)
        elif cmd == "/explain":
            await self._explain_code(args)
        elif cmd == "/clear":
            self.current_agent.clear_session()
            print("✅ Session cleared")
        elif cmd == "/history":
            self._show_history()
        elif cmd == "/exit" or cmd == "/quit":
            print("Goodbye! 👋")
            sys.exit(0)
        else:
            print(f"Unknown command: {cmd}. Use /help for available commands.")

    async def _chat(self, message: str) -> None:
        """Send chat message."""
        print("\n⏳ Thinking...")

        try:
            full_response = ""
            async for chunk in self.current_agent.chat_stream(message):
                print(chunk, end="", flush=True)
                full_response += chunk

            print("\n")
        except Exception as e:
            print(f"\n❌ Error: {e}")

    async def _analyze_code(self, args: str) -> None:
        """Analyze code."""
        print(
            "📝 Paste your code (end with a blank line, or type 'EOF' on a new line):"
        )
        lines = []
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, input)
                if line.strip() == "EOF" or (not line and lines):
                    break
                lines.append(line)
            except EOFError:
                break

        code = "\n".join(lines)
        if not code.strip():
            print("No code provided.")
            return

        print("\n⏳ Analyzing code...")
        result = await self.current_agent.analyze_code(code, args or "python")
        print(f"\n📊 Analysis:\n{result}\n")

    async def _generate_tests(self, args: str) -> None:
        """Generate tests for code."""
        print(
            "📝 Paste your code (end with a blank line, or type 'EOF' on a new line):"
        )
        lines = []
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, input)
                if line.strip() == "EOF" or (not line and lines):
                    break
                lines.append(line)
            except EOFError:
                break

        code = "\n".join(lines)
        if not code.strip():
            print("No code provided.")
            return

        print("\n⏳ Generating tests...")
        result = await self.current_agent.generate_tests(code, args or "python")
        print(f"\n✅ Generated tests:\n{result}\n")

    async def _refactor_code(self, args: str) -> None:
        """Refactor code."""
        print(
            "📝 Paste your code (end with a blank line, or type 'EOF' on a new line):"
        )
        lines = []
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, input)
                if line.strip() == "EOF" or (not line and lines):
                    break
                lines.append(line)
            except EOFError:
                break

        code = "\n".join(lines)
        if not code.strip():
            print("No code provided.")
            return

        print("\n⏳ Refactoring code...")
        result = await self.current_agent.refactor_code(code, args or "python")
        print(f"\n♻️  Refactored code:\n{result}\n")

    async def _explain_code(self, args: str) -> None:
        """Explain code."""
        print(
            "📝 Paste your code (end with a blank line, or type 'EOF' on a new line):"
        )
        lines = []
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, input)
                if line.strip() == "EOF" or (not line and lines):
                    break
                lines.append(line)
            except EOFError:
                break

        code = "\n".join(lines)
        if not code.strip():
            print("No code provided.")
            return

        print("\n⏳ Explaining code...")
        result = await self.current_agent.explain_code(code, args or "python")
        print(f"\n📖 Explanation:\n{result}\n")

    async def _select_model(self, model_id: str) -> None:
        """Select model."""
        if not model_id:
            self._list_models()
            return

        if self.current_agent.set_model(model_id):
            print(f"✅ Switched to {model_id}")
        else:
            print(f"❌ Model {model_id} not found")

    async def setup_provider(self) -> None:
        """Setup new provider."""
        print("\n" + "=" * 60)
        print("📋 Qwen Code Provider Setup")
        print("=" * 60)

        print("\nChoose provider protocol:")
        protocols = ["openai", "anthropic", "gemini"]
        for i, proto in enumerate(protocols, 1):
            print(f"{i}. {proto}")

        choice = await asyncio.get_event_loop().run_in_executor(
            None, lambda: input("\nSelect (1-3): ").strip()
        )

        protocol_map = {"1": "openai", "2": "anthropic", "3": "gemini"}
        protocol = protocol_map.get(choice)

        if not protocol:
            print("Invalid choice")
            return

        # Get provider details
        provider_id = await asyncio.get_event_loop().run_in_executor(
            None, lambda: input(f"\nEnter model ID (e.g., qwen3.6-plus): ").strip()
        )

        provider_name = await asyncio.get_event_loop().run_in_executor(
            None, lambda: input("Enter provider name (e.g., Qwen): ").strip()
        )

        base_url = await asyncio.get_event_loop().run_in_executor(
            None, lambda: input("Enter API base URL: ").strip()
        )

        env_key = await asyncio.get_event_loop().run_in_executor(
            None, lambda: input("Enter environment variable name for API key: ").strip()
        )

        # Create provider
        provider = QwenProvider(
            id=provider_id,
            name=provider_name,
            protocol=protocol,
            base_url=base_url,
            env_key=env_key,
            description=f"{provider_name} via {protocol.upper()}",
        )

        self.config.add_provider(provider)
        self.config.default_provider = provider.id

        if self.config.save_to_file():
            print(f"\n✅ Provider configured: {provider_id}")
            self.current_agent.set_model(provider_id)
        else:
            print("❌ Failed to save configuration")

    def _list_models(self) -> None:
        """List available models."""
        models = self.current_agent.get_available_models()
        if not models:
            print("No models configured")
            return

        print("\n📦 Available Models:")
        for model in models:
            current = " ⭐" if model["id"] == self.current_agent.model else ""
            print(
                f"  • {model['id']:<25} ({model['protocol']}) - {model['description']}{current}"
            )

    def _list_sessions(self) -> None:
        """List active sessions."""
        sessions = self.session_manager.list_sessions()
        if not sessions:
            print("No active sessions")
            return

        print("\n🔄 Active Sessions:")
        for session_id in sessions:
            current = (
                " ⭐" if session_id == self.session_manager.current_session else ""
            )
            print(f"  • {session_id}{current}")

    async def _manage_session(self, args: str) -> None:
        """Manage sessions."""
        parts = args.split()
        if not parts:
            print("Usage: /session <new|delete|switch> [session_id]")
            return

        action = parts[0].lower()

        if action == "new":
            session_id = (
                parts[1]
                if len(parts) > 1
                else f"session_{len(self.session_manager.sessions)}"
            )
            self.session_manager.create_session(session_id, self.router)
            self.current_agent = self.session_manager.get_current_session()
            print(f"✅ Created session: {session_id}")

        elif action == "delete":
            if len(parts) < 2:
                print("Specify session to delete")
                return
            if self.session_manager.delete_session(parts[1]):
                self.current_agent = self.session_manager.get_current_session()
                print(f"✅ Deleted session: {parts[1]}")
            else:
                print("Session not found")

        elif action == "switch":
            if len(parts) < 2:
                self._list_sessions()
                return
            if self.session_manager.switch_session(parts[1]):
                self.current_agent = self.session_manager.get_current_session()
                print(f"✅ Switched to {parts[1]}")
            else:
                print("Session not found")

    def _show_history(self) -> None:
        """Show conversation history."""
        history = self.current_agent.get_session_history()
        if not history:
            print("No conversation history")
            return

        print("\n📜 Conversation History:")
        for i, msg in enumerate(history, 1):
            role = "👤" if msg["role"] == "user" else "🤖"
            content = msg["content"][:100]
            if len(msg["content"]) > 100:
                content += "..."
            print(f"{i}. {role} {msg['role']}: {content}")

    def _show_help(self) -> None:
        """Show help message."""
        print(
            """
🆘 Available Commands:

  Chat:
    /help              Show this help message
    /clear             Clear conversation history
    /history           Show conversation history
    /exit, /quit       Exit the program

  Models:
    /models            List available models
    /select <id>       Switch to a model
    /auth              Setup new provider/model

  Sessions:
    /sessions          List all sessions
    /session new       Create new session
    /session delete <id>  Delete session
    /session switch <id>  Switch to session

  Code Tools:
    /analyze [lang]    Analyze code (default: python)
    /tests [lang]      Generate tests (default: python)
    /refactor [lang]   Refactor code (default: python)
    /explain [lang]    Explain code (default: python)

"""
        )


async def main(router: Optional[FreeRouter] = None) -> None:
    """Main entry point."""
    cli = QwenCLI(router)
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())
