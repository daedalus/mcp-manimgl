# AGENTS.md — mcp-manimgl

## Overview

MCP server that exposes manimgl (Manim OpenGL) functionality as tools for LLMs. Enables AI agents to create mathematical animations programmatically through MCP tools.

## Commands

| Command | Description |
|---------|------------|
| `pytest` | Run test suite |
| `ruff format` | Format code |
| `prospector --with-tool ruff --with-tool mypy src/` | Lint + type check |
| `semgrep --config=auto src/` | Security and pattern scanning |
| `vulture --min-confidence 90 src/` | Dead/unused code detection |

## Development

```bash
pip install -e ".[test]"
pytest
ruff format src/ tests/
prospector --with-tool ruff --with-tool mypy src/
semgrep --config=auto --severity=ERROR src/
vulture --min-confidence 90 src/
```

## Testing

Tests cover:
- Scene manager: init, state, mobject/animation lifecycle, save/restore, script generation
- Mobject builder: every mobject type, edge cases (unicode, custom positions, uniqueness)
- Animation builder: every animation type, edge cases (zero time, negative scale, groups)
- Integration: combined mobject + animation flows

## Code Style

- Format: ruff format
- Lint + Type check: prospector (ruff check + mypy + pylint)
- Docstrings: Google style

## Release

```bash
bumpversion patch  # or minor/major
git tag v<version>
git push && git push --tags
```

## MCP Server

```bash
pip install mcp-manimgl
```

Add to your `mcp.json`:

```json
{
  "mcpServers": {
    "mcp-manimgl": {
      "command": "mcp-manimgl"
    }
  }
}
```
