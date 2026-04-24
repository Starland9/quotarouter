# FreeRouter Project Structure

```
quotarouter/
│
├── 📁 .github/
│   └── workflows/
│       └── tests.yml                 # CI/CD pipeline
│
├── 📁 src/quotarouter/               # Main package
│   ├── __init__.py                  # Package exports
│   │
│   ├── 📁 core/                     # Core logic (SOLID)
│   │   ├── __init__.py
│   │   ├── types.py                 # Abstract interfaces & data models
│   │   └── router.py                # Main FreeRouter class
│   │
│   ├── 📁 providers/                # API adapters (pluggable)
│   │   ├── __init__.py
│   │   └── openai_compatible.py     # OpenAI-compatible adapter
│   │
│   ├── 📁 config/                   # Configuration
│   │   ├── __init__.py
│   │   └── registry.py              # Provider definitions
│   │
│   └── 📁 storage/                  # Quota persistence (swappable)
│       ├── __init__.py
│       └── quota_manager.py         # JSON & in-memory storage
│
├── 📁 tests/                        # Unit tests (>80% coverage)
│   ├── __init__.py
│   └── test_core.py                 # Comprehensive test suite
│
├── 📁 examples/                     # Usage examples
│   ├── README.md                    # Examples guide
│   ├── 01_basic_completion.py       # Simple usage
│   ├── 02_streaming.py              # Streaming responses
│   ├── 03_conversation.py           # Multi-turn chat
│   ├── 04_status.py                 # Monitoring quotas
│   └── 05_custom_provider.py        # Custom configuration
│
├── 📁 docs/                         # Detailed documentation
│   ├── API.md                       # Complete API reference
│   └── ARCHITECTURE.md              # Design patterns & SOLID
│
├── 📄 README.md                     # Main documentation (start here!)
├── 📄 GETTING_STARTED.md            # 5-minute quickstart
├── 📄 CONTRIBUTING.md               # How to contribute
├── 📄 CHANGELOG.md                  # Version history
├── 📄 LICENSE                       # MIT License
│
├── 🔧 pyproject.toml                # Modern Python project config
├── 🔧 setup.py                      # Setuptools configuration
├── 🔧 pytest.ini                    # Test configuration
├── 🔧 requirements.txt              # Production dependencies
├── 🔧 requirements-dev.txt          # Development dependencies
│
├── .gitignore                       # Git ignore rules
└── .env.example                     # API key template

```

## Key Design Principles

### 🏗️ SOLID Architecture

1. **Single Responsibility**: Each class has one job
   - `ProviderConfig`: Configuration
   - `FreeRouter`: Routing logic
   - `ProviderAdapter`: API communication
   - `QuotaStorage`: Persistence

2. **Open/Closed**: Easy to extend
   - Add providers without modifying router
   - Add adapters without changing code
   - Custom storage implementations

3. **Liskov Substitution**: Interchangeable implementations
   - Swap `OpenAICompatibleAdapter` for custom adapter
   - Swap `JSONQuotaStorage` for database storage

4. **Interface Segregation**: Focused contracts
   - `ProviderAdapter` interface
   - `QuotaStorage` interface
   - `ProviderSelector` protocol

5. **Dependency Inversion**: Depend on abstractions
   - Router depends on `ProviderAdapter`, not OpenAI client
   - Router depends on `QuotaStorage`, not JSON file

### 📦 Clean Architecture

```
┌─────────────────────────────────┐
│  Presentation Layer (Examples)  │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  Application Layer (FreeRouter) │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  Business Logic Layer (Core)    │
└──────────────┬──────────────────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────▼──────┐     ┌───▼────────────┐
│ Adapters   │     │ Storage        │
│(Pluggable) │     │ (Pluggable)    │
└────────────┘     └────────────────┘
```

### 🧪 Testing Strategy

- **Unit Tests** in `tests/` (>80% coverage)
- **Fixtures** for common setup
- **Mocking** external APIs
- **In-memory Storage** for testing

### 📚 Documentation

- `README.md` - Start here
- `GETTING_STARTED.md` - 5-minute quickstart
- `docs/API.md` - Complete API reference
- `docs/ARCHITECTURE.md` - Design deep dive
- `examples/` - 5 working examples
- `CONTRIBUTING.md` - Development guide

## Running the Project

### Install
```bash
pip install -e ".[dev]"
```

### Run Tests
```bash
pytest --cov=quotarouter
```

### Code Quality
```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

### Run Examples
```bash
python examples/01_basic_completion.py
python examples/02_streaming.py
```

## File Purposes

### Core Package (`src/quotarouter/`)
- **Clean, modular, extensible**
- No business logic in single monolithic file
- Clear separation of concerns
- Easy to test each component

### Tests (`tests/`)
- Comprehensive unit tests
- Mock external dependencies
- >80% code coverage
- Fast, isolated tests

### Documentation (`docs/`)
- API reference
- Architecture patterns
- Design decisions
- Extension points

### Examples (`examples/`)
- Real-world usage
- Copy-paste ready code
- Progressive complexity
- Common patterns

### Configuration
- `pyproject.toml`: Modern Python config
- `setup.py`: For backward compatibility
- `pytest.ini`: Test runner config
- `requirements*.txt`: Dependency lists
- `.gitignore`: Git rules
- `.env.example`: API key template

## Next Steps

1. **Get Started**: Read [GETTING_STARTED.md](GETTING_STARTED.md)
2. **Learn API**: Check [docs/API.md](docs/API.md)
3. **Understand Design**: Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
4. **Run Examples**: Try `examples/`
5. **Contribute**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**This is a professional, production-ready open-source project! 🚀**
