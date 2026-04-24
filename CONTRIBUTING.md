# Contributing to FreeRouter

We love your input! We want to make contributing to FreeRouter as easy and transparent as possible.

## Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/Starland9/quotarouter.git
cd quotarouter
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install in development mode

```bash
pip install -e ".[dev]"
```

### 4. Copy environment template

```bash
cp .env.example .env
# Add your API keys to .env
```

## Code Style

We follow PEP 8 with a 100-character line limit.

### Format Code

```bash
# Format with black
black src/ tests/ examples/

# Sort imports
isort src/ tests/ examples/

# Check style
flake8 src/ tests/
```

### Type Hints

```python
# Good
def complete(self, prompt: str, max_tokens: int = 4096) -> str:
    pass

# Also good (for complex types)
from typing import Optional, Iterator

def complete_stream(
    self,
    prompt: str,
    max_tokens: int = 4096,
) -> Iterator[str]:
    pass
```

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=quotarouter --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run specific test
pytest tests/test_core.py::TestFreeRouter::test_router_initialization
```

### Write Tests

Tests go in `tests/test_*.py`. Use pytest conventions:

```python
import pytest
from quotarouter import FreeRouter

class TestFreeRouter:
    def test_router_initialization(self):
        """Test that router initializes correctly."""
        router = FreeRouter(verbose=False)
        assert router is not None

    def test_with_fixture(self, some_fixture):
        """Test using a fixture."""
        pass
```

### Test Coverage

Aim for >80% coverage:

```bash
pytest --cov=quotarouter --cov-report=term-missing
```

## Process

### 1. Create an issue

Describe the bug or feature request. Discuss approach before coding.

### 2. Create a feature branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/my-bug-fix
```

### 3. Make changes

- Write clean, well-documented code
- Add tests for new functionality
- Update documentation

### 4. Verify code quality

```bash
# Format
black src/ tests/
isort src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/

# Test
pytest
```

### 5. Commit with descriptive message

```bash
git commit -m "feat: add support for custom adapters

- Implement ProviderAdapter ABC
- Add OpenAI-compatible adapter
- Update documentation with examples"
```

### 6. Push and create pull request

```bash
git push origin feature/my-feature
```

Then open a PR on GitHub with:
- Clear title (e.g., "Add support for Claude models")
- Description of changes
- Related issue number (e.g., "Fixes #123")

## Architecture Guidelines

FreeRouter follows **SOLID principles**:

- **S**ingle Responsibility: Each class has one reason to change
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Subtypes interchangeable for base types
- **I**nterface Segregation: Focused interfaces, not bloated ones
- **D**ependency Inversion: Depend on abstractions, not concretions

### Adding a New Adapter

1. Create `src/quotarouter/providers/your_adapter.py`
2. Implement `ProviderAdapter` ABC
3. Add tests in `tests/test_your_adapter.py`
4. Update `src/quotarouter/providers/__init__.py`
5. Document in `docs/API.md`

### Adding a New Provider

1. Add to `src/quotarouter/config/registry.py`
2. Add environment variable to `.env.example`
3. Update README with provider info

## Documentation

### Docstring Style

Use Google-style docstrings:

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
    
    Automatically falls back to next provider if quota is hit.
    
    Args:
        prompt: User prompt
        system: System prompt
        max_tokens: Max response tokens
        history: Previous messages for context
        
    Returns:
        Response text
        
    Raises:
        RuntimeError: If all providers exhausted
    """
    pass
```

### Update Documentation

- Update `docs/` files when API changes
- Keep `README.md` examples working
- Update examples in `examples/` if behavior changes

## Commit Message Convention

Use Conventional Commits:

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, missing semicolons)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Maintenance, dependency updates

Examples:
```
feat(provider): add support for Claude models

fix(router): handle timeout errors gracefully

docs: improve quickstart guide

test(storage): add JSON storage tests
```

## Reporting Bugs

**Security Issues:** Please email security@example.com instead of using issues.

**Other Issues:** Include:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (Python version, OS, etc.)
- API keys (NEVER! Use placeholders)

## Suggesting Features

Include:
- Use case / motivation
- Proposed solution
- Alternative solutions considered
- Any concerns

## Questions?

- Open a [Discussion](https://github.com/Starland9/quotarouter/discussions)
- Ask in Issues
- Email: landrysimo99@gmail.com

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all.

- Be respectful and inclusive
- Welcome different opinions
- Provide constructive feedback
- Focus on the idea, not the person

## License

By contributing, you agree that your contributions will be licensed under its MIT License.

---

**Thank you for contributing to FreeRouter! 🎉**
