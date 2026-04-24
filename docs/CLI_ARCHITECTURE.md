# CLI Architecture Guide

## Overview

The QuotaRouter CLI is organized in a modular architecture that makes it easy to add new commands and maintain existing ones.

```
src/quotarouter/cli/
├── __init__.py              # Main CLI app definition and command registration
├── commands/                # Individual command implementations
│   ├── __init__.py          # Command exports
│   ├── status.py            # Show provider status
│   ├── complete.py          # Send single completion request
│   ├── stream.py            # Stream responses
│   ├── config.py            # Configuration management
│   ├── reset.py             # Reset quotas
│   └── book.py              # NEW: Write entire books with retry logic
└── utils/                   # Shared utilities
    ├── __init__.py          # Rich component exports
    └── errors.py            # Error handling functions
```

## Architecture Principles

### 1. Single Responsibility
Each command module is responsible for exactly one CLI command. Business logic is separated from CLI infrastructure.

### 2. Shared Utilities
- **Formatting**: Rich components (Console, Table, Panel, Progress) exported from `utils/__init__.py`
- **Error Handling**: Centralized error functions in `utils/errors.py`
  - `print_error(message, exit_code=1)`: Print error and exit
  - `print_warning(message)`: Print yellow warning
  - `print_success(message)`: Print green success

### 3. Command Registration
Commands are registered in `cli/__init__.py`:
```python
app.command(name="command_name")(command_function)
```

The `name` parameter explicitly sets the CLI command name, allowing function names to be semantic (e.g., `status_command` becomes `quotarouter status`).

## Adding a New Command

### Step 1: Create Command Module
Create `src/quotarouter/cli/commands/mycommand.py`:

```python
"""My new command."""

import typer
from rich.console import Console

console = Console()

def my_command(
    arg: str = typer.Argument(..., help="Required argument"),
    option: str = typer.Option("default", help="Optional flag"),
):
    """
    Brief description.
    
    Longer description with usage examples.
    """
    try:
        # Implementation
        console.print("[green]Success[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
```

### Step 2: Export from commands/__init__.py
Add to `src/quotarouter/cli/commands/__init__.py`:
```python
from .mycommand import my_command

__all__ = [..., "my_command"]
```

### Step 3: Register in cli/__init__.py
Add to `src/quotarouter/cli/__init__.py`:
```python
from .commands import my_command

# In the registration section:
app.command(name="mycommand")(my_command)
```

## Current Commands

### status
**File**: [status.py](status.py)
**Purpose**: Display provider quota status with Rich table
**Features**: Formatted table, quota statistics, summary panel

### complete
**File**: [complete.py](complete.py)
**Purpose**: Send single completion request
**Features**: Custom system prompt, token limits, session stats

### stream
**File**: [stream.py](stream.py)
**Purpose**: Stream long responses
**Features**: Real-time output, session tracking

### config
**File**: [config.py](config.py)
**Purpose**: Show configuration info
**Features**: List API key requirements, provider defaults

### reset
**File**: [reset.py](reset.py)
**Purpose**: Reset quota counters
**Features**: Safety confirmation, admin-only operation

### book (NEW)
**File**: [book.py](book.py)
**Purpose**: Write entire books chapter by chapter
**Features**:
- Multi-chapter generation with progress tracking
- Automatic retry on failure (configurable max retries)
- Checkpoint/save after each chapter
- Progress bar with chapter tracking
- Provider fallback when quota exhausts
- Resume from last checkpoint
- Markdown output with chapter structure

## Testing Commands

```bash
# Test CLI help
quotarouter --help

# Test individual commands
quotarouter status
quotarouter config --list
quotarouter book "My Book" --chapters 3 -o book.md
quotarouter book "Story" -c 2 --chapter-length 1500
```

## Error Handling Patterns

All commands follow this pattern:

```python
try:
    # Command logic
    console.print("[green]✅ Success[/green]")
except Exception as e:
    console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
    raise typer.Exit(code=1)
```

Or use the shared error utilities:
```python
from ..utils.errors import print_error, print_warning, print_success

try:
    # Logic
    print_success("Operation completed")
except Exception as e:
    print_error(str(e))  # This will exit with code 1
```

## Development Guidelines

1. **Keep commands focused**: One command, one file, one responsibility
2. **Use Rich for output**: All formatting should use Rich components
3. **Handle errors gracefully**: Always catch exceptions and provide helpful messages
4. **Update help text**: Use docstrings and option helps for self-documenting code
5. **Test each command**: Verify with `quotarouter command_name --help`

## Module Dependencies

```
cli/__init__.py
├── commands/
│   ├── status.py → FreeRouter
│   ├── complete.py → FreeRouter
│   ├── stream.py → FreeRouter
│   ├── config.py → DEFAULT_PROVIDERS
│   ├── reset.py → FreeRouter
│   └── book.py → FreeRouter, Progress, Panel
└── utils/
    ├── __init__.py → Rich
    └── errors.py → Rich, sys
```

All commands import from `...core.router` and `...config.registry` as needed.
