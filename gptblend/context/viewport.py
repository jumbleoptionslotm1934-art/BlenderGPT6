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

    try:
        result = bpy.ops.render.opengl(
            write_still=True,
            view_context=True,
            filepath=filepath,
        )
        if "FINISHED" not in result or not os.path.exists(filepath):
            return None

        with open(filepath, "rb") as handle:
            data = base64.b64encode(handle.read()).decode("ascii")
        return f"data:image/png;base64,{data}"
    except Exception:
        return None
    finally:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except OSError:
            pass
