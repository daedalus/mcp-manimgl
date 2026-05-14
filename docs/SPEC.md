# SPEC.md — mcp-manimgl-server

## Purpose

An MCP (Model Context Protocol) server that exposes manimgl (Manim OpenGL) functionality as tools for LLMs. Enables AI agents to programmatically create mathematical animations, generate manim scene scripts, configure scenes, add and manipulate mobjects, apply animations, and render output videos/images.

## Scope

### What IS in scope
- Creating and configuring manimgl scenes
- Creating all major mobject types (shapes, graphs, text, 3D objects, etc.)
- Applying animations to mobjects (transform, fade, grow, rotate, shift, etc.)
- Rendering scenes to video files or single frames
- Generating executable Python manim scripts from tool calls
- Scene state management (add/remove mobjects, undo, clear)
- Camera configuration (position, orientation, resolution)
- Headless/offscreen rendering support
- Code generation for manimgl scenes

### What is NOT in scope
- A full manimgl REPL or interactive viewer
- Real-time streaming of rendered frames
- Audio/sound integration
- Advanced shader customization
- Full LaTeX editor (beyond Tex mobject creation)
- Direct mouse/keyboard event simulation
- GUI scene builder

## Public API / Interface

### Server Entry Points

```
mcp.run_stdio()  # Run MCP server with stdio transport
```

### MCP Tools

#### Scene Management
| Tool | Signature | Description |
|------|-----------|-------------|
| `create_scene` | `(background_color: str = "#333333", resolution: str = "1280x720", fps: int = 30, frame_height: float = 8.0) -> SceneInfo` | Create a new scene with config |
| `get_scene_info` | `() -> SceneInfo` | Get current scene config and element count |
| `clear_scene` | `() -> bool` | Remove all mobjects from scene |
| `add_wait` | `(duration: float = 1.0) -> bool` | Add a wait period to the scene |
| `save_state` | `() -> bool` | Save current scene state |
| `restore_state` | `() -> bool` | Restore previously saved state |
| `set_camera` | `(position: str = None, orientation: list[float] = None, frame_height: float = None) -> bool` | Configure camera |

#### Mobject Creation
| Tool | Signature | Description |
|------|-----------|-------------|
| `add_circle` | `(radius: float = 1.0, color: str = "#FFFFFF", fill_opacity: float = 0.0, stroke_width: float = 4.0, position: list[float] = None) -> MobjectInfo` | Add a circle |
| `add_square` | `(side_length: float = 2.0, ...) -> MobjectInfo` | Add a square |
| `add_rectangle` | `(width: float = 4.0, height: float = 2.0, ...) -> MobjectInfo` | Add a rectangle |
| `add_polygon` | `(vertices: list[list[float]], ...) -> MobjectInfo` | Add a polygon |
| `add_line` | `(start: list[float], end: list[float], ...) -> MobjectInfo` | Add a line |
| `add_arrow` | `(start: list[float], end: list[float], ...) -> MobjectInfo` | Add an arrow |
| `add_dot` | `(point: list[float] = None, color: str = "#FFFFFF", radius: float = 0.1) -> MobjectInfo` | Add a dot |
| `add_text` | `(text: str, font_size: float = 48, color: str = "#FFFFFF", font: str = "Consolas") -> MobjectInfo` | Add text mobject |
| `add_tex` | `(tex_string: str, font_size: float = 48, color: str = "#FFFFFF") -> MobjectInfo` | Add LaTeX math |
| `add_function_graph` | `(function: str, x_range: list[float] = None, color: str = "#FFFF00") -> MobjectInfo` | Graph a function |
| `add_parametric_curve` | `(function: str, t_range: list[float] = None, color: str = "#FFFFFF") -> MobjectInfo` | Parametric curve |
| `add_coordinate_system` | `(x_range: list[float] = None, y_range: list[float] = None, axis_config: dict = None) -> MobjectInfo` | Axes/number plane |
| `add_vector` | `(vector: list[float], color: str = "#FFFFFF") -> MobjectInfo` | Vector arrow |
| `add_labeled_point` | `(label: str, point: list[float], color: str = "#FFFFFF", dot_radius: float = 0.1) -> MobjectInfo` | Point with label |
| `add_3d_object` | `(object_type: str, ...) -> MobjectInfo` | 3D object (sphere, cube, torus, etc.) |
| `add_brace` | `(mobject_id: str, direction: str = "DOWN") -> MobjectInfo` | Brace labeling |

#### Mobject Manipulation
| Tool | Signature | Description |
|------|-----------|-------------|
| `move_to` | `(mobject_id: str, position: list[float], aligned_edge: str = None) -> bool` | Move mobject to position |
| `shift` | `(mobject_id: str, vector: list[float]) -> bool` | Shift mobject by vector |
| `scale` | `(mobject_id: str, scale_factor: float, about_point: list[float] = None) -> bool` | Scale mobject |
| `rotate` | `(mobject_id: str, angle: float, axis: list[float] = None, about_point: list[float] = None) -> bool` | Rotate mobject |
| `set_color` | `(mobject_id: str, color: str) -> bool` | Set mobject color |
| `set_opacity` | `(mobject_id: str, opacity: float) -> bool` | Set mobject opacity |
| `align_to` | `(mobject_id: str, reference_id: str, direction: str) -> bool` | Align to another mobject |
| `next_to` | `(mobject_id: str, reference_id: str, direction: str = "RIGHT", buff: float = 0.25) -> bool` | Position next to another |

#### Animation
| Tool | Signature | Description |
|------|-----------|-------------|
| `animate_transform` | `(mobject_id: str, target_mobject_type: str = None, target_config: dict = None, run_time: float = 1.0, rate_func: str = "smooth") -> bool` | Transform to new shape |
| `animate_fade_in` | `(mobject_id: str, run_time: float = 1.0, shift_direction: list[float] = None) -> bool` | Fade in |
| `animate_fade_out` | `(mobject_id: str, run_time: float = 1.0) -> bool` | Fade out |
| `animate_grow` | `(mobject_id: str, grow_type: str = "center", run_time: float = 1.0) -> bool` | Grow animation |
| `animate_rotate` | `(mobject_id: str, angle: float = None, run_time: float = 1.0) -> bool` | Rotate animation |
| `animate_scale` | `(mobject_id: str, scale_factor: float, run_time: float = 1.0) -> bool` | Scale animation |
| `animate_shift` | `(mobject_id: str, vector: list[float], run_time: float = 1.0) -> bool` | Shift animation |
| `animate_indicate` | `(mobject_id: str, run_time: float = 0.5) -> bool` | Highlight/indicate |
| `animate_write` | `(mobject_id: str, run_time: float = 3.0) -> bool` | Show creation (write effect) |
| `animate_set_color` | `(mobject_id: str, color: str, run_time: float = 1.0) -> bool` | Animate color change |
| `animate_move_along_path` | `(mobject_id: str, path_type: str, path_config: dict, run_time: float = 3.0) -> bool` | Move along path |
| `animate_group` | `(animation_data: list[dict], group_type: str = "animation_group", run_time: float = 1.0) -> bool` | Group animations together |

#### Advanced
| Tool | Signature | Description |
|------|-----------|-------------|
| `add_custom_code` | `(code_snippet: str, insert_point: str = "before_render") -> bool` | Inject custom Python code |
| `generate_scene_script` | `(download: bool = False) -> str` | Get full generated Python script |
| `render_scene` | `(output_path: str = None, format: str = "mp4") -> dict` | Render scene to file |
| `save_frame` | `(output_path: str = None) -> dict` | Save single frame |
| `set_config` | `(config: dict) -> bool` | Set global rendering config |

### Data Structures

```python
class SceneInfo(TypedDict):
    scene_id: str
    background_color: str
    resolution: tuple[int, int]
    fps: int
    frame_height: float
    mobject_count: int
    animation_count: int
    has_rendered: bool

class MobjectInfo(TypedDict):
    mobject_id: str
    mobject_type: str
    color: str
    position: list[float]
    properties: dict

class AnimationInfo(TypedDict):
    animation_id: str
    animation_type: str
    mobject_id: str
    run_time: float
    rate_func: str
    properties: dict
```

## Data Formats

- **Colors**: Hex strings ("#RRGGBB" or "#RRGGBBAA") or named manim colors ("RED", "BLUE", "GREEN", etc.)
- **Positions/Vectors**: 3-element float lists [x, y, z]
- **Angles**: Radians (float)
- **Resolutions**: "WxH" string format, e.g. "1920x1080"
- **Functions**: Python expression strings using 'x' or 't' as variable, e.g. "x**2" or "sin(t)"
- **Rate Functions**: Strings matching manim rate functions: "smooth", "linear", "ease_in_sine", "ease_out_sine", "ease_in_out_sine", "ease_in_quad", etc.
- **Directions**: Strings matching direction constants: "UP", "DOWN", "LEFT", "RIGHT", "IN", "OUT", "UL", "UR", "DL", "DR", "ORIGIN"

## Edge Cases

1. **Empty scene rendering**: Render a scene with no mobjects should produce an empty frame (not crash)
2. **Invalid mobject ID**: Operations on non-existent mobject IDs should return error
3. **Overlapping animations**: Multiple animations on same mobject should compose gracefully
4. **Zero run_time**: Animations with run_time=0 should complete instantly
5. **Negative scale**: Scale with negative values should mirror the mobject
6. **Out-of-bounds positions**: Mobjects positioned far outside frame should not crash renderer
7. **Unicode in text**: Unicode strings in Text mobjects should render without error
8. **Invalid LaTeX**: Invalid TeX strings should return an error message, not crash
9. **Memory cleanup**: Creating many scenes should not leak memory
10. **Offscreen rendering**: Must work in headless/server environments (no display)

## Performance & Constraints

- Scene state is stored in-memory; mobject count should ideally stay under 10,000
- Rendering is the primary bottleneck; single frame renders should complete in < 30s for typical scenes
- The server must work with Python 3.11+
- Cannot depend on display hardware; must support EGL/osmesa for headless rendering
- Generated Python scripts should be valid and runnable independently of the MCP server
