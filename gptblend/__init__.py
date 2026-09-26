bl_info = {
    "name": "GPT Blend",
    "author": "GPT Blend",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > GPT Blend",
    "description": "Connect Blender to OpenAI GPT models.",
    "category": "3D View",
}

from . import preferences
from .ui import panel, operators

def register():
    preferences.register()
    panel.register()
    operators.register()

def unregister():
    operators.unregister()
    panel.unregister()
    preferences.unregister()
