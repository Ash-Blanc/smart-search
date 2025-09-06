# Smart Search CLI

A lightweight command-line interface for the Smart Search engine, providing fast access to AI-powered search capabilities without the overhead of a web interface.

## Features

- **Lightweight**: Minimal dependencies and fast execution
- **Same Backend**: Uses the same Agno + DSPy framework as the web app
- **Flexible Output**: Text or JSON output formats
- **Scripting Ready**: Perfect for automation and integration
- **Interactive Mode**: For extended search sessions
- **Personalization**: Maintains search history and preferences

## Installation

The CLI is included with the main Smart Search package. After installing the main package:

```bash
uv sync
```

## Usage

### Basic Search

```bash
# Simple search
python -m cli.smart_search "Latest developments in AI"

# Search with higher confidence threshold
python -m cli.smart_search "Quantum computing breakthroughs" --confidence 85

# Deep search
python -m cli.smart_search "Climate change solutions" --depth deep
```

### Output Formats

```bash
# JSON output
python -m cli.smart_search "Python best practices" --format json

# Save to file
python -m cli.smart_search "Machine learning trends" --output results.txt

# JSON output to file
python -m cli.smart_search "Space exploration" --format json --output results.json
```

### Interactive Mode

```bash
# Start interactive session
python -m cli.smart_search --interactive
```

### User Personalization

```bash
# Use specific user ID for personalization
python -m cli.smart_search "AI ethics" --user-id abc123

# Let the system generate a user ID (default)
python -m cli.smart_search "Latest research"
```

## Scripting Examples

### Bash Script

```bash
#!/bin/bash
# daily_search.sh

echo "Running daily research scans..."

python -m cli.smart_search "AI research papers today" --output ai_research.txt
python -m cli.smart_search "Tech news today" --output tech_news.txt

echo "Research scans complete!"
```

### Python Script

```python
#!/usr/bin/env python3
import subprocess
import json

def smart_search(query, confidence=70):
    result = subprocess.run([
        'python', '-m', 'cli.smart_search', query,
        '--format', 'json',
        '--confidence', str(confidence)
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        raise Exception(f"Search failed: {result.stderr}")

# Example usage
try:
    result = smart_search("Latest breakthroughs in renewable energy")
    print(f"Confidence: {result['confidence']}%")
    print(result['results'])
except Exception as e:
    print(f"Error: {e}")
```

## Performance

- **Startup Time**: < 1 second
- **Search Time**: 2-5 seconds (depending on depth)
- **Memory Usage**: ~30MB
- **Dependencies**: Uses existing Smart Search components

## Integration

The CLI can be easily integrated into:
- Shell scripts
- CI/CD pipelines
- Other Python applications
- Automation workflows
- Research tools