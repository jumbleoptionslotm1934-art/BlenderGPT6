# GPT Blend

AI-powered Blender add-on for connecting Blender to OpenAI GPT models.

## GPT Blend 0.5.2

GPT Blend uses OpenAI function calling to let the selected GPT model operate Blender through a structured tool layer instead of returning only Python code.

### Agent improvements

- Up to **100 model/tool continuation rounds** per request by default.
- A separate **150 total tool-call safety cap** by default.
- Optional repeated-call loop protection.
- Automatic retries for transient network/API failures.
- Persistent multi-turn sessions using the Responses API response chain.
- Model-specific sessions: changing models starts a new session automatically.
- Manual **New Chat** control.
- Persistent in-panel chat history.
- Live agent/tool activity log with tool-call count.
- Clean cancellation and session reset.
- Optional active viewport screenshot sent with each new prompt for visual reasoning.
- Blender undo checkpoints before GPT-driven edits.

### Scene and object control

- Inspect the scene.
- Inspect individual objects.
- Create cubes, spheres, cylinders, cones, toruses, and planes.
- Transform objects.
- Move objects by relative offsets.
- Rotate objects by relative angles.
- Set exact object dimensions.
- Apply object scale.
- Rename objects.
- Duplicate objects.
- Delete objects when explicitly requested.
- Select multiple objects.
- Batch-transform objects.
- Arrange objects in a line.
- Align objects.
- Distribute objects evenly.
- Hide/unhide objects.
- Change render visibility.
- Parent objects.
- Create Empty helpers.
- Set object origins.

### Materials and shading

- Create/update Principled materials.
- Assign base color, metallic, and roughness.
- Set viewport display colors.
- Procedural Noise, Voronoi, Wave, and Brick textures with optional bump detail.
- Automatic Material Preview when GPT assigns a material or procedural texture.
- Smooth or flat shade meshes.

### Modeling and modifiers

- Bevel.
- Subdivision Surface.
- Array.
- Mirror.
- Solidify.
- Boolean.
- Shrinkwrap.
- Simple Deform.
- Decimate.
- Weighted Normal.
- Remove modifiers.
- Apply modifiers.
- Join objects.
- Create Bezier curves.
- Create 3D text.
- Select mesh vertices, edges, and faces.
- Set mesh selection mode.
- Merge selected vertices.
- Dissolve selected mesh elements.
- Extrude selected faces.
- Smart Project or Angle Based UV unwrap.

### Scene organization

- Create collections.
- Move objects between collections.
- Inspect collection membership.

### Lighting and cameras

- Create Point, Area, Sun, and Spot lights.
- Create cameras.
- Make a camera the active scene camera.
- Aim an object or camera at another object.
- Change the world background.

### Animation

- Configure FPS and frame range.
- Create explicit object, camera, and light transform keyframes.
- Choose interpolation per keyframe or across an existing action.
- Inspect authored animation actions and keyframes.
- Clear existing object animation.

### Rendering

- Configure render engine.
- Configure resolution.
- Configure resolution percentage.
- Configure frame rate.

The tool layer currently contains **59 model-facing Blender tools**.

## Installation

1. Download the repository and package it as a Blender extension.
2. Install it from Blender Preferences > Get Extensions > Install from Disk.
3. Enable GPT Blend.
4. Open the 3D View sidebar (N) and select GPT Blend.
5. Configure your OpenAI API key in Preferences.

Never commit your API key.

## Example prompts

- "Build a simple wooden table with four legs and a beveled top."
- "Arrange these five objects in a row with 2 meters between each."
- "Make the selected object blue, metallic, slightly rough, and smoothly shaded."
- "Mirror this mesh across X and add a small bevel."
- "Use this object as a Boolean cutter and subtract it from the main mesh."
- "Create an Area light above the scene, point it at the model, and set up a camera."
- "Create a collection called Environment and organize the scene into it."
- "Set the render to 1920x1080 at 60 FPS."
- "Inspect the selected object and tell me what modifiers and materials it has."
- "Create a New Chat and start a completely different task."

## Safety and scope

GPT Blend uses structured Blender operations rather than unrestricted generated Python. The model is instructed to avoid unnecessary edits and never delete objects unless the user explicitly requests deletion.

Mutating GPT operations create Blender undo checkpoints when Blender permits them.

GPT Blend can include an active 3D Viewport screenshot as multimodal input when enabled in Preferences.

Network/model generation now runs off Blender's main thread. Blender tool calls that modify Blender data are marshalled back to Blender's main thread, keeping the UI responsive while GPT is thinking. A heavy Blender operation itself can still temporarily occupy the main thread, but waiting on the OpenAI API no longer freezes the interface.

## Development

Keep Blender-specific operations in `gptblend/tools/blender_ops.py` and their model-facing JSON schemas in `gptblend/tools/schemas.py`. The registry connects the two layers.

Never commit an API key.
