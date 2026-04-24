# 🏗️ FreeRouter Development Instructions

This file documents the core architectural principles and coding standards for FreeRouter. All contributions should follow these rules.

## Core Principles

### 1. SOLID Architecture

FreeRouter strictly follows **SOLID principles** to ensure maintainability and extensibility:

- **S**ingle Responsibility: Each class/module has exactly ONE reason to change
  - `types.py` → Type definitions only
  - `router.py` → Routing logic only
  - `quota_manager.py` → Storage persistence only
  - `openai_compatible.py` → API communication only
  - `cli.py` → CLI command handling only

- **O**pen/Closed: Code is open for extension, closed for modification
  - Add new providers via `ProviderConfig` without modifying `FreeRouter`
  - Add new adapters via `ProviderAdapter` ABC without changing router logic
  - Add new storage backends via `QuotaStorage` ABC without modifying router
  - Add new CLI commands via Typer without modifying core router

- **L**iskov Substitution: Subtypes are interchangeable for base types
  - `InMemoryQuotaStorage` and `JSONQuotaStorage` both implement `QuotaStorage`
  - Any `ProviderAdapter` works with the router
  - Any `ProviderConfig` integrates seamlessly

- **I**nterface Segregation: Depend on focused interfaces, not bloated ones
  - `ProviderAdapter` has only 2 methods: `complete()` and `complete_stream()`
  - `QuotaStorage` has only 2 methods: `load_quotas
  - CLI commands accept only needed parameters()` and `save_quotas()`
  - Router doesn't depend on OpenAI client directly

- **D**ependency Inversion: Depend on abstractions, not concrete implementations
  - `FreeRouter.__init__()` accepts abstract `ProviderAdapter` and `QuotaStorage`
  - Concrete implementations are injected at runtime
  - CLI uses injected router instance for flexibility
  - Easy to swap implementations for testing or alternative backends

### 2. Module Organization

**NEVER** deviate from this structure:

```
src/__init__.py          ← Package entry, .env loading
├── __main__.py          ← Python module execution
├── cli.py               ← CLI command definitions (NEW)
├── core/
│   ├── types.py         ← Abstract interfaces & data models ONLY
│   └── router.py        ← Main routing logic ONLY
├── providers/
│   └── openai_compatible.py  ← Adapter implementations
├── config/
│   └── registry.py      ← Provider configurations
└── storage/
    └── quota_manager.py ← Storage implementations
```

**Rules:**
- New code goes in `src/quotarouter/`, NOT at root
- Never create new directories without justification
- Keep module names singular and descriptive
- CLI logic goes in `cli.py` only, not scattered across modulesfication
- Keep module names singular and descriptive

### 3. Import Paths

**CRITICAL**: Always import from the correct module to avoid circular dependencies.

**Correct:**
```python
# In storage/quota_manager.py
from ..core.types import QuotaStorage  # ✅ Import from core.types

# In core/router.py
from ..config.registry import DEFAULT_PROVIDERS  # ✅ Up then across
```

**Incorrect:**
```python
# ❌ DON'T do this - creates circular import
from .types import QuotaStorage  # Wrong - types is in core, not storage

# ❌ DON'T do this - breaks dependency inversion
from ..storage.quota_manager import JSONQuotaStorage  # Should inject instead
```

**Pattern:**
- Import abstractions from `core.types` (the single source of truth)
- Never import concrete implementations from other modules
- Use dependency injection (`__init__` parameters) to pass implementations

### 4. Provider Pattern

**When adding a new provider:**

1. **Add to registry** (`config/registry.py`):
   ```python
   ProviderConfig(
       id="unique_id",
       name="Display Name",
       model="model-name",
       daily_token_limit=1_000_000,
       rpm_limit=60,
       priority=N,  # Lower = higher priority
       api_key_env="PROVIDER_API_KEY",
       base_url="https://api.provider.com/v1",
       flag="🌍",  # Country flag emoji
   )
   ```

2. **Add environment variable** (`.env.example`):
   ```bash
   PROVIDER_API_KEY=your_key_here
   ```

3. **Update documentation** (`README.md`):
   - Add to provider table
   - Update token count in features
   - Add to acknowledgments

4. **Test**:
   - Providers use OpenAI-compatible API ✅
   - Other APIs require new `ProviderAdapter` implementation

### 5. CLI Pattern (NEW)

**When adding a new CLI command:**

1. **Define command in `cli.py`** using `@app.command()`:
   ```python
   @app.command()
   def my_command(
       arg1: str = typer.Argument(..., help="Description"),
       opt1: str = typer.Option("default", "--opt1", help="Description"),
   ):
       """Command description for help text."""
       try:
           # Implementation
           console.print("[green]Success[/green]")
       except Exception as e:
           console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
           raise typer.Exit(code=1)
   ```

2. **Use Rich for output** (console, tables, panels):
   ```python
   from rich.console import Console
   from rich.table import Table
   
   console = Console()
   table = Table(title="Title")
   table.add_column("Column")
   console.print(table)
   ```

3. **Handle errors gracefully**:
   - Catch specific exceptions only
   - Print helpful error messages
   - Exit with code 1 on error
   - Never let exceptions bubble up unhandled

4. **Test CLI commands**:
   - Test in isolation (mock router if needed)
   - Test error cases
   - Verify exit codes

### 6. Testing Standards

**Test organization:**
- Tests go in `tests/test_*.py` matching module names
- Use `pytest` with fixtures and mocking
- Target >80% code coverage

**Mocking rules:**
- **For properties**: Use `patch.dict("os.environ", {...})` NOT `patch.object()` on properties
  ```python
  # ✅ Correct
  with patch.dict("os.environ", {"API_KEY": "fake"}):
      assert provider.is_configured  # Checks environment

  # ❌ Wrong - properties don't have setters
  with patch.object(provider, "is_configured", True):
      pass
  ```

- **For imports**: Patch at the source module (where it's imported from)
  ```python
  # ✅ Correct - patch where OpenAI is actually used
  with patch("openai.OpenAI") as mock:
      adapter.complete(...)

  # ❌ Wrong - doesn't patch the right location
  with patch("quotarouter.providers.openai_compatible.OpenAI"):
      pass
  ```

- **Create isolated test providers**: Use `create_test_providers()` instead of modifying defaults

### 6. Type Hints & Documentation

**Always include:**
- Type hints on function parameters and return types
- Google-style docstrings with Args, Returns, Raises sections
- Descriptive variable names (no `x`, `y`, `temp`)

```python
def complete(
    self,
    prompt: str,
    system: str = "You are a helpful assistant.",
    max_tokens: int = 4096,
    history: Optional[list[dict]] = None,
) -> str:
    """
    Send a prompt and get response.
    
    Args:
        prompt: User prompt text
        system: System prompt for context
        max_tokens: Maximum response tokens
        history: Previous messages for context
        
    Returns:
        Response text from LLM
        
    Raises:
        RuntimeError: If all providers exhausted
    """
```

### 7. Code Style

- **Line length**: 100 characters max
- **Format**: `black` (run before commit)
- **Sort imports**: `isort` with black profile
- **Lint**: `flake8` must pass
- **Types**: `mypy` for type checking (warnings OK, errors not)

```bash
# Before committing, run:
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

### 8. Provider Adapter Pattern

**Never create provider-specific code in `router.py`**. Instead:

1. Create adapter that extends `ProviderAdapter` ABC
2. Implement `complete()` and `complete_stream()` methods
3. Handle provider-specific logic (authentication, error handling) in adapter
4. Router stays provider-agnostic

Example structure:
```python
class AzureOpenAIAdapter(ProviderAdapter):
    """Azure-specific OpenAI implementation."""
    
    def complete(self, provider, messages, max_tokens):
        # Azure-specific logic here
        pass
    
    def complete_stream(self, provider, messages, max_tokens):
        # Azure-specific logic here
        pass
```

### 9. Storage Implementation Pattern

**When creating custom storage:**

```python
class DatabaseQuotaStorage(QuotaStorage):
    """Persist quotas to database."""
    
    def load_quotas(self) -> dict[str, int]:
        """Load from database."""
        pass
    
    def save_quotas(self, quotas: dict[str, int]) -> None:
        """Save to database."""
        pass
```

Then inject: `router = FreeRouter(storage=DatabaseQuotaStorage())`

### 10. Environment Variable Loading

**Pattern for `.env` file handling:**

The package automatically loads `.env` from the current working directory on import:

```python
# In __init__.py - automatically runs on package import
def _load_dotenv_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    # Parse and load into os.environ
    
_load_dotenv()  # Called at package import time
```

**Rules:**
- `.env` is loaded from `Path.cwd() / ".env"` (current working directory)
- Only loads if file exists
- Skips comments (lines starting with `#`)
- Supports `export` prefix and quoted values
- Never overwrites existing environment variables
- Users can manually set env vars instead of using `.env`

### 11. Versioning

**Version format** (Semantic Versioning):
- **Major**: Breaking changes to public API
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes

**Update checklist** before release:

1. Update version in all files:
   - `pyproject.toml` → `[project] version = "x.y.z"`
   - `setup.py` → `version="x.y.z"`
   - `src/quotarouter/__init__.py` → `__version__ = "x.y.z"`

2. Update `CHANGELOG.md`:
   - Move `[Unreleased]` items to new version section
   - Add date in format `YYYY-MM-DD`
   - Categorize changes: Added, Changed, Fixed, Removed, Deprecated

3. Commit and tag:
   ```bash
   git add CHANGELOG.md pyproject.toml setup.py src/quotarouter/__init__.py
   git commit -m "chore: release v0.3.0"
   git tag -a v0.3.0 -m "Release version 0.3.0"
   ```

### 12. Documentation Updates

**When changing code, update:**
- Docstrings in code
- Type hints if signature changes
- `docs/API.md` if public API changes
- `docs/ARCHITECTURE.md` if pattern changes
- `README.md` for user-facing features
- `CLI_GUIDE.md` for CLI changes
- `CHANGELOG.md` for version notes
- `.github/instructions/core-instructions.md` if adding patterns

## Common Patterns

### Adding a Feature
1. Create minimal interface in `core/types.py` if needed
2. Implement concrete version in appropriate module
3. Inject via `__init__()` parameters
4. Test in isolation
5. Document in docstrings and markdown

### Adding a CLI Command
1. Add `@app.command()` function to `cli.py`
2. Use Rich for formatted output
3. Handle errors with try/except and meaningful messages
4. Write tests for command behavior
5. Document in CLI_GUIDE.md

### Fixing a Bug
1. Write failing test first
2. Implement fix in implementation module
3. Ensure test passes
4. Check no other tests break
5. Update CHANGELOG.md

### Refactoring
1. Keep interface stable
2. Change implementation in specific module only
3. Run full test suite
4. Update docs if behavior changes

## Anti-Patterns to Avoid

❌ **Circular imports** - Import from higher-level modules only
❌ **God classes** - Keep classes focused (Single Responsibility)
❌ **Global state** - Use dependency injection instead
❌ **Hardcoded values** - Use configuration and environment variables
❌ **Try/except all** - Catch specific exceptions only
❌ **Monolithic functions** - Break into smaller, testable units
❌ **Skipped tests** - Fix or remove, never skip
❌ **Mixed concerns** - One class = one responsibility
❌ **CLI logic in core** - Keep CLI separate in `cli.py`
❌ **Unformatted output** - Use Rich for tables, panels, colors

## Review Checklist

Before opening a PR, verify:
- [ ] Code follows SOLID principles
- [ ] All new imports are correct (no circular dependencies)
- [ ] Tests pass and cover >80% of new code
- [ ] Code formatted with `black` and `isort`
- [ ] Type hints added to new functions
- [ ] Docstrings updated/added
- [ ] Documentation updated (`README.md`, `docs/`, `CLI_GUIDE.md`)
- [ ] No anti-patterns introduced
- [ ] CHANGELOG.md updated with version and changes
- [ ] Version number updated in `pyproject.toml`, `setup.py`, `__init__.py`

## Questions or Clarifications

If unsure about a pattern, check:
1. `docs/ARCHITECTURE.md` for design patterns
2. `CLI_GUIDE.md` for CLI usage patterns
3. Existing code in similar modules for examples
4. This instructions file for rules
5. Open an issue for discussion

---

**These rules exist to keep FreeRouter maintainable, testable, and extensible as it grows.**
