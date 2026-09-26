import base64
import os
import tempfile
import uuid

import bpy


def capture_viewport_data_url():
    """Capture the active 3D viewport as a PNG data URL.

    Returns None when Blender cannot capture the current viewport. This is
    intentionally best-effort so visual context never blocks normal chat.
    """
    area = bpy.context.area
    if area is None or area.type != "VIEW_3D":
        return None

    filepath = os.path.join(
        tempfile.gettempdir(),
        f"gptblend_viewport_{uuid.uuid4().hex}.png",
    )

    scene = bpy.context.scene
    original_filepath = scene.render.filepath
    original_format = scene.render.image_settings.file_format

    try:
        scene.render.filepath = filepath
        scene.render.image_settings.file_format = "PNG"
        result = bpy.ops.render.opengl(
            write_still=True,
            view_context=True,
        )
        if "FINISHED" not in result or not os.path.exists(filepath):
            return None

        with open(filepath, "rb") as handle:
            data = base64.b64encode(handle.read()).decode("ascii")
        return f"data:image/png;base64,{data}"
    except Exception:
        return None
    finally:
        scene.render.filepath = original_filepath
        scene.render.image_settings.file_format = original_format
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except OSError:
            pass
