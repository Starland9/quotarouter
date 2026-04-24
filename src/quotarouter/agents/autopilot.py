"""Autonomous development agent for QuotaRouter."""

import json
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

console = Console()


class TaskStatus(Enum):
    """Task status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Task:
    """Development task."""

    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 1  # 1=high, 2=medium, 3=low
    created_at: str = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 3

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class ProjectPlan:
    """Development project plan."""

    project_name: str
    description: str
    goals: list[str]
    tasks: list[Task]
    created_at: str = None
    updated_at: str = None
    completed: bool = False

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()


class ProjectManager:
    """Manages project plans and tasks."""

    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir).expanduser()
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.plan_file = self.project_dir / "autopilot_plan.json"
        self.logs_dir = self.project_dir / ".autopilot"
        self.logs_dir.mkdir(exist_ok=True)

    def load_plan(self) -> Optional[ProjectPlan]:
        """Load existing project plan."""
        if not self.plan_file.exists():
            return None

        try:
            with open(self.plan_file, "r") as f:
                data = json.load(f)
                tasks = [
                    Task(
                        id=t["id"],
                        title=t["title"],
                        description=t["description"],
                        status=TaskStatus(t.get("status", "pending")),
                        priority=t.get("priority", 1),
                        created_at=t.get("created_at"),
                        completed_at=t.get("completed_at"),
                        error=t.get("error"),
                        attempts=t.get("attempts", 0),
                    )
                    for t in data.get("tasks", [])
                ]
                return ProjectPlan(
                    project_name=data["project_name"],
                    description=data["description"],
                    goals=data["goals"],
                    tasks=tasks,
                    created_at=data.get("created_at"),
                    updated_at=data.get("updated_at"),
                    completed=data.get("completed", False),
                )
        except Exception as e:
            console.print(f"[red]Error loading plan: {e}[/red]")
            return None

    def save_plan(self, plan: ProjectPlan) -> None:
        """Save project plan to file."""
        plan.updated_at = datetime.now().isoformat()
        data = asdict(plan)
        data["tasks"] = [
            {
                **asdict(t),
                "status": t.status.value,
            }
            for t in plan.tasks
        ]

        with open(self.plan_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_pending_tasks(self, plan: ProjectPlan) -> list[Task]:
        """Get pending tasks sorted by priority."""
        pending = [t for t in plan.tasks if t.status == TaskStatus.PENDING]
        return sorted(pending, key=lambda t: t.priority)

    def get_task_progress(self, plan: ProjectPlan) -> tuple[int, int]:
        """Get (completed, total) task counts."""
        total = len(plan.tasks)
        completed = sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED)
        return completed, total

    def update_task(
        self,
        plan: ProjectPlan,
        task_id: str,
        status: TaskStatus,
        error: Optional[str] = None,
    ) -> None:
        """Update task status."""
        for task in plan.tasks:
            if task.id == task_id:
                task.status = status
                task.updated_at = datetime.now().isoformat()
                if status == TaskStatus.COMPLETED:
                    task.completed_at = datetime.now().isoformat()
                if error:
                    task.error = error
                    task.attempts += 1
                break

    def log_task(self, task_id: str, log_content: str) -> None:
        """Log task execution details."""
        log_file = self.logs_dir / f"{task_id}.log"
        with open(log_file, "a") as f:
            f.write(f"\n[{datetime.now().isoformat()}]\n{log_content}\n")

    def is_project_complete(self, plan: ProjectPlan) -> bool:
        """Check if all tasks are completed."""
        if not plan.tasks:
            return False
        return all(t.status == TaskStatus.COMPLETED for t in plan.tasks)


class AgentState:
    """Maintains agent execution state."""

    def __init__(self):
        self.iterations = 0
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.start_time = datetime.now()
        self.last_action = None
        self.thinking = []  # Track agent reasoning

    def add_thought(self, thought: str) -> None:
        """Add agent reasoning."""
        self.thinking.append(
            {
                "timestamp": datetime.now().isoformat(),
                "thought": thought,
            }
        )

    def get_summary(self) -> str:
        """Get execution summary."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return (
            f"Iterations: {self.iterations}\n"
            f"Completed: {self.tasks_completed}\n"
            f"Failed: {self.tasks_failed}\n"
            f"Elapsed: {elapsed:.1f}s"
        )
