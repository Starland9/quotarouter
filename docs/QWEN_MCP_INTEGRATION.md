# Qwen Code MCP Integration

## Overview

QuotaRouter now integrates with Qwen Code through a Model Context Protocol (MCP) server, enabling intelligent LLM provider routing with quota management.

### Features

✅ **Multi-Provider Support** - OpenAI, Anthropic, Google, Alibaba DashScope, and any OpenAI-compatible API
✅ **Quota Management** - Automatic quota tracking and provider fallback
✅ **Interactive CLI** - User-friendly terminal interface for chat and code operations
✅ **Agentic Interface** - Agent wrapper for programmatic usage
✅ **Code Tools** - Built-in analysis, testing, refactoring, and explanation tools
✅ **Session Management** - Multi-session support for parallel conversations
✅ **Streaming Support** - Real-time response streaming

## Installation

### Basic Setup

```bash
# Install with Qwen Code support
pip install quotarouter[qwen]

# Or install everything
pip install quotarouter[all]
```

### Dependencies

- `httpx>=0.24.0` - For async HTTP requests
- `pydantic>=2.0.0` - For configuration management

## Quick Start

### Interactive CLI

```bash
# Launch interactive Qwen Code agent
python -m quotarouter.cli.qwen_integration

# Or run the example
python examples/08_qwen_mcp_integration.py
```

### Configuration

First time setup will prompt you to configure a provider:

```
Choose provider protocol:
1. openai
2. anthropic
3. gemini

Select (1-3): 1

Enter model ID (e.g., qwen3.6-plus): qwen3.6-plus
Enter provider name (e.g., Qwen): Qwen
Enter API base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
Enter environment variable name for API key: DASHSCOPE_API_KEY
```

Configuration is saved to `~/.qwen/settings.json`

## Usage

### Interactive Commands

```
/help              Show help message
/models            List available models
/select <id>       Switch to a model
/auth              Setup new provider
/sessions          List all sessions
/session new       Create new session
/session switch <id>  Switch to session
/analyze [lang]    Analyze code
/tests [lang]      Generate tests
/refactor [lang]   Refactor code
/explain [lang]    Explain code
/clear             Clear conversation
/history           Show conversation history
/exit              Exit program
```

### Programmatic Usage

#### Simple Chat

```python
import asyncio
from quotarouter.agents import QwenAgent

async def main():
    agent = QwenAgent()
    
    # Get available models
    models = agent.get_available_models()
    agent.set_model(models[0]['id'])
    
    # Chat
    response = await agent.chat("What is Python?")
    print(response)

asyncio.run(main())
```

#### With Quota Routing

```python
import asyncio
from quotarouter.core.router import FreeRouter
from quotarouter.agents import QwenAgent

async def main():
    # Create router for quota management
    router = FreeRouter()
    
    # Create agent with routing
    agent = QwenAgent(router)
    agent.set_model("qwen3.6-plus")
    
    # Chat (uses router for quota management)
    response = await agent.chat("Explain async programming")
    print(response)

asyncio.run(main())
```

#### Code Analysis Tools

```python
# Analyze code
code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

result = await agent.analyze_code(code, language="python")
print(result)

# Generate tests
tests = await agent.generate_tests(code)
print(tests)

# Refactor code
refactored = await agent.refactor_code(code, improvements=["optimize", "add type hints"])
print(refactored)

# Explain code
explanation = await agent.explain_code(code)
print(explanation)
```

#### Multi-Session

```python
from quotarouter.agents import AgentSessionManager

# Create session manager
manager = AgentSessionManager()

# Create sessions
agent1 = manager.create_session("session1")
agent2 = manager.create_session("session2")

# Chat in different sessions
await agent1.chat("Hello from session 1")
await agent2.chat("Hello from session 2")

# Switch sessions
manager.switch_session("session1")
current = manager.get_current_session()
```

### MCP Server

```python
import asyncio
from quotarouter.mcp import QwenCodeMCPServer

async def main():
    # Create MCP server
    mcp = QwenCodeMCPServer()
    
    # Get list of providers
    providers = mcp.get_available_providers()
    print(providers)
    
    # Complete request
    response = await mcp.complete(
        prompt="What is Machine Learning?",
        model="qwen3.6-plus"
    )
    print(response['text'])
    
    # Stream response
    async for chunk in mcp.stream(
        prompt="Explain neural networks",
        model="qwen3.6-plus"
    ):
        print(chunk['text'], end='', flush=True)

asyncio.run(main())
```

## Configuration File

### Location
`~/.qwen/settings.json`

### Example Configuration

```json
{
  "modelProviders": {
    "openai": [
      {
        "id": "qwen3.6-plus",
        "name": "Qwen3.6-Plus",
        "baseUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "description": "Qwen3.6-Plus via Alibaba DashScope",
        "envKey": "DASHSCOPE_API_KEY"
      },
      {
        "id": "gpt-4o",
        "name": "OpenAI",
        "baseUrl": "https://api.openai.com/v1",
        "description": "GPT-4 Turbo",
        "envKey": "OPENAI_API_KEY"
      }
    ]
  },
  "security": {
    "auth": {
      "selectedType": "openai"
    }
  },
  "model": {
    "name": "qwen3.6-plus"
  }
}
```

### Configuration Options

- **modelProviders**: Object mapping protocol types to provider lists
  - `id`: Model identifier for the API
  - `name`: Display name
  - `protocol`: API protocol (openai, anthropic, gemini)
  - `baseUrl`: API endpoint URL
  - `envKey`: Environment variable for API key
  - `description`: Provider description

- **security.auth.selectedType**: Default protocol to use

- **model.name**: Default model on startup

## API Keys

### Setting API Keys

Option 1: Environment Variable (Recommended)
```bash
export DASHSCOPE_API_KEY="sk-xxxxxxxx"
export OPENAI_API_KEY="sk-xxxxxxxx"
```

Option 2: .env file
```
DASHSCOPE_API_KEY=sk-xxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxx
```

Option 3: settings.json (Least secure, not recommended)
```json
{
  "env": {
    "DASHSCOPE_API_KEY": "sk-xxxxxxxx"
  }
}
```

## Examples

### Example 1: Interactive Chat

```bash
$ python examples/08_qwen_mcp_integration.py
🦞 Qwen Code Interactive Agent

📦 Available Models:
  • qwen3.6-plus      (openai) - Qwen3.6-Plus via Alibaba DashScope ⭐
  • gpt-4o            (openai) - GPT-4 Turbo

🤖 Qwen [qwen3.6-plus] > What are generators in Python?
⏳ Thinking...

Generators in Python are functions that return an iterator object which produces...
```

### Example 2: Code Analysis

```bash
$ python examples/08_qwen_mcp_integration.py --script

🔄 Streaming response...
Generators in Python are functions that return an iterator object...
```

### Example 3: With Routing

```bash
$ python examples/08_qwen_mcp_integration.py --with-routing

🔀 Qwen Code with QuotaRouter Integration
Active provider: Cerebras
Total tokens used: 1234
```

## Supported Providers

### OpenAI-Compatible
- Alibaba Cloud ModelStudio / DashScope
- OpenAI
- OpenRouter
- Fireworks AI
- ModelScope
- Any OpenAI-compatible endpoint

### Other Protocols
- Anthropic Claude
- Google Gemini
- Vertex AI

## Architecture

```
QuotaRouter
├── MCP Server (QwenCodeMCPServer)
│   ├── Configuration (QwenConfig)
│   ├── Provider Management
│   └── API Communication
├── Agent Wrapper (QwenAgent)
│   ├── Chat Interface
│   ├── Code Tools
│   └── Session Management
└── CLI (QwenCLI)
    ├── Interactive Commands
    ├── Configuration Setup
    └── User Interface
```

## Troubleshooting

### No API Key Found
```
Error: No API key for qwen3.6-plus
```
Set the environment variable:
```bash
export DASHSCOPE_API_KEY="your-key"
```

### Provider Not Configured
```
❌ No providers configured. Running setup...
```
Run setup again:
```
/auth
```

### Connection Timeout
- Check API endpoint URL
- Verify network connectivity
- Check API key validity

### Model Not Found
```
Model qwen3.6-plus not found
```
Use `/models` to see available models and `/select <id>` to switch

## Best Practices

1. **Store API Keys Securely** - Use environment variables, never commit to git
2. **Use Quota Routing** - Leverage QuotaRouter for automatic provider fallback
3. **Multi-Session** - Use different sessions for parallel tasks
4. **Monitor Usage** - Check `/stats` for quota information
5. **Code Tool Validation** - Verify AI-generated code before using in production

## Performance Tips

- Use streaming for large responses
- Set appropriate max_tokens to save quota
- Leverage code analysis tools to catch issues early
- Use session history for context in multi-turn conversations

## Contributing

To extend the integration:

1. Add new providers to configuration
2. Implement custom code tools in QwenAgent
3. Add new CLI commands to QwenCLI

## License

MIT - See LICENSE file for details

## Support

- GitHub Issues: https://github.com/Starland9/quotarouter/issues
- Documentation: https://github.com/Starland9/quotarouter/blob/main/docs/QWEN_MCP_INTEGRATION.md
