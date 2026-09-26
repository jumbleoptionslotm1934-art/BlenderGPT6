# GPT Blend

AI-powered Blender add-on for OpenAI GPT models. Control Blender with natural language for 3D modeling, mesh editing, materials, cameras, lighting, animation, rendering, and scene automation.

![Blender](https://img.shields.io/badge/Blender-5.2%2B-orange?logo=blender&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--6-412991?logo=openai&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

GPT Blend is a Blender AI assistant, BlenderGPT-style add-on, and OpenAI Blender plugin that lets an AI agent inspect and modify Blender through structured tools instead of only generating Python scripts.

## Highlights

- GPT-6 Astra, GPT-6 Sol, and GPT-6 Luna are supported through the OpenAI API.
- Also supports the current GPT-5.6 Sol, GPT-5.6 Terra, and GPT-5.6 Luna API models for compatibility across the current GPT flagship families.
- 70 model-facing Blender tools covering modeling, mesh editing, materials, cameras, lighting, animation, constraints, collections, and rendering.
- Multi-step AI agent workflows using the OpenAI Responses API.
- Optional 3D Viewport image context so the model can reason about what is visible.
- Automatic verification of important Blender changes.
- Blender undo checkpoints and destructive-operation controls.
- Persistent multi-turn sessions, retry, cancellation, usage reporting, and live tool activity.
- Real Blender 5.2.2 LTS runtime tests for animation reliability.

## What people search for

GPT Blend is useful for people looking for:

- Blender AI
- Blender AI assistant
- BlenderGPT
- BlenderGPT alternative
- ChatGPT for Blender
- OpenAI Blender plugin
- AI Blender add-on
- Blender natural-language automation
- AI 3D modeling in Blender
- AI-assisted Blender animation
- Blender AI materials and shaders
- Blender AI camera and lighting setup
- Blender AI scene generation

## GPT Blend 0.8.0

GPT Blend 0.8.0 adds the GPT-6 model family to the Blender model picker while keeping the current GPT-5.6 family available.

### Current OpenAI models in GPT Blend

| Model | API ID |
| --- | --- |
| GPT-6 Astra | `gpt-6-astra` |
| GPT-6 Sol | `gpt-6-sol` |
| GPT-6 Luna | `gpt-6-luna` |
| GPT-5.6 Sol | `gpt-5.6-sol` |
| GPT-5.6 Terra | `gpt-5.6-terra` |
| GPT-5.6 Luna | `gpt-5.6-luna` |

OpenAI's current API model catalog lists GPT-6 Astra, GPT-6 Sol, and GPT-6 Luna as the GPT-6 flagship family, with GPT-5.6 Sol, Terra, and Luna also available in the API. GPT Blend uses the documented API IDs directly.

Official OpenAI model documentation:

- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/guides/latest-model

## Why GPT Blend?

Many Blender AI tools focus on generating a Python script and asking the user to execute it. GPT Blend instead exposes Blender as a structured tool environment to the model.

The agent can:

1. Inspect the current Blender scene.
2. Inspect individual objects and their materials/modifiers.
3. Read optional viewport image context.
4. Decide which Blender tools are needed.
5. Execute multiple operations.
6. Inspect the result and verify important changes.
7. Continue until the task is complete or a safety limit is reached.

This makes GPT Blend suitable for multi-step workflows such as building a scene, assigning materials, arranging objects, setting up lights and cameras, creating animation, and configuring render output.

## Blender AI capabilities

### Modeling and scene creation

- Create cubes, spheres, cylinders, cones, toruses, and planes.
- Transform, move, rotate, scale, rename, duplicate, delete, and select objects.
- Batch transforms.
- Arrange, align, and distribute objects.
- Parent objects.
- Create Empty helpers.
- Set object origins.
- Create and organize collections.
- Inspect scenes, objects, modifiers, materials, and collections.

### Mesh editing and modifiers

- Bevel
- Subdivision Surface
- Array
- Mirror
- Solidify
- Boolean
- Shrinkwrap
- Simple Deform
- Decimate
- Weighted Normal
- Remove modifiers
- Apply modifiers
- Join objects
- Vertex, edge, and face selection
- Mesh selection modes
- Merge vertices
- Dissolve mesh elements
- Face extrusion
- Smart Project and Angle Based UV unwrap

### Materials, shading, and procedural textures

- Create and update Principled BSDF materials.
- Set base color, metallic, and roughness.
- Set viewport display colors.
- Procedural Noise, Voronoi, Wave, and Brick textures.
- Procedural bump detail.
- Smooth and flat shading.
- Automatic Material Preview for relevant material operations.

### Cameras and cinematics

- Create cameras.
- Perspective, Orthographic, and Panoramic projection.
- Lens and orthographic scale.
- Clipping range.
- Sensor shift.
- Depth of field.
- Focus objects.
- Aim cameras or objects at other objects.
- Track To and Damped Track constraints.
- Copy Transforms constraints.

### Lighting

- Point lights
- Area lights
- Sun lights
- Spot lights
- Energy
- Color
- Shadow size
- Spot size and blend
- Sun angle
- World background

### Animation

- FPS and frame range.
- Object, camera, and light transform keyframes.
- Location, rotation, and scale animation.
- Keyframe interpolation.
- Animation inspection.
- Repeat, Offset, and Mirror cycle behavior.
- Timeline markers and camera markers.
- Viewport visibility animation.
- Render visibility animation.
- Clear existing animation.

GPT Blend's animation implementation has been tested against **Blender 5.2.2 LTS** using a real headless Blender runtime test covering action creation, F-Curves, keyframes, animation evaluation, visibility animation, inspection, and animation clearing.

### Rendering

- Render engine.
- Resolution.
- Resolution percentage.
- Frame rate.
- Output path.
- Still-image format.
- Transparent film.

## Example prompts

> Create a stylized low-poly castle with towers and a courtyard.

> Build a wooden table with four legs, bevel the edges, add a wood material, create an Area light, and set up a camera.

> Animate this object moving from frame 1 to frame 60 and make the animation loop.

> Inspect the selected object and explain its modifiers, materials, dimensions, and animation.

> Use the viewport image to identify the main model and improve the composition with a camera and lighting setup.

> Create a collection called Environment and organize the scene into Environment, Characters, and Props.

> Set the render to 1920x1080 at 60 FPS and enable transparent film.

## Installation

1. Download the GPT Blend extension ZIP from the latest successful GitHub Actions package build.
2. Open **Blender 5.2 or newer**.
3. Go to **Edit → Preferences → Get Extensions**.
4. Choose **Install from Disk**.
5. Select the GPT Blend `.zip` package.
6. Enable GPT Blend.
7. Open the 3D View Sidebar with **N**.
8. Open the **GPT Blend** panel.
9. Enter your OpenAI API key in Preferences.
10. Select GPT-6 Astra, GPT-6 Sol, GPT-6 Luna, or another supported GPT model.
11. Send a natural-language Blender request.

## Architecture

GPT Blend uses an OpenAI Responses API agent loop + structured Blender tools:

```text
Natural-language prompt
        ↓
Blender scene / optional viewport context
        ↓
OpenAI Responses API
        ↓
Model selects Blender tools
        ↓
Blender executes tools
        ↓
Tool results returned to the model
        ↓
Verification / additional tool calls
        ↓
Completed Blender workflow
```

Network/model work runs outside Blender's main UI execution path. Blender data mutations are marshalled onto Blender's main thread.

## Agent and safety controls

- Up to 100 model/tool continuation rounds by default.
- 150 total Blender tool calls by default.
- Optional repeated-call loop protection.
- Automatic retries for transient API/network failures.
- Destructive operations can be disabled in Preferences.
- Blender undo checkpoints are created before GPT-driven mutations when supported.
- Important operations can be automatically verified after execution.

These controls are intended to limit runaway tool loops and accidental destructive workflows. Important changes should still be reviewed by the user.

## Visual context

When enabled, GPT Blend can capture the active Blender 3D Viewport and send the image as additional model context.

Visual context can help with:

- object placement;
- scene composition;
- visible geometry;
- viewport state;
- visual troubleshooting;
- material and shading inspection.

## UI

The GPT Blend sidebar includes:

- Connection status
- Model selector
- Session state
- Tool-call count
- Elapsed time
- API token usage when available
- Chat history
- Live activity log
- Response display
- Send
- Stop
- Retry
- Copy Response
- New Chat
- Clear

Changing the selected model starts a model-specific session.

## Verification

GPT Blend can verify important changes after tool execution.

Examples include:

- animation → animation inspection;
- object mutation → object inspection;
- render/timeline changes → scene inspection.

Verification is counted toward the configured tool-call safety limit.

## Privacy and API keys

GPT Blend sends prompts and selected Blender scene/viewport context to the OpenAI API when you use it.

Never publish your OpenAI API key.

Do not send confidential information unless your privacy or organizational requirements permit that use.

## Troubleshooting

### Model/API error

Check the OpenAI API key, selected model, network connection, and whether that model is available to the OpenAI project.

### Blender animation error

Restart Blender after installing a new GPT Blend build so Blender loads the updated Python modules.

### Repeated tool calls

Enable loop protection and reduce the maximum agent rounds or total tool calls.

### Material changes are hard to see

Some material operations intentionally switch the viewport to Material Preview so the result is immediately visible.

## Developer structure

| Path | Purpose |
| --- | --- |
| `gptblend/core/client.py` | OpenAI Responses API client and tool loop |
| `gptblend/core/async_agent.py` | Worker-thread orchestration |
| `gptblend/tools/schemas.py` | Model-facing tool definitions |
| `gptblend/tools/blender_ops.py` | Blender tool implementations |
| `gptblend/tools/registry.py` | Tool registry |
| `gptblend/context/scene.py` | Scene context |
| `gptblend/context/viewport.py` | Viewport image capture |
| `gptblend/ui/operators.py` | Blender operators and polling |
| `gptblend/ui/panel.py` | Sidebar UI |
| `gptblend/preferences.py` | API/model/safety preferences |
| `tests/test_animation_runtime.py` | Blender runtime animation test |
| `tests/validate_tool_surface.py` | Tool/schema consistency test |
| `.github/workflows/validate.yml` | CI validation and packaging |

## CI

Every push and pull request runs Python validation plus a real Blender 5.2.2 runtime test.

The package job also validates the Blender extension manifest and builds an installable extension ZIP.

## Version

GPT Blend 0.8.0

Target Blender version: 5.2.0+

License: MIT

Repository: https://github.com/jumbleoptionslotm1934-art/GPTBlend

## Contributing

Bug reports should include the Blender version, GPT Blend version, selected model/API ID, exact prompt, and relevant error or tool output.

Never include an OpenAI API key in an issue, pull request, screenshot, or log.