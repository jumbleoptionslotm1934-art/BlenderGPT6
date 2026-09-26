import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, EnumProperty

class GPTBlendPreferences(AddonPreferences):
    bl_idname = __package__

    api_key: StringProperty(
        name="OpenAI API Key",
        description="API key used by GPT Blend. Stored in Blender preferences.",
        subtype="PASSWORD",
        default="",
    )

    model: EnumProperty(
        name="Model",
        items=[
            ("gpt-6-luna", "GPT-6 Luna", "Fast everyday model"),
            ("gpt-6-sol", "GPT-6 Sol", "High-capability model"),
            ("gpt-6-astra", "GPT-6 Astra", "Flagship reasoning model"),
        ],
        default="gpt-6-luna",
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="GPT Blend — OpenAI")
        layout.prop(self, "api_key")
        layout.prop(self, "model")

classes = (GPTBlendPreferences,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

def get_preferences():
    return bpy.context.preferences.addons[__package__].preferences
