# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.0] - 2026-04-24

### Added
- **REST API Server** - FastAPI-based REST API for LLM routing:
  - `quotarouter api` command to launch the server (default: 0.0.0.0:8000)
  - Endpoints for completions, streaming, status, book generation, config
  - Server-Sent Events (SSE) streaming with NDJSON format
  - Auto-generated OpenAPI documentation (Swagger UI + ReDoc)
  - CORS middleware for cross-origin requests
  - Perfect for Chainlit, web apps, microservices integration
  - Examples: `quotarouter api`, `quotarouter api --port 9000 --reload`, `quotarouter api --workers 4`
  - Full documentation in docs/API_SERVER.md
- **Chainlit Chat App** - Real-time chat interface for QuotaRouter (examples/07_chainlit_integration.py):
  - Interactive LLM chat with real-time streaming responses
  - Provider status monitor with quota visualization
  - Command-based interface (`/status` to check quotas)
  - Beautiful chat UI with message history
  - One-click deployment
  - Run with: `chainlit run examples/07_chainlit_integration.py`
- **Python API Client** - Example integration code (examples/08_api_integration.py):
  - QuotaRouterClient class for easy API interaction
  - Examples for all endpoints
  - Streaming, book generation, status monitoring
  - Comprehensive usage patterns
- **API Dependencies** - Optional package extras:
  - Install with: `pip install quotarouter[api]` (FastAPI, Uvicorn, Pydantic)
  - Or install all: `pip install quotarouter[all]`
- **Modular CLI architecture** - Reorganized command-line interface:
  - Each command in its own module under `cli/commands/` for maintainability
  - Shared utilities in `cli/utils/` (error handling, Rich components)
  - New command registration pattern with explicit naming
  - Easy to add new commands without modifying existing ones
- **New `quotarouter book` command** - Write entire books with automatic retry:
  - Generate multiple chapters sequentially
  - Auto-retry failed chapters (configurable, default 3 retries)
  - Checkpoint after each successful chapter
  - Resume from last checkpoint if interrupted
  - Beautiful progress bar with chapter tracking
  - Markdown output with chapter structure
  - Provider fallback when quota exhausts
  - Usage: `quotarouter book "Title" --chapters 5 --chapter-length 2000 -o book.md`

### Changed
- CLI refactored from monolithic `cli.py` to modular `cli/` package structure
- Command names now clean (e.g., `quotarouter status` instead of derived from function names)
- CLI startup faster due to lazy imports within command modules
- Rich Console error handling improved (removed invalid `file=sys.stderr` parameter usage)
- All commands now use centralized error handling utilities

### Documentation
- Added docs/API_SERVER.md with complete API reference, examples, and deployment guides
- Updated docs/API.md with new REST API section including curl examples, Python examples, and Chainlit integration
- Added example files: 07_chainlit_integration.py, 08_api_integration.py
- Added pyproject.toml optional dependencies groups: `[api]`, `[chainlit]`, `[all]`

## [0.3.0] - 2026-04-24

### Added
- **Command-line interface (CLI)** with comprehensive commands:
  - `quotarouter status` - Show provider quota status with rich formatting
  - `quotarouter complete` - Send simple completion requests
  - `quotarouter stream` - Stream long responses with real-time output
  - `quotarouter config` - Display configuration and API key variables
  - `quotarouter reset` - Reset quota counters for testing
- Dependency injection of `.env` file at package import time
- Support for environment variable configuration without explicit `load_dotenv()`
- Rich library integration for beautiful CLI output (tables, panels, colors)
- CLI_GUIDE.md with comprehensive usage documentation
- Example script for CLI usage patterns
- Automatic help text for all commands

### Changed
- Dependencies: Added `typer[all]>=0.9.0` and `rich>=13.0.0`
- Package now loads `.env` automatically on import
- Console scripts entry point for `quotarouter` command

### Fixed
- Package discovery in `pyproject.toml` using `find` instead of explicit package list
- `.env` loading now supports comments and quoted values

### Documentation
- Added CLI_GUIDE.md with command reference and examples
- Added core development instructions in `.github/instructions/core-instructions.md`

## [0.2.0] - 2024-04-24

### Added
- Initial release of FreeRouter
- Multi-provider LLM routing with automatic quota management
- Support for 5 free-tier providers (Cerebras, Groq, Google AI, Mistral, OpenRouter)
- Streaming and non-streaming completion APIs
- Automatic provider fallback on quota exhaustion
- RPM rate limiting per provider
- Quota persistence to JSON file
- Comprehensive documentation and examples
- Unit tests with >80% coverage

### Features
- `FreeRouter.complete()` - Simple completion requests
- `FreeRouter.complete_stream()` - Streaming responses
- `FreeRouter.status()` - Quota monitoring
- Extensible architecture with pluggable adapters and storage
- Type hints for better IDE support
- Detailed logging for debugging

### Providers
- [Cerebras](https://www.cerebras.ai/) - Llama 3.1 70B (1M tokens/day)
- [Groq](https://groq.com/) - Llama 3.3 70B (500K tokens/day)
- [Google AI Studio](https://aistudio.google.com/) - Gemini 2.0 Flash (480K tokens/day)
- [Mistral AI](https://mistral.ai/) - Mistral Large (1B tokens/month)
- [OpenRouter](https://openrouter.ai/) - DeepSeek R1 (200K tokens/day)

---

## Release Guidelines

### Version Format
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes

### Before Release
- Update CHANGELOG.md
- Update version in `src/quotarouter/__init__.py`
- Run full test suite
- Update README if needed
- Tag commit with version

### Release Process
```bash
# Update version
# Update CHANGELOG
git add CHANGELOG.md src/quotarouter/__init__.py
git commit -m "chore: release v0.2.0"

# Tag release
git tag v0.2.0

# Push
git push origin main
git push origin --tags

# Build and publish
python -m build
twine upload dist/*
```

---

[Unreleased]: https://github.com/Starland9/quotarouter/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Starland9/quotarouter/releases/tag/v0.2.0
