# 🤖 QuotaRouter Autonomous Agent & Autopilot

Autonomous development agent powered by QuotaRouter for automated project development, planning, and execution.

## 🎯 Overview

The QuotaRouter Autonomous Agent is a fully-featured development AI that can:

- **📊 Analyze Projects** - Understand your codebase structure and goals
- **📋 Plan Work** - Create detailed task lists with priorities
- **⚙️ Execute Tasks** - Implement features, fix bugs, write tests
- **🔄 Iterate** - Adapt based on results and continue until completion
- **💾 Persist State** - Save progress and resume from checkpoints
- **🚀 Autopilot Mode** - Run fully autonomous without human intervention

## 🚀 Quick Start

### Installation

```bash
pip install quotarouter
```

### Interactive Mode (with approval workflow)

```bash
quotarouter agent . --new
```

The agent will:
1. Analyze your project
2. Create a development plan
3. Show each task before executing
4. Ask for your approval before proceeding
5. Execute and save results

### Autonomous Mode (--autopilot)

```bash
quotarouter agent . --autopilot --new
```

The agent runs fully autonomously without prompts:
1. Analyzes project automatically
2. Creates plan automatically
3. Executes all tasks without asking
4. Continues until all tasks are complete

### Resume Previous Work

```bash
quotarouter agent .
```

If a plan already exists, it continues from where it left off.

## 📖 Usage Examples

### Basic Autopilot on Current Directory

```bash
quotarouter agent . --autopilot
```

### Custom System Prompt

```bash
quotarouter agent . --autopilot --system "You are a Python expert specializing in web development"
```

### Limited Iterations

```bash
quotarouter agent . --autopilot --max-iterations 50
```

### Create New Plan (ignore existing)

```bash
quotarouter agent . --new --autopilot
```

### Verbose Mode with Tracking

```bash
quotarouter agent /path/to/project --new
# Responds to each task with approval workflow
```

## 🏗️ Architecture

### Components

1. **ProjectManager** (`autopilot.py`)
   - Manages project plans and tasks
   - Saves/loads state from `autopilot_plan.json`
   - Tracks task progress and logs

2. **AutopilotAgent** (`autonomous.py`)
   - Main agent engine
   - Analyzes projects using LLM
   - Creates and executes plans
   - Manages execution loop

3. **Task System**
   - Task definitions with priority levels
   - Status tracking (pending, in_progress, completed, failed)
   - Error recovery with retry limits

4. **AgentState**
   - Tracks iterations, completions, failures
   - Stores agent reasoning
   - Provides execution metrics

### Data Structures

```python
# Task representation
Task(
    id="task_1",
    title="Add documentation",
    description="Create README and API docs",
    priority=1,  # 1=high, 2=medium, 3=low
    status=TaskStatus.PENDING,
)

# Project plan
ProjectPlan(
    project_name="MyProject",
    description="A Python web service",
    goals=["Improve code quality", "Add tests"],
    tasks=[...],
)
```

## 🔧 Options

### `quotarouter agent [PROJECT_DIR]`

#### Arguments

- `PROJECT_DIR` - Directory to develop (default: `.`)

#### Options

- `--autopilot, -a` - Run fully autonomous (no prompts)
- `--new, -n` - Create new plan (ignore existing)
- `--max-iterations, -m INTEGER` - Max iterations (default: 100)
- `--system, -s TEXT` - Custom system prompt
- `--help` - Show help

## 💾 Project State

The agent saves state to the project directory:

```
project/
├── autopilot_plan.json      # Current plan and task status
└── .autopilot/
    ├── task_1.log          # Task execution logs
    ├── task_2.log
    └── ...
```

### Plan File Example

```json
{
  "project_name": "MyProject",
  "description": "A Python web service",
  "goals": ["Improve testing", "Add CI/CD"],
  "tasks": [
    {
      "id": "task_1",
      "title": "Add unit tests",
      "description": "Create test suite for core module",
      "status": "completed",
      "priority": 1,
      "created_at": "2026-04-24T12:00:00",
      "completed_at": "2026-04-24T12:15:00"
    },
    ...
  ],
  "completed": false,
  "created_at": "2026-04-24T12:00:00",
  "updated_at": "2026-04-24T12:30:00"
}
```

## 🧠 How the Agent Works

### Phase 1: Project Analysis

```python
# Agent reads project structure
# Lists files and directories
# Identifies technologies used
# Determines project purpose
```

### Phase 2: Plan Creation

The agent creates a detailed plan with:
- Project goals (3-5 major objectives)
- Concrete tasks (10-15 specific actions)
- Priority levels for each task
- Execution order based on dependencies

### Phase 3: Task Execution

For each task:
1. **Understand** - Read relevant code and understand requirements
2. **Plan** - Create specific implementation strategy
3. **Review** - Show plan to user (in interactive mode)
4. **Execute** - Implement the solution
5. **Verify** - Ensure completion
6. **Log** - Save execution results

### Phase 4: Iteration

Agent continues until:
- All tasks are completed, OR
- Max iterations reached, OR
- Unrecoverable error occurs

## 🎯 System Prompts

### Default System Prompt

Optimized for general development across multiple languages.

### Custom System Prompts

You can provide specialized prompts for different contexts:

```bash
# Python expert
quotarouter agent . --system "You are a Python expert. Focus on PEP 8, type hints, and testing."

# Web development
quotarouter agent . --system "Specialize in web development. Use modern frameworks and best practices."

# Security
quotarouter agent . --system "Focus on security best practices. Check for vulnerabilities and sanitize inputs."
```

## 📊 Progress Tracking

The agent displays:
- Current task title and description
- Execution plan
- Implementation details
- Progress bar (X/Y tasks completed)
- Success metrics

## 🔄 Error Handling

The agent handles:
- File not found errors
- Permission issues
- LLM API failures (uses FreeRouter fallback)
- Task execution failures
- Graceful interruption (Ctrl+C)

Each task can retry up to 3 times before failing.

## 🚀 Python API

```python
from quotarouter.agents.autonomous import AutopilotAgent
from quotarouter.core.router import FreeRouter
import asyncio

async def main():
    router = FreeRouter()
    agent = AutopilotAgent(
        project_dir="./my_project",
        router=router,
        max_iterations=100,
        auto_approve=True,  # Autopilot mode
    )
    
    # Customize system prompt
    agent.system_prompt = "You are a Python expert..."
    
    # Run agent
    await agent.run_autopilot(create_new_plan=True)

asyncio.run(main())
```

## 📝 Examples

### Example 1: Complete a Python Project

```bash
cd my_python_project
quotarouter agent . --new --autopilot
```

### Example 2: Add Documentation

```bash
quotarouter agent . --system "Focus on creating comprehensive documentation and docstrings"
```

### Example 3: Code Refactoring

```bash
quotarouter agent . --system "Refactor code for readability and performance. Follow Python best practices."
```

### Example 4: Testing

```bash
quotarouter agent . --system "Add comprehensive unit tests. Target 90% code coverage."
```

## ⚙️ Configuration

The agent respects QuotaRouter configuration:

```bash
# Setup providers
quotarouter config set

# Check provider status
quotarouter status

# Run agent (uses configured providers)
quotarouter agent . --autopilot
```

## 🎓 Best Practices

1. **Define Clear Goals** - Projects with specific goals get better plans
2. **Review First Plan** - Use interactive mode first to review the generated plan
3. **Use Domain Prompts** - Customize system prompt for specific domains
4. **Monitor Progress** - Check `.autopilot/` directory for execution logs
5. **Resume Safely** - Agent saves state, you can resume anytime

## 🔗 Integration with QuotaRouter

The agent uses QuotaRouter's quota management:

- **Multi-provider routing** - Switches providers automatically if quota exhausted
- **Token tracking** - Tracks total tokens used
- **Fallback support** - Falls back to next provider seamlessly
- **Cost optimization** - Uses free-tier providers first

## 📦 Installation Options

### Full Installation

```bash
pip install quotarouter
```

This includes all QuotaRouter features plus the autonomous agent.

## 🐛 Troubleshooting

### Agent runs but doesn't execute tasks

**Solution**: Check provider configuration
```bash
quotarouter config set
quotarouter status
```

### Tasks fail with "API not responding"

**Solution**: Start API server in another terminal
```bash
quotarouter api
```

### Agent stuck in loop

**Solution**: Increase `--max-iterations` or reduce project scope

### State file corrupted

**Solution**: Delete `autopilot_plan.json` and run with `--new`

## 📚 More Examples

See `examples/09_autopilot_agent.py` for complete Python API usage.

## 🤝 Contributing

The agent is highly extensible. You can:
- Add custom tools (file operations, command execution, etc.)
- Create specialized agents for specific domains
- Integrate with external APIs
- Build upon the ProjectManager class

## 📄 License

MIT - See LICENSE file
