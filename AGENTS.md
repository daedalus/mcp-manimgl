# AGENTS.md — mcp-manimgl

## Overview

MCP server that exposes manimgl (Manim OpenGL) functionality as tools for LLMs. Enables AI agents to create mathematical animations programmatically through MCP tools.

## Commands

| Command | Description |
|---------|------------|
| `pytest` | Run test suite |
| `ruff format` | Format code |
| `prospector --with-tool ruff --with-tool mypy src/` | Lint + type check |
| `semgrep --config=auto src/` | Security and pattern scanning (install separately: `pip install semgrep`) |
| `vulture --min-confidence 90 src/` | Dead/unused code detection |

## Development

```bash
pip install -e ".[test]"
pytest
ruff format src/ tests/
prospector --with-tool ruff --with-tool mypy src/
pip install semgrep && semgrep --config=auto --severity=ERROR src/  # semgrep not included in [lint] due to mcp version conflict
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

## Development Server (with Auto-Reload)

During development, start the server with `--reload` to automatically pick up source changes:

```bash
mcp-manimgl --reload
```

This uses `watchfiles` to monitor the src/ directory and restarts the server whenever a `.py` file changes. Install with:

```bash
pip install watchfiles
```

Without `--reload`, you must restart the server manually after editing source files (e.g., `audio_mixer.py`, `scene_manager.py`).

## Known Bugs

1. **Audio mixer double-bracket bug** (`src/mcp_manimgl/utils/audio_mixer.py`): ffmpeg filter labels include `[]` brackets, producing `[[label]]` syntax error. Fixed in source but requires server restart.
2. **Custom code indentation stripping** (`src/mcp_manimgl/core/scene_manager.py`): `line.strip()` flattens all indentation. Fixed in source but requires server restart.
3. **Narration timing misalignment**: The `get_audio_manifest()` start_times reflect event order, not visual section boundaries. Narrations overlap when mixed via manifest times. Fix: compute section-aligned delays manually via ffmpeg.
