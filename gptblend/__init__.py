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
