**mcp-manimgl-server** — MCP server exposing manimgl (Manim OpenGL) mathematical animation functionality as tools for LLMs.

[![PyPI](https://img.shields.io/pypi/v/mcp-manimgl-server.svg)](https://pypi.org/project/mcp-manimgl-server/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-manimgl-server.svg)](https://pypi.org/project/mcp-manimgl-server/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/master/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

mcp-name: io.github.dclavijo/mcp-manimgl-server

## Install

```bash
pip install mcp-manimgl-server
```

Requires manimgl system dependencies (pangocairo, OpenGL). See [manimgl docs](https://github.com/3b1b/manim).

## Usage

### MCP Server

```bash
# Run with stdio transport (default for MCP)
mcp-manimgl-server
```

### In Claude Desktop / Cursor / MCP clients

Add to your `mcp.json`:

```json
{
  "mcpServers": {
    "mcp-manimgl-server": {
      "command": "mcp-manimgl-server"
    }
  }
}
```

### Programmatic Scene Building (Generated Script Example)

```python
from manimlib import *
import numpy as np

class GeneratedScene(Scene):
    def construct(self):
        m_circle = Circle(radius=2.0, color='#FF0000', fill_opacity=0.5, stroke_width=2.0)
        m_circle.move_to(ORIGIN)
        self.add(m_circle)
        self.play(FadeIn(m_circle, run_time=1.0))
        self.wait(2.0)
```

## Tools

The server exposes these tool categories:

### Scene Management
- `create_scene` - Create/configure a new scene
- `clear_scene` - Remove all elements
- `add_wait` - Add wait/pause
- `set_camera` - Configure camera
- `save_state` / `restore_state` - State management
- `generate_scene_script` - Get the generated Python script

### Mobject Creation
- `add_circle`, `add_square`, `add_rectangle`, `add_polygon`
- `add_line`, `add_arrow`, `add_dot`
- `add_text`, `add_tex` (LaTeX)
- `add_function_graph`, `add_parametric_curve`
- `add_coordinate_system`, `add_vector`
- `add_labeled_point`, `add_brace`, `add_number_line`
- `add_decimal_number`, `add_matrix`
- `add_3d_object` (sphere, cube, torus, cone, cylinder)

### Mobject Manipulation
- `move_to`, `shift`, `scale`, `rotate`
- `set_color`, `set_opacity`
- `next_to`, `align_to`

### Animations
- `animate_transform`, `animate_fade_in/out`, `animate_grow`
- `animate_rotate`, `animate_scale`, `animate_shift`
- `animate_indicate`, `animate_write`, `animate_set_color`
- `animate_move_along_path`, `animate_group`

### Rendering
- `render_scene` - Render to video
- `save_frame` - Save single frame
- `get_render_status` - Check environment

## Development

```bash
git clone https://github.com/dclavijo/mcp-manimgl-server.git
cd mcp-manimgl-server
pip install -e ".[test]"

# run tests
pytest

# format
ruff format src/ tests/

# lint + type check
prospector --with-tool ruff --with-tool mypy src/

# security scan
semgrep --config=auto --severity=ERROR src/

# find unused code
vulture --min-confidence 90 src/
```

## MCP

mcp-name: io.github.dclavijo/mcp-manimgl-server
