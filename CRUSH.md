# Smart Search Commands & Style Guide

## Build/Run Commands
```bash
# Install dependencies
uv sync

# Run full application (FastAPI + Reflex UI)
uv run python run.py

# CLI search
uv run python -m cli.smart_search "query" [--depth shallow|medium|deep] [--confidence 70-100]

# Run API server only
uv run python -m uvicorn api.main:app --reload --port 8000

# Reflex UI only (cd reflex_app first)
uv run python -m reflex run
```

## Testing Commands
```bash
# Run all tests
uv run pytest tests/

# Run single test file
uv run pytest tests/test_cli.py

# Run specific test
uv run pytest tests/test_cli.py::test_cli_help -v

# Manual CLI test
python tests/test_cli.py
```

## Code Style Guidelines
- **Framework**: Agno (phidata) for AI agents, FastAPI for backend, Reflex for frontend  
- **Python**: 3.12+, use type hints (from typing import Optional, List, Dict)
- **Async**: Use `async def` for FastAPI endpoints, regular functions for agents
- **Imports**: Group by stdlib, third-party, local. Use absolute imports from project root
- **Error Handling**: Wrap external API calls in try/except, log errors, failover gracefully
- **Config**: All API keys/env vars in `config.py` via `python-dotenv`
- **Agents**: Inherit from Agno Agent classes, use OpenAI models via OpenRouter (primary) or OpenAI (fallback)
- **Models**: Default to `gpt-4o-mini`, configurable in `config.py`
- **Search**: Use DuckDuckGo + Serper APIs, LanceDB for vector storage, Cohere for reranking
- **Memory**: AgentMemory for conversation history, user profiles in `data/user_profiles/`
- **Testing**: Assert patterns, subprocess for CLI tests, pytest for unit tests
- **CLI**: Use argparse, support JSON/text output, interactive mode flag
- **Logging**: Print status messages to console (🚀, ✅, 🎉), errors to stderr