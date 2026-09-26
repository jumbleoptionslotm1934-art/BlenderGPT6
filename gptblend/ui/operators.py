import bpy
from bpy.types import Operator
from ..preferences import get_preferences
from ..core.client import send_message, GPTBlendError
from ..context.scene import get_scene_context

class GPTBlendSendOperator(Operator):
    bl_idname = "gptblend.send"
    bl_label = "Send to GPT"

    def execute(self, context):
        props = context.scene.gptblend_props
        prefs = get_preferences()
        if not props.prompt.strip():
            props.response = "Enter a prompt first."
            return {"FINISHED"}
        props.response = "Thinking..."
        try:
            props.response = send_message(prefs.api_key, prefs.model, props.prompt.strip(), get_scene_context())
        except GPTBlendError as exc:
            props.response = str(exc)
        except Exception as exc:
            props.response = f"Unexpected error: {exc}"
        props.model = prefs.model
        props.prompt = ""
        return {"FINISHED"}

class GPTBlendClearOperator(Operator):
    bl_idname = "gptblend.clear"
    bl_label = "Clear"

    def execute(self, context):
        context.scene.gptblend_props.response = ""
        context.scene.gptblend_props.prompt = ""
        return {"FINISHED"}

classes = (GPTBlendSendOperator, GPTBlendClearOperator)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
