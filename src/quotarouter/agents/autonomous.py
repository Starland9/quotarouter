"""Autonomous agent engine with MCP integration."""

import asyncio
import json
from pathlib import Path
from typing import Optional, Any
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.table import Table

from quotarouter.core.router import FreeRouter
from quotarouter.agents.autopilot import (
    ProjectManager,
    ProjectPlan,
    Task,
    TaskStatus,
    AgentState,
)

console = Console()


class AutopilotAgent:
    """Autonomous development agent with MCP support."""

    def __init__(
        self,
        project_dir: str,
        router: Optional[FreeRouter] = None,
        max_iterations: int = 100,
        auto_approve: bool = False,
    ):
        """Initialize autopilot agent.

        Args:
            project_dir: Directory containing the project
            router: QuotaRouter instance for LLM access
            max_iterations: Maximum iterations before stopping
            auto_approve: Automatically approve changes without confirmation
        """
        self.project_dir = Path(project_dir).expanduser()
        self.router = router or FreeRouter(verbose=False)
        self.manager = ProjectManager(self.project_dir)
        self.state = AgentState()
        self.max_iterations = max_iterations
        self.auto_approve = auto_approve

        # System prompt for the agent
        self.system_prompt = """You are an autonomous development agent. Your role is to:

1. **Understand the project** - Analyze the project structure and requirements
2. **Plan work** - Create a detailed task list with priorities
3. **Execute tasks** - Implement features, fix bugs, write tests
4. **Verify completion** - Ensure tasks are completed correctly
5. **Adapt** - Adjust your approach based on results

Always:
- Think step-by-step before taking action
- Consider edge cases and error handling
- Follow best practices for the language/framework
- Test your changes thoroughly
- Document your work

Tools available:
- Read files: Use read_file(path) to view code
- Write files: Use write_file(path, content) to create/modify files
- Run commands: Use run_command(cmd) to execute shell commands
- Analyze: Use analyze_code(path) for suggestions
- Test: Use generate_tests(path) to create tests"""

    async def analyze_project(self) -> str:
        """Analyze project structure and requirements."""
        console.print(
            Panel(
                "[bold cyan]🔍 Analyzing project structure...[/bold cyan]",
                border_style="cyan",
            )
        )

        # Get project overview
        analysis_prompt = f"""Analyze this project structure and requirements:

Project directory: {self.project_dir}

Tasks:
1. List all main files and their purposes
2. Identify the tech stack
3. Describe the project's primary goal
4. Identify potential issues or areas for improvement
5. Suggest initial development tasks

Be concise but thorough."""

        analysis = self.router.complete(
            prompt=analysis_prompt,
            system=self.system_prompt,
            max_tokens=2000,
        )

        return analysis

    async def create_plan(self, analysis: str) -> ProjectPlan:
        """Create project development plan based on analysis."""
        console.print(
            Panel(
                "[bold cyan]📋 Creating development plan...[/bold cyan]",
                border_style="cyan",
            )
        )

        plan_prompt = f"""Based on this project analysis:

{analysis}

Create a detailed development plan with:
1. Project name and description
2. 3-5 main goals
3. 10-15 specific, actionable tasks with priorities (1=high, 2=medium, 3=low)

Format your response as JSON:
{{
  "project_name": "string",
  "description": "string",
  "goals": ["goal1", "goal2", ...],
  "tasks": [
    {{
      "id": "task_1",
      "title": "string",
      "description": "string",
      "priority": 1
    }},
    ...
  ]
}}

Only output the JSON, no other text."""

        plan_json = self.router.complete(
            prompt=plan_prompt,
            system=self.system_prompt,
            max_tokens=3000,
        )

        try:
            plan_data = json.loads(plan_json)
            tasks = [
                Task(
                    id=t["id"],
                    title=t["title"],
                    description=t["description"],
                    priority=t.get("priority", 2),
                )
                for t in plan_data.get("tasks", [])
            ]

            plan = ProjectPlan(
                project_name=plan_data.get("project_name", "Unknown Project"),
                description=plan_data.get("description", ""),
                goals=plan_data.get("goals", []),
                tasks=tasks,
            )

            self.manager.save_plan(plan)
            return plan

        except json.JSONDecodeError:
            console.print("[red]Failed to parse plan JSON[/red]")
            # Create minimal plan
            return ProjectPlan(
                project_name="Development Project",
                description="Automated development plan",
                goals=["Improve code quality"],
                tasks=[],
            )

    async def execute_task(self, task: Task, plan: ProjectPlan) -> bool:
        """Execute a single task."""
        self.state.iterations += 1

        # Update UI
        console.print()
        console.print(
            Panel(
                f"[bold yellow]▶ Task {task.id}[/bold yellow]\n"
                f"[cyan]{task.title}[/cyan]\n\n"
                f"[dim]{task.description}[/dim]",
                border_style="yellow",
            )
        )

        # Generate execution plan
        self.state.add_thought(f"Starting task: {task.title}")

        execution_prompt = f"""Execute this development task:

Task: {task.title}
Description: {task.description}

Project context:
- Name: {plan.project_name}
- Goals: {", ".join(plan.goals)}

Steps to follow:
1. Understand what needs to be done
2. Check what files exist
3. Implement the solution
4. Test the changes
5. Verify completion

Provide a detailed execution plan with specific file paths and code changes needed."""

        plan_text = self.router.complete(
            prompt=execution_prompt,
            system=self.system_prompt,
            max_tokens=2000,
        )

        console.print(
            Panel(
                plan_text,
                border_style="green",
                title="📝 Execution Plan",
            )
        )

        # Request approval unless auto_approve is enabled
        if not self.auto_approve:
            console.print(
                "\n[yellow]Review the plan above and confirm continuation:[/yellow]"
            )
            console.print(
                "[dim]Press Enter to continue or 'skip' to skip this task...[/dim]"
            )
            response = input("> ").strip().lower()
            if response == "skip":
                return False

        # Execute the plan
        with console.status("[bold green]⚙️  Executing task...[/bold green]"):
            execution = self.router.complete(
                prompt=f"""Now execute the plan above. Start implementing:

{plan_text}

Provide the actual code/changes needed. Be specific about file paths and line numbers.""",
                system=self.system_prompt,
                max_tokens=3000,
            )

        console.print(
            Panel(
                execution,
                border_style="green",
                title="✅ Implementation",
            )
        )

        self.manager.log_task(task.id, f"Execution result:\n{execution}")

        self.state.tasks_completed += 1
        return True

    async def run_autopilot(self, create_new_plan: bool = False) -> None:
        """Run autonomous development agent."""

        console.print(
            Panel(
                "[bold cyan]🚀 QuotaRouter Autopilot Agent[/bold cyan]\n\n"
                f"[cyan]Project:[/cyan] {self.project_dir}\n"
                f"[cyan]Max iterations:[/cyan] {self.max_iterations}\n"
                f"[cyan]Auto-approve:[/cyan] {'Yes' if self.auto_approve else 'No'}",
                border_style="cyan",
                title="🤖 Autopilot Started",
            )
        )

        # Load or create plan
        plan = None
        if not create_new_plan:
            plan = self.manager.load_plan()

        if not plan:
            analysis = await self.analyze_project()
            plan = await self.create_plan(analysis)

        # Display plan
        self._display_plan(plan)

        # Main loop
        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1

            # Check if complete
            if self.manager.is_project_complete(plan):
                console.print(
                    Panel(
                        "[bold green]✅ All tasks completed![/bold green]",
                        border_style="green",
                        title="🎉 Project Complete",
                    )
                )
                break

            # Get next pending task
            pending = self.manager.get_pending_tasks(plan)
            if not pending:
                break

            task = pending[0]

            # Execute task
            try:
                success = await self.execute_task(task, plan)

                if success:
                    self.manager.update_task(plan, task.id, TaskStatus.COMPLETED)
                else:
                    self.manager.update_task(plan, task.id, TaskStatus.BLOCKED)

                self.manager.save_plan(plan)

            except Exception as e:
                console.print(f"[red]Error executing task: {e}[/red]")
                self.manager.update_task(plan, task.id, TaskStatus.FAILED, str(e))
                self.state.tasks_failed += 1
                self.manager.save_plan(plan)

            # Show progress
            completed, total = self.manager.get_task_progress(plan)
            console.print(
                f"\n[cyan]Progress: {completed}/{total} tasks completed[/cyan]"
            )

        # Final summary
        self._display_summary(plan)

    def _display_plan(self, plan: ProjectPlan) -> None:
        """Display project plan."""
        table = Table(
            title=plan.project_name, show_header=True, header_style="bold cyan"
        )
        table.add_column("Task", style="cyan", width=30)
        table.add_column("Description", width=50)
        table.add_column("Priority", justify="center", width=12)

        for task in plan.tasks:
            priority_emoji = (
                "🔴" if task.priority == 1 else "🟡" if task.priority == 2 else "🟢"
            )
            table.add_row(
                task.title,
                task.description[:47] + "...",
                f"{priority_emoji} {task.priority}",
            )

        console.print(table)

    def _display_summary(self, plan: ProjectPlan) -> None:
        """Display execution summary."""
        completed, total = self.manager.get_task_progress(plan)

        table = Table(
            title="Execution Summary", show_header=True, header_style="bold green"
        )
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Tasks", str(total))
        table.add_row("Completed", str(completed))
        table.add_row(
            "Success Rate", f"{completed / total * 100:.1f}%" if total > 0 else "0%"
        )
        table.add_row("Iterations", str(self.state.iterations))
        table.add_row(
            "Status",
            "✅ Complete"
            if self.manager.is_project_complete(plan)
            else "⏳ In Progress",
        )

        console.print(table)
