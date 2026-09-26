import bpy
import time
from bpy.types import Operator

from ..preferences import get_preferences
from ..context.scene import get_scene_context
from ..context.viewport import capture_viewport_data_url
from ..core.async_agent import AsyncAgentJob
from ..tools.registry import run_tool


_ACTIVE_JOB = None
_TIMER_REGISTERED = False


def _unregister_timer():
    global _TIMER_REGISTERED
    if not _TIMER_REGISTERED:
        return
    try:
        bpy.app.timers.unregister(_poll_active_job)
    except Exception:
        pass
    _TIMER_REGISTERED = False


def _append_chat(props, role, message):
    lines = props.chat_log.splitlines() if props.chat_log else []
    lines.append(
        f"[{time.strftime('%H:%M:%S')}] {role.upper()}: {str(message)}"
    )
    props.chat_log = "\n".join(lines[-40:])


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

        props.tool_calls = snapshot["tool_calls"]
        usage = snapshot.get("usage") or {}
        props.input_tokens = int(usage.get("input_tokens", 0) or 0)
        props.output_tokens = int(usage.get("output_tokens", 0) or 0)
        props.total_tokens = int(usage.get("total_tokens", 0) or 0)
        props.elapsed_seconds = f'{snapshot["elapsed_seconds"]:.1f}'
        props.activity_log = "\n".join(snapshot["events"][-20:])

        if snapshot["done"]:
            if snapshot["error"]:
                props.response = snapshot["error"]
                if snapshot["status"] != "Cancelled":
                    _append_chat(props, "assistant", snapshot["error"])
            elif snapshot["response_text"]:
                props.response = snapshot["response_text"]
                _append_chat(props, "assistant", snapshot["response_text"])

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

        viewport_image = (
            capture_viewport_data_url()
            if prefs.include_viewport_snapshot
            else None
        )

        _append_chat(props, "user", prompt)
        props.last_prompt = prompt

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
            viewport_image_data_url=viewport_image,
        )

        _ACTIVE_JOB = job
        props.response = "Starting GPT Blend..."
        props.status = "Starting"
        props.model = prefs.model
        props.prompt = ""

        job.start()
        _ensure_timer()
        return {"FINISHED"}


class GPTBlendRetryOperator(Operator):
    bl_idname = "gptblend.retry"
    bl_label = "Retry Last Prompt"

    def execute(self, context):
        props = context.scene.gptblend_props
        if _ACTIVE_JOB is not None:
            props.response = "GPT Blend is already working."
            return {"FINISHED"}
        if not props.last_prompt.strip():
            props.response = "No previous prompt is available to retry."
            props.status = "Waiting for prompt"
            return {"FINISHED"}

        props.prompt = props.last_prompt
        return bpy.ops.gptblend.send()


class GPTBlendCopyResponseOperator(Operator):
    bl_idname = "gptblend.copy_response"
    bl_label = "Copy Response"

    def execute(self, context):
        response = context.scene.gptblend_props.response
        if not response:
            return {"CANCELLED"}
        context.window_manager.clipboard = response
        context.scene.gptblend_props.status = "Response copied"
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
            _ACTIVE_JOB = None
        _unregister_timer()

        props = context.scene.gptblend_props
        props.response = ""
        props.prompt = ""
        props.response_id = ""
        props.session_model = ""
        props.chat_log = ""
        props.last_prompt = ""
        props.activity_log = ""
        props.tool_calls = 0
        props.elapsed_seconds = "0.0"
        props.status = "New session"
        return {"FINISHED"}


class GPTBlendClearOperator(Operator):
    bl_idname = "gptblend.clear"
    bl_label = "Clear"

    def execute(self, context):
        global _ACTIVE_JOB

        if _ACTIVE_JOB is not None:
            _ACTIVE_JOB.cancel()
            _ACTIVE_JOB = None
        _unregister_timer()

        context.scene.gptblend_props.response = ""
        context.scene.gptblend_props.prompt = ""
        context.scene.gptblend_props.last_prompt = ""
        context.scene.gptblend_props.status = "Ready"
        context.scene.gptblend_props.activity_log = ""
        context.scene.gptblend_props.tool_calls = 0
        context.scene.gptblend_props.elapsed_seconds = "0.0"
        return {"FINISHED"}


classes = (
    GPTBlendConfigureOperator,
    GPTBlendSendOperator,
    GPTBlendRetryOperator,
    GPTBlendCopyResponseOperator,
    GPTBlendStopOperator,
    GPTBlendNewChatOperator,
    GPTBlendClearOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global _ACTIVE_JOB, _TIMER_REGISTERED

    if _ACTIVE_JOB is not None:
        _ACTIVE_JOB.cancel()
        _ACTIVE_JOB = None

    if _TIMER_REGISTERED:
        try:
            bpy.app.timers.unregister(_poll_active_job)
        except Exception:
            pass
        _TIMER_REGISTERED = False

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
