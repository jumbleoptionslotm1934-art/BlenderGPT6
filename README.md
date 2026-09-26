# GPT Blend

AI-powered Blender add-on for connecting Blender to OpenAI GPT models.

## GPT Blend 0.7.0

GPT Blend uses OpenAI function calling to let the selected GPT model operate Blender through a structured tool layer instead of returning only Python code.

### Agent improvements

- Up to **100 model/tool continuation rounds** per request by default.
- A separate **150 total tool-call safety cap** by default.
- Optional repeated-call loop protection.
- Automatic retries for transient network/API failures.
- Persistent multi-turn sessions using the Responses API response chain.
- Retry the last failed/cancelled prompt without retyping it.
- Copy GPT responses directly to the system clipboard.
- Show API-reported token usage when available.
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
- Configure existing light energy, color, shadow size, spot settings, and sun angle.
- Create cameras.
- Configure existing camera projection, clipping, lens, and sensor shift.
- Make a camera the active scene camera.
- Aim an object or camera at another object.
- Change the world background.

### Animation

- Configure FPS and frame range.
- Create explicit object, camera, and light transform keyframes.
- Choose interpolation per keyframe or across an existing action.
- Inspect authored animation actions and keyframes.
- Loop animations with Repeat, Offset, or Mirror cycles.
- Add and remove timeline markers, including camera markers.
- Configure camera depth of field.
- Add Track To / Damped Track constraints.
- Add Copy Transforms constraints.
- Remove named constraints.
- Configure render output path, still-image format, and transparent film.
- Animate viewport/render visibility with hold-style keyframes.
- Clear existing object animation.

### Rendering

- Configure render engine.
- Configure resolution.
- Configure resolution percentage.
- Configure frame rate.

The tool layer currently contains **70 model-facing Blender tools**.

## Installation

### User installation

GPT Blend 0.7.0 is packaged as a real Blender extension ZIP.

1. Download the packaged `gptblend-0.7.0.zip` file from the latest successful **package** GitHub Actions run.
2. Open Blender 5.2 or newer.
3. Go to **Edit → Preferences → Get Extensions**.
4. Choose **Install from Disk**.
5. Select the GPT Blend `.zip` package.
6. Enable GPT Blend.
7. Open the 3D View sidebar with **N**.
8. Open the **GPT Blend** panel.
9. Add your OpenAI API key in Preferences.

### Developer installation

Clone the repository and work from the `gptblend/` extension directory. The repository also contains the runtime tests and CI packaging workflow.

### After upgrading

Restart Blender after installing a newer GPT Blend build. This ensures Blender unloads older Python modules and loads the updated animation/tool implementation.

---

## OpenAI and ChatGPT model support

GPT Blend talks to the OpenAI API; it is not a browser wrapper around the ChatGPT website.

OpenAI model availability changes over time. Current OpenAI documentation lists GPT-6 Astra and GPT-6 Sol/Luna in relevant ChatGPT Work and Codex experiences, while the OpenAI API documentation currently lists GPT-5.6 Sol, GPT-5.6 Terra, and GPT-5.6 Luna.

Official references:

- https://platform.openai.com/docs/models
- https://help.openai.com/en/articles/20001354-gpt-5-6

### GPT Blend 0.7.0 built-in model picker

| GPT Blend option | API model ID |
| --- | --- |
| GPT-5.6 Luna | `gpt-5.6-luna` |
| GPT-5.6 Sol | `gpt-5.6-sol` |
| GPT-5.6 Terra | `gpt-5.6-terra` |

GPT-6 Astra is a current ChatGPT model, but GPT Blend 0.7.0 does not expose an Astra API ID in its built-in model picker. ChatGPT product names and API model IDs are not automatically interchangeable.

This section should be kept up to date when OpenAI changes model IDs or availability.

---

## First-time configuration

After installation:

1. Enter your OpenAI API key in GPT Blend Preferences.
2. Select the model.
3. Choose the safety/tool limits appropriate for your workflow.
4. Open the GPT Blend sidebar panel.
5. Send a simple test prompt such as: **Create a cube at the origin.**

Useful safety preferences include:

- Maximum agent rounds
- Maximum total tool calls
- Loop protection
- Allow destructive operations
- Send viewport snapshot

Never commit or publicly share your OpenAI API key.

---

## Capabilities

GPT Blend 0.7.0 contains 70 model-facing Blender tools covering:

### Scene and objects

- Scene/object inspection
- Primitive creation
- Cameras, lights, text, curves, and Empty helpers
- Transform, rename, duplicate, delete, selection, parenting
- Batch transforms
- Linear arrangement, alignment, and distribution
- Visibility and render visibility
- Collections

### Materials and shading

- Principled materials
- Base color, metallic, roughness
- Object display colors
- Procedural Noise, Voronoi, Wave, and Brick textures
- Bump detail
- Viewport shading

### Modeling and mesh editing

- Bevel, Subdivision, Array, Mirror, Solidify
- Boolean, Shrinkwrap, Simple Deform
- Decimate and Weighted Normal
- Smooth/flat shading
- Join and origin operations
- Vertex/edge/face selection
- Merge, dissolve, extrude
- UV unwrapping

### Animation

- FPS and frame range
- Transform keyframes
- Location, rotation, and scale animation
- Keyframe interpolation
- Animation inspection
- Clear animation
- Viewport visibility animation
- Render visibility animation
- Loop/cycle modifiers
- Timeline markers

### Cameras and cinematics

- Perspective, Orthographic, and Panoramic cameras
- Lens and orthographic scale
- Clipping range
- Sensor shift
- Depth of field
- Focus objects
- Aim and tracking constraints

### Lighting

- Point, Area, Sun, and Spot lights
- Energy and color
- Shadow size
- Spot size and blend
- Sun angle

### Constraints

- Track To
- Damped Track
- Copy Transforms
- Constraint removal

### Rendering

- Render engine
- Resolution
- Resolution percentage
- FPS
- Output path
- Image format
- Transparent film

---

## Animation reliability

Animation is one of the most Blender-version-sensitive parts of GPT Blend.

GPT Blend 0.7.0 was tested against **Blender 5.2.2 LTS** using a real headless Blender runtime test.

The test verifies:

- transform Action creation;
- transform F-Curve creation;
- transform keyframes at multiple frames;
- actual transform evaluation at a later frame;
- animation inspection;
- viewport visibility animation;
- render visibility animation;
- animation clearing.

The implementation uses Blender's newer layered Action/F-Curve architecture and avoids relying exclusively on older object keyframe convenience APIs.

---

## Agent architecture

GPT Blend is built around an agent/tool loop:

1. Collect relevant scene context.
2. Optionally capture a viewport snapshot.
3. Send the request to the OpenAI Responses API.
4. Let the model select structured Blender tools.
5. Execute Blender tools on Blender's main thread.
6. Return structured tool results to the model.
7. Verify important operations.
8. Continue until completion, a safety limit, or an error.

This architecture allows multi-step requests instead of requiring the user to manually execute each Blender operation.

---

## Verification

Important operations can be automatically verified after execution.

For example, animation changes are followed by animation inspection. Object mutations can be followed by object inspection. Scene-wide changes such as render settings and timeline changes can be checked through scene inspection.

Verification consumes tool-call budget and is therefore included in the total tool-call safety cap.

---

## Safety and limits

Default agent limits are intentionally bounded:

- 100 continuation rounds
- 150 total Blender tool calls
- repeated-call loop protection

Destructive operations are separately controlled by a preference.

GPT Blend also places Blender undo checkpoints before mutating tool calls.

These protections are intended to reduce runaway tool loops and accidental destructive workflows; they are not a substitute for reviewing important Blender changes.

---

## Visual context

When enabled, GPT Blend can capture the active 3D View and provide the image as additional context.

This is useful when the request depends on:

- composition;
- object placement;
- visible geometry;
- viewport state;
- visual troubleshooting.

Viewport capture is best-effort and depends on the prompt being sent from a usable 3D View context.

---

## UI features

The GPT Blend sidebar provides:

- connection status;
- model selector;
- session state;
- tool-call count;
- elapsed time;
- API token usage when available;
- chat history;
- live tool activity;
- response display;
- Send;
- Stop;
- Retry;
- Copy Response;
- New Chat;
- Clear.

Changing the selected model starts a new model-specific session.

---

## Troubleshooting

### Animation fails

Restart Blender after installing a new GPT Blend build so the updated Python modules are actually loaded.

If an animation request fails, ask GPT Blend to inspect the animation and report the exact error. Recent versions include more detailed exception information.

### `bpy_prop_collection.__contains__` appears

This was a Blender 5.2 compatibility issue in earlier development builds. GPT Blend now resolves scene objects through collection name lookup instead of invalid object-instance membership checks.

### API/model errors

Check the API key, selected model, network connection, and whether the selected API model is available to your OpenAI account.

### Repeated tool calls

Enable Loop Protection and consider reducing the maximum tool-call limits.

### Material changes look different

Some material tools intentionally switch viewport shading so the change becomes immediately visible. Shared Blender materials can affect multiple objects.

---

## Developer structure

| Path | Responsibility |
| --- | --- |
| `gptblend/core/client.py` | Responses API client and agent/tool loop |
| `gptblend/core/async_agent.py` | Worker-thread orchestration |
| `gptblend/tools/schemas.py` | Model-facing tool definitions |
| `gptblend/tools/blender_ops.py` | Blender tool implementations |
| `gptblend/tools/registry.py` | Tool registry |
| `gptblend/context/scene.py` | Scene context |
| `gptblend/context/viewport.py` | Viewport image capture |
| `gptblend/ui/operators.py` | Blender operators and async polling |
| `gptblend/ui/panel.py` | Sidebar UI |
| `gptblend/preferences.py` | API/model/safety preferences |
| `tests/test_animation_runtime.py` | Real Blender animation test |
| `tests/validate_tool_surface.py` | Structural consistency test |
| `.github/workflows/validate.yml` | CI validation and extension packaging |

---

## Automated CI

Every push/pull request runs structural Python validation and a Blender 5.2.2 runtime test.

The CI package job also validates the Blender extension manifest, builds the installable ZIP package, and uploads it as a GitHub Actions artifact named `gptblend-0.7.0`.

At the time of this release, the latest packaging workflow completed successfully.

---

## Privacy and credentials

GPT Blend sends prompts and selected scene/viewport context to the OpenAI API when you use it.

Do not send confidential information through the extension unless that use is allowed by your privacy and organizational requirements.

Never publish your API key.

---

## Known limitations

- Blender must be running for Blender tool execution.
- Blender operations execute on Blender's main thread.
- A heavy Blender operation can temporarily make the UI unresponsive.
- Network cancellation cannot instantly terminate an already-blocking HTTP request.
- GPT Blend currently handles one agent job at a time.
- Viewport screenshots depend on a usable 3D View context.
- Shared Blender materials can affect multiple users of the material.
- Blender API changes can require future compatibility updates.
- OpenAI model IDs and availability can change independently of GPT Blend releases.

---

## License

GPT Blend is distributed under the MIT License. See [LICENSE](LICENSE).

---

## Contributing

When reporting a bug, include:

- Blender version;
- GPT Blend version;
- selected model/API ID;
- exact prompt;
- relevant tool or error message;
- whether the issue reproduces in a new Blender file.

Never include your OpenAI API key in an issue, pull request, screenshot, or log.

---

## Current release

**GPT Blend 0.7.0**

Target Blender version: **5.2.0+**

Primary repository: https://github.com/jumbleoptionslotm1934-art/GPTBlend## Example prompts

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
