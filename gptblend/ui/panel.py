import bpy
from bpy.types import Panel, PropertyGroup
from bpy.props import StringProperty, PointerProperty
from ..preferences import get_preferences


class GPTBlendSceneProperties(PropertyGroup):
    prompt: StringProperty(name="Prompt", default="")
    response: StringProperty(name="Response", default="")
    model: StringProperty(name="Model", default="gpt-6-luna")
    response_id: StringProperty(name="Response ID", default="")
    session_model: StringProperty(name="Session Model", default="")
    status: StringProperty(name="Status", default="Ready")


class GPTBlendPanel(Panel):
    bl_label = "GPT Blend"
    bl_idname = "VIEW3D_PT_gptblend"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GPT Blend"

    def draw(self, context):
        layout = self.layout
        props = context.scene.gptblend_props
        prefs = get_preferences()

        layout.label(text="GPT Blend", icon="WORLD")

        if prefs.api_key:
            row = layout.row()
            row.label(text="Connected", icon="CHECKMARK")
        else:
            box = layout.box()
            box.alert = True
            box.label(text="OpenAI API key not configured", icon="ERROR")
            box.operator("gptblend.configure", icon="PREFERENCES")

        layout.prop(prefs, "model", text="Model")

        status = layout.row()
        status.label(text=f"Status: {props.status}")
        if props.response_id:
            status.label(text="Session active", icon="LINKED")

        box = layout.box()
        if props.response:
            for line in props.response.splitlines():
                box.label(text=line[:200])
        else:
            box.label(text="Ask GPT Blend something.")

        layout.prop(props, "prompt", text="")

        row = layout.row(align=True)
        row.operator("gptblend.send", icon="CONSOLE", text="Send to GPT")
        row.operator("gptblend.new_chat", icon="FILE_NEW", text="New Chat")

        layout.operator("gptblend.clear", icon="X")


classes = (GPTBlendSceneProperties, GPTBlendPanel)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.gptblend_props = PointerProperty(type=GPTBlendSceneProperties)


def unregister():
    del bpy.types.Scene.gptblend_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
