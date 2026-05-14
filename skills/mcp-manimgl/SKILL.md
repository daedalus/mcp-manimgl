name: mcp-manimgl
description: >
  MCP server that exposes manimgl (Manim OpenGL) functionality as tools for LLMs.
  Enables AI agents to create mathematical animations programmatically through MCP tools.
  Triggers on: manim, manimgl, mathematical animation creation.
---

# mcp-manimgl Skill

## Description

This MCP server provides tools for creating mathematical animations using manimgl (Manim OpenGL) through an MCP interface. It allows LLMs to build scenes programmatically by creating mobjects (geometric shapes, text, graphs, 3D objects), applying animations, configuring cameras, and rendering to video.

## Usage

The server exposes tools organized into categories:
- **Scene Management**: create_scene, clear_scene, set_camera, add_wait, save/restore state
- **Mobject Creation**: add_circle, add_square, add_text, add_tex, add_function_graph, add_3d_object, etc.
- **Mobject Manipulation**: move_to, shift, scale, rotate, set_color, etc.
- **Animation**: animate_fade_in, animate_grow, animate_transform, animate_rotate, etc.
- **Rendering**: render_scene, save_frame, generate_scene_script

## Examples

1. Create a scene with a red circle that grows in:
   - create_scene("#1a1a2e", "1920x1080", 60)
   - add_circle(2.0, "#FF0000", 0.5, 2.0)
   - animate_grow(m_id, "center", 1.0)
   - add_wait(2.0)
   - render_scene()

2. Graph a function with coordinate axes:
   - create_scene()
   - add_coordinate_system([-5, 5, 1], [-3, 3, 1])
   - add_function_graph("sin(x)", [-5, 5, 0.05], "#FFFF00")
   - animate_write(graph_id, 3.0)
   - add_wait(1.0)
   - render_scene()
