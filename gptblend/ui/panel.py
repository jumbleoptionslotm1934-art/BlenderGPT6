import bpy
from bpy.types import Panel, PropertyGroup
from bpy.props import StringProperty, PointerProperty, IntProperty
from ..preferences import get_preferences


class GPTBlendSceneProperties(PropertyGroup):
    prompt: StringProperty(name="Prompt", default="")
    response: StringProperty(name="Response", default="")
    model: StringProperty(name="Model", default="gpt-6-luna")
    response_id: StringProperty(name="Response ID", default="")
    session_model: StringProperty(name="Session Model", default="")
    status: StringProperty(name="Status", default="Ready")
    chat_log: StringProperty(name="Chat Log", default="")
    activity_log: StringProperty(name="Activity Log", default="")
    tool_calls: IntProperty(name="Tool Calls", default=0)


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
        if props.tool_calls:
            status.label(text=f"Tools: {props.tool_calls}")

        history_box = layout.box()
        history_box.label(text="Chat", icon="TEXT")
        if props.chat_log:
            for line in props.chat_log.splitlines()[-14:]:
                history_box.label(text=line[:180])
        else:
            history_box.label(text="No messages yet.")

        activity_box = layout.box()
        activity_box.label(text="Activity", icon="TIME")
        if props.activity_log:
            for line in props.activity_log.splitlines()[-10:]:
                activity_box.label(text=line[:180])
        else:
            activity_box.label(text="Waiting for activity.")

        box = layout.box()
        if props.response:
            for line in props.response.splitlines():
                box.label(text=line[:200])
        else:
            box.label(text="Ask GPT Blend something.")

        layout.prop(props, "prompt", text="")

        row = layout.row(align=True)
        if props.status not in {"Ready", "Error", "Cancelled", "New session", "Waiting for prompt"}:
            row.operator("gptblend.stop", icon="CANCEL", text="Stop")
        else:
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
