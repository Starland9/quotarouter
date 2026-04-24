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

- **O**pen/Closed: Code is open for extension, closed for modification
  - Add new providers via `ProviderConfig` without modifying `FreeRouter`
  - Add new adapters via `ProviderAdapter` ABC without changing router logic
  - Add new storage backends via `QuotaStorage` ABC without modifying router

- **L**iskov Substitution: Subtypes are interchangeable for base types
  - `InMemoryQuotaStorage` and `JSONQuotaStorage` both implement `QuotaStorage`
  - Any `ProviderAdapter` works with the router
  - Any `ProviderConfig` integrates seamlessly

- **I**nterface Segregation: Depend on focused interfaces, not bloated ones
  - `ProviderAdapter` has only 2 methods: `complete()` and `complete_stream()`
  - `QuotaStorage` has only 2 methods: `load_quotas()` and `save_quotas()`
  - Router doesn't depend on OpenAI client directly

- **D**ependency Inversion: Depend on abstractions, not concrete implementations
  - `FreeRouter.__init__()` accepts abstract `ProviderAdapter` and `QuotaStorage`
  - Concrete implementations are injected at runtime
  - Easy to swap implementations for testing or alternative backends

### 2. Module Organization

**NEVER** deviate from this structure:

```
src/freerouter/
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
- New code goes in `src/freerouter/`, NOT at root
- Never create new directories without justification
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

### 5. Testing Standards

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
  with patch("freerouter.providers.openai_compatible.OpenAI"):
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

### 10. Documentation Updates

**When changing code, update:**
- Docstrings in code
- Type hints if signature changes
- `docs/API.md` if public API changes
- `docs/ARCHITECTURE.md` if pattern changes
- `README.md` for user-facing features
- `CHANGELOG.md` for version notes

## Common Patterns

### Adding a Feature
1. Create minimal interface in `core/types.py`
2. Implement concrete version in appropriate module
3. Inject via `__init__()` parameters
4. Test in isolation
5. Document in docstrings and markdown

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

## Review Checklist

Before opening a PR, verify:
- [ ] Code follows SOLID principles
- [ ] All new imports are correct (no circular dependencies)
- [ ] Tests pass and cover >80% of new code
- [ ] Code formatted with `black` and `isort`
- [ ] Type hints added to new functions
- [ ] Docstrings updated/added
- [ ] Documentation updated (`README.md`, `docs/`)
- [ ] No anti-patterns introduced
- [ ] CHANGELOG.md updated

## Questions or Clarifications

If unsure about a pattern, check:
1. `docs/ARCHITECTURE.md` for design patterns
2. Existing code in similar modules for examples
3. This instructions file for rules
4. Open an issue for discussion

---

**These rules exist to keep FreeRouter maintainable, testable, and extensible as it grows.**
