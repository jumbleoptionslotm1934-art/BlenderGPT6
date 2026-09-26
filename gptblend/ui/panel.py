import bpy
from bpy.types import Panel, PropertyGroup
from bpy.props import StringProperty, PointerProperty
from ..preferences import get_preferences

class GPTBlendSceneProperties(PropertyGroup):
    prompt: StringProperty(name="Prompt", default="")
    response: StringProperty(name="Response", default="")
    model: StringProperty(name="Model", default="gpt-6-luna")

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
        box = layout.box()
        if props.response:
            for line in props.response.splitlines():
                box.label(text=line[:200])
        else:
            box.label(text="Ask GPT Blend something.")
        layout.prop(props, "prompt", text="")
        layout.operator("gptblend.send", icon="CONSOLE")
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
