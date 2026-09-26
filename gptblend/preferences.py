import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, EnumProperty, IntProperty, BoolProperty


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

    max_tool_rounds: IntProperty(
        name="Max Agent Rounds",
        description="Maximum number of model/tool continuation rounds for one prompt.",
        default=100,
        min=1,
        max=200,
    )

    max_total_tool_calls: IntProperty(
        name="Max Total Tool Calls",
        description="Hard safety cap on the total Blender tool calls in one prompt.",
        default=150,
        min=1,
        max=500,
    )

    loop_protection: BoolProperty(
        name="Loop Protection",
        description="Stop the agent when it repeats the exact same tool call too many times.",
        default=True,
    )

    allow_destructive_operations: BoolProperty(
        name="Allow Destructive Operations",
        description="Allow GPT Blend to delete objects, apply modifiers, and join objects without an additional confirmation step.",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="GPT Blend — OpenAI")
        layout.prop(self, "api_key")
        layout.prop(self, "model")

        box = layout.box()
        box.label(text="Agent Controls", icon="SETTINGS")
        box.prop(self, "max_tool_rounds")
        box.prop(self, "max_total_tool_calls")
        box.prop(self, "loop_protection")
        box.prop(self, "allow_destructive_operations")


classes = (GPTBlendPreferences,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


def get_preferences():
    return bpy.context.preferences.addons[__package__].preferences
