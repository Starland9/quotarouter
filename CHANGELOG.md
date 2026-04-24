# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
