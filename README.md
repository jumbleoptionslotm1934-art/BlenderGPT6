# GPT Blend

AI-powered Blender add-on for connecting Blender to OpenAI GPT models.

## Current capabilities

GPT Blend now uses OpenAI function calling to let the selected GPT model operate Blender through a controlled tool layer instead of returning only Python code.

### Scene and object control
- Inspect the scene
- Inspect an individual object
- Create primitives
- Transform objects
- Rename objects
- Duplicate objects
- Delete objects when explicitly requested
- Select objects
- Hide or unhide objects
- Change render visibility

### Modeling and shading
- Set viewport object colors
- Create and assign materials
- Add Bevel modifiers
- Add Subdivision Surface modifiers
- Remove modifiers
- Apply modifiers
- Smooth or flat shade meshes
- Join objects
- Set object origins
- Parent objects

### Scene organization
- Create collections
- Move objects between collections
- Inspect collection membership

### Scene setup
- Create Point, Area, Sun, and Spot lights
- Create cameras and make one the active camera
- Change the world background
- Create 3D text

The current tool layer contains the original six Blender operations plus 20 additional capabilities.

## Installation

1. Download or clone this repository.
2. Install the extension from Blender Preferences > Get Extensions > Install from Disk, using the repository package.
3. Enable GPT Blend.
4. Open the 3D View sidebar (N) and select GPT Blend.
5. Configure your OpenAI API key in Preferences.

Never commit your API key.

## Example prompts

- "Create three cubes in a row, 2 meters apart."
- "Make the middle cube blue and slightly metallic."
- "Add a small bevel and smooth shading to the selected object."
- "Create a collection called Environment and move the selected objects into it."
- "Add an area light above the scene and make it the main light."
- "Create a camera at this location and make it the active camera."
- "Put the text 'GPT Blend' above the scene."

## Safety and scope

GPT Blend keeps tool inputs structured and limited to explicit Blender operations. The model is instructed to avoid unnecessary edits and never delete objects unless the user explicitly asks for deletion.

The current network request is synchronous, so Blender may remain busy while a request is being processed. Async execution and richer visual workspace understanding are planned next.

## Development

Keep Blender-specific operations in `gptblend/tools/blender_ops.py` and their model-facing JSON schemas in `gptblend/tools/schemas.py`. The registry connects the two layers.

Never commit an API key.
