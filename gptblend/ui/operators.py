import bpy
from bpy.types import Operator
from ..preferences import get_preferences
from ..core.client import send_message, GPTBlendError
from ..context.scene import get_scene_context


class GPTBlendConfigureOperator(Operator):
    bl_idname = "gptblend.configure"
    bl_label = "Configure API Key"

    def execute(self, context):
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {"FINISHED"}


class GPTBlendSendOperator(Operator):
    bl_idname = "gptblend.send"
    bl_label = "Send to GPT"

    def execute(self, context):
        props = context.scene.gptblend_props
        prefs = get_preferences()

        if not props.prompt.strip():
            props.response = "Enter a prompt first."
            props.status = "Waiting for prompt"
            return {"FINISHED"}

        props.response = "Thinking..."
        props.status = "Working"

        # A session is model-specific. Switching models starts a fresh session.
        previous_response_id = (
            props.response_id
            if props.response_id and props.session_model == prefs.model
            else None
        )

        try:
            response_text, _output, response_id = send_message(
                prefs.api_key,
                prefs.model,
                props.prompt.strip(),
                get_scene_context(),
                previous_response_id=previous_response_id,
                max_tool_rounds=prefs.max_tool_rounds,
                max_total_tool_calls=prefs.max_total_tool_calls,
                loop_protection=prefs.loop_protection,
                allow_destructive_operations=prefs.allow_destructive_operations,
            )
            props.response = response_text or "GPT returned no text response."
            props.response_id = response_id or ""
            props.session_model = prefs.model
            props.status = "Ready"
        except GPTBlendError as exc:
            props.response = str(exc)
            props.status = "Error"
        except Exception as exc:
            props.response = f"Unexpected error: {exc}"
            props.status = "Error"

        props.model = prefs.model
        props.prompt = ""
        return {"FINISHED"}


class GPTBlendNewChatOperator(Operator):
    bl_idname = "gptblend.new_chat"
    bl_label = "New Chat"

    def execute(self, context):
        props = context.scene.gptblend_props
        props.response = ""
        props.prompt = ""
        props.response_id = ""
        props.session_model = ""
        props.status = "New session"
        return {"FINISHED"}


class GPTBlendClearOperator(Operator):
    bl_idname = "gptblend.clear"
    bl_label = "Clear"

    def execute(self, context):
        props = context.scene.gptblend_props
        props.response = ""
        props.prompt = ""
        props.status = "Ready"
        return {"FINISHED"}


classes = (
    GPTBlendConfigureOperator,
    GPTBlendSendOperator,
    GPTBlendNewChatOperator,
    GPTBlendClearOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
