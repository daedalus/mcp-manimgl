**mcp-manimgl** — MCP server exposing manimgl (Manim OpenGL) mathematical animation functionality as tools for LLMs.

[![PyPI](https://img.shields.io/pypi/v/mcp-manimgl.svg)](https://pypi.org/project/mcp-manimgl/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-manimgl.svg)](https://pypi.org/project/mcp-manimgl/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/master/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

mcp-name: io.github.dclavijo/mcp-manimgl

## Install

```bash
pip install mcp-manimgl
```

Optional extras:

```bash
# For rendering (requires manimgl + system deps)
pip install "mcp-manimgl[render]"

# For audio narration + MIDI music support
pip install "mcp-manimgl[audio]"
```

Requires manimgl system dependencies (pangocairo, OpenGL). See [manimgl docs](https://github.com/3b1b/manim).

## Usage

### MCP Server

```bash
# Run with stdio transport (default for MCP)
mcp-manimgl
```

### In Claude Desktop / Cursor / MCP clients

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

## Tools

The server exposes these tool categories:

### Scene Management
- `create_scene` — Create/configure a new scene
- `clear_scene` — Remove all elements
- `add_wait` — Add wait/pause
- `set_camera` — Configure camera
- `set_config` — Set global rendering config
- `save_state` / `restore_state` — State management
- `generate_scene_script` — Get the generated Python script

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

### Audio
- `add_narration` — Generate TTS (gTTS) narration that plays at the current timeline position
- `add_background_music` — Add background music from audio files or **MIDI files** (auto-rendered via FluidSynth). Supports volume control, looping, and sidechain ducking during narration.

### Rendering
- `render_scene` — Render to video (auto-mixes background music + narration with ducking)
- `save_frame` — Save single frame
- `get_render_status` — Check environment

## Audio Features

### Narration

```python
# TTS narration at current timeline position
add_narration("Shor's algorithm factors large numbers in polynomial time.")
```

### Background Music

Accepts audio files (`.mp3`, `.wav`, `.ogg`) or MIDI files (`.mid`, `.midi`). MIDI files are rendered to audio using FluidSynth and the system SoundFont.

```python
# From an audio file
add_background_music("/path/to/music.mp3", volume=0.3, loop=True)

# From a MIDI file (auto-rendered)
add_background_music("/path/to/classical.mid", volume=0.2)

# With ducking configuration
add_background_music(
    "bach_chorale.mid",
    volume=0.25,
    loop=True,
    duck_threshold="-20dB",
    duck_ratio=6,
    duck_attack=0.05,
    duck_release=0.3,
)
```

When both background music and narration are present, `render_scene` automatically:
1. Renders the video without audio via manimgl
2. Places the music track (looped if needed) at the configured volume
3. Places each narration track at its timeline position
4. Applies sidechain compression so music volume ducks during narration
5. Composites everything into the final MP4 via ffmpeg

## MIDI Rendering

MIDI files are rendered using `pyfluidsynth` with a system SoundFont. On Debian/Ubuntu:

```bash
sudo apt install fluidr3mono-gm-soundfont libfluidsynth3
pip install "mcp-manimgl[audio]"
```

Auto-discovered SoundFont paths:
- `/usr/share/sounds/sf3/` (`.sf3`)
- `/usr/share/sounds/sf2/` (`.sf2`)
- `/usr/share/fluidr3mono-gm-soundfont/`

## Development

```bash
git clone https://github.com/dclavijo/mcp-manimgl.git
cd mcp-manimgl
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

mcp-name: io.github.dclavijo/mcp-manimgl
