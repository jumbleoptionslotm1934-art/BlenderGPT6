import bpy
from bpy.types import Operator

from ..preferences import get_preferences
from ..context.scene import get_scene_context
from ..core.async_agent import AsyncAgentJob
from ..tools.registry import run_tool


_ACTIVE_JOB = None
_TIMER_REGISTERED = False


def _scene_props():
    if _ACTIVE_JOB is None:
        return None
    scene = bpy.data.scenes.get(_ACTIVE_JOB.scene_name)
    return scene.gptblend_props if scene and hasattr(scene, "gptblend_props") else None


def _poll_active_job():
    global _ACTIVE_JOB, _TIMER_REGISTERED

    job = _ACTIVE_JOB
    if job is None:
        _TIMER_REGISTERED = False
        return None

    # Blender API calls stay on Blender's main thread.
    processed = 0
    while processed < 2:
        try:
            request = job.tool_queue.get_nowait()
        except Exception:
            break

        if job.cancel_event.is_set():
            request.result = {
                "ok": False,
                "cancelled": True,
                "message": "Task cancelled before tool execution.",
            }
        else:
            try:
                request.result = run_tool(request.name, request.arguments)
            except Exception as exc:
                request.result = {
                    "ok": False,
                    "message": f"Blender tool execution error: {exc}",
                }

        request.event.set()
        processed += 1

    props = _scene_props()
    snapshot = job.snapshot()

    if props is not None:
        props.status = snapshot["status"]

        if snapshot["done"]:
            if snapshot["error"]:
                props.response = snapshot["error"]
            elif snapshot["response_text"]:
                props.response = snapshot["response_text"]

            if snapshot["response_id"]:
                props.response_id = snapshot["response_id"]
                props.session_model = job.model

    if snapshot["done"]:
        _ACTIVE_JOB = None
        _TIMER_REGISTERED = False
        return None

    return 0.08


def _ensure_timer():
    global _TIMER_REGISTERED
    if not _TIMER_REGISTERED:
        bpy.app.timers.register(_poll_active_job, first_interval=0.08)
        _TIMER_REGISTERED = True


class GPTBlendConfigureOperator(Operator):
    bl_idname = "gptblend.configure"
    bl_label = "Configure API Key"

    def execute(self, context):
        bpy.ops.screen.userpref_show("INVOKE_DEFAULT")
        return {"FINISHED"}


class GPTBlendSendOperator(Operator):
    bl_idname = "gptblend.send"
    bl_label = "Send to GPT"

    def execute(self, context):
        global _ACTIVE_JOB

        props = context.scene.gptblend_props
        prefs = get_preferences()

        if _ACTIVE_JOB is not None:
            props.response = "GPT Blend is already working. Use Stop to cancel the current task."
            return {"FINISHED"}

        prompt = props.prompt.strip()
        if not prompt:
            props.response = "Enter a prompt first."
            props.status = "Waiting for prompt"
            return {"FINISHED"}

        previous_response_id = (
            props.response_id
            if props.response_id and props.session_model == prefs.model
            else None
        )

        job = AsyncAgentJob(
            api_key=prefs.api_key,
            model=prefs.model,
            user_message=prompt,
            context_text=get_scene_context(),
            scene_name=context.scene.name,
            previous_response_id=previous_response_id,
            max_tool_rounds=prefs.max_tool_rounds,
            max_total_tool_calls=prefs.max_total_tool_calls,
            loop_protection=prefs.loop_protection,
            allow_destructive_operations=prefs.allow_destructive_operations,
        )

        _ACTIVE_JOB = job
        props.response = "Starting GPT Blend..."
        props.status = "Starting"
        props.model = prefs.model
        props.prompt = ""

        job.start()
        _ensure_timer()
        return {"FINISHED"}


class GPTBlendStopOperator(Operator):
    bl_idname = "gptblend.stop"
    bl_label = "Stop GPT"

    def execute(self, context):
        props = context.scene.gptblend_props

        if _ACTIVE_JOB is None:
            props.status = "Ready"
            return {"FINISHED"}

        _ACTIVE_JOB.cancel()
        props.status = "Stopping..."
        return {"FINISHED"}


class GPTBlendNewChatOperator(Operator):
    bl_idname = "gptblend.new_chat"
    bl_label = "New Chat"

    def execute(self, context):
        global _ACTIVE_JOB

        if _ACTIVE_JOB is not None:
            _ACTIVE_JOB.cancel()

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
        context.scene.gptblend_props.response = ""
        context.scene.gptblend_props.prompt = ""
        context.scene.gptblend_props.status = "Ready"
        return {"FINISHED"}


classes = (
    GPTBlendConfigureOperator,
    GPTBlendSendOperator,
    GPTBlendStopOperator,
    GPTBlendNewChatOperator,
    GPTBlendClearOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global _ACTIVE_JOB

    if _ACTIVE_JOB is not None:
        _ACTIVE_JOB.cancel()
        _ACTIVE_JOB = None

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
