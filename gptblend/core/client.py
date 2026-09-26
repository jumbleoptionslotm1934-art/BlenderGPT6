import json
import time
import urllib.request
import urllib.error

from ..tools.registry import get_tools, run_tool

API_URL = "https://api.openai.com/v1/responses"
MAX_TOOL_ROUNDS = 100
MAX_TOTAL_TOOL_CALLS = 150
MAX_IDENTICAL_TOOL_CALLS = 4
MAX_REQUEST_RETRIES = 3
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

VERIFY_OBJECT_ARGUMENT = {
    "create_object": "name",
    "transform_object": "name",
    "rename_object": "new_name",
    "duplicate_object": "new_name",
    "set_material": "object_name",
    "set_object_color": "name",
    "move_object_delta": "name",
    "rotate_object_delta": "name",
    "set_object_dimensions": "name",
    "apply_object_scale": "name",
    "set_procedural_texture": "object_name",
    "animate_object_transform": "object_name",
}


class GPTBlendError(Exception):
    pass


def _request(api_key, payload):
    last_error = None

    for attempt in range(MAX_REQUEST_RETRIES + 1):
        request = urllib.request.Request(
            API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_error = GPTBlendError(f"OpenAI API error ({exc.code}): {body}")
            if exc.code not in RETRYABLE_STATUS_CODES or attempt >= MAX_REQUEST_RETRIES:
                raise last_error from exc
            time.sleep(min(2 ** attempt, 8))
        except urllib.error.URLError as exc:
            last_error = GPTBlendError(f"Network error: {exc.reason}")
            if attempt >= MAX_REQUEST_RETRIES:
                raise last_error from exc
            time.sleep(min(2 ** attempt, 8))
        except Exception as exc:
            raise GPTBlendError(f"Request failed: {exc}") from exc

    raise last_error or GPTBlendError("Request failed after retries.")


def _extract_text(data):
    output = data.get("output_text")
    if output:
        return output

    chunks = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                chunks.append(content["text"])
    return "\n".join(chunks)


def send_message(
    api_key,
    model,
    user_message,
    context_text="",
    history=None,
    previous_response_id=None,
    max_tool_rounds=MAX_TOOL_ROUNDS,
    max_total_tool_calls=MAX_TOTAL_TOOL_CALLS,
    loop_protection=True,
    allow_destructive_operations=False,
    tool_executor=None,
    progress_callback=None,
    cancel_event=None,
    viewport_image_data_url=None,
):
    if not api_key:
        raise GPTBlendError("No OpenAI API key configured.")

    max_tool_rounds = max(1, min(int(max_tool_rounds), 200))
    max_total_tool_calls = max(1, min(int(max_total_tool_calls), 500))

    instructions = (
        "You are GPT Blend, an interactive AI assistant inside Blender. "
        "You can inspect and modify the Blender workspace using the provided Blender tools. "
        "Prefer tools over writing bpy Python code. "
        "Do not claim an action happened unless a tool returned success. "
        "When a task requires multiple steps, perform those steps with tools and verify important results. "
        "Use inspect_scene or inspect_object when object names, transforms, modifiers, materials, "
        "or collections are uncertain. "
        "Do not delete objects unless the user explicitly requests deletion. "
        "Do not apply modifiers, join objects, or change scene structure unless it helps fulfill the user's request. "
        "Keep changes scoped to the user's request and avoid unnecessary edits. "
        "When the user asks for visible color, materials, or textures, actually create/apply the material with the material tools. "
        "When a procedural texture is requested, use set_procedural_texture rather than only changing viewport color. "
        "When the user expects to see the material or texture in the 3D viewport, use set_viewport_shading with MATERIAL as needed. "
        "When the user asks for an animation, use the animation tools to set scene timing and create explicit transform keyframes instead of only moving the object once. "
        "For camera, light, or object animation, use animate_object_transform and verify the authored action afterward. "
        "After important material, texture, camera, lighting, or geometry changes, verify the result with an inspection tool before claiming success. "
        "Use the provided viewport image as visual evidence when present; distinguish what is visible there from what must be verified through Blender tools.\n\n"
        f"CURRENT BLENDER CONTEXT:\n{context_text or 'No context available.'}"
    )

    input_items = []
    if history:
        input_items.extend(history)

    user_content = [{"type": "input_text", "text": user_message}]
    if viewport_image_data_url:
        user_content.append({
            "type": "input_image",
            "image_url": viewport_image_data_url,
            "detail": "auto",
        })
    input_items.append({"role": "user", "content": user_content})

    payload = {
        "model": model,
        "instructions": instructions,
        "input": input_items,
        "tools": get_tools(),
        "parallel_tool_calls": False,
    }

    if previous_response_id:
        payload["previous_response_id"] = previous_response_id

    tool_call_count = 0
    last_signature = None
    identical_call_count = 0

    def progress(message):
        if progress_callback:
            try:
                progress_callback(message)
            except Exception:
                pass

    def cancelled():
        return bool(cancel_event and cancel_event.is_set())

    for round_index in range(max_tool_rounds):
        if cancelled():
            raise GPTBlendError("GPT Blend task cancelled.")
        progress(f"Thinking (round {round_index + 1}/{max_tool_rounds})")

        if tool_call_count >= max_total_tool_calls:
            raise GPTBlendError(
                f"GPT Blend stopped after {max_total_tool_calls} total tool calls to prevent runaway execution."
            )

        progress("Waiting for OpenAI...")
        data = _request(api_key, payload)
        tool_calls = [item for item in data.get("output", []) if item.get("type") == "function_call"]

        if not tool_calls:
            return _extract_text(data), data.get("output", []), data.get("id")

        tool_outputs = []
        for call in tool_calls:
            tool_call_count += 1
            if tool_call_count > max_total_tool_calls:
                raise GPTBlendError(
                    f"GPT Blend stopped after {max_total_tool_calls} total tool calls."
                )

            try:
                arguments = json.loads(call.get("arguments", "{}"))
            except json.JSONDecodeError as exc:
                result = {"ok": False, "message": f"Invalid tool arguments: {exc}"}
            else:
                signature = json.dumps(
                    {"name": call.get("name"), "arguments": arguments},
                    sort_keys=True,
                    separators=(",", ":"),
                )

                if signature == last_signature:
                    identical_call_count += 1
                else:
                    identical_call_count = 1
                    last_signature = signature

                if loop_protection and identical_call_count > MAX_IDENTICAL_TOOL_CALLS:
                    raise GPTBlendError(
                        f"GPT Blend stopped because the same tool call repeated "
                        f"{MAX_IDENTICAL_TOOL_CALLS} times."
                    )

                if (
                    call.get("name") in {"delete_object", "apply_modifier", "join_objects", "merge_selected_vertices", "dissolve_selected"}
                    and not allow_destructive_operations
                ):
                    result = {
                        "ok": False,
                        "confirmation_required": True,
                        "message": (
                            f"'{call.get('name')}' is a destructive operation and is disabled "
                            "until destructive operations are enabled in GPT Blend Preferences."
                        ),
                    }
                else:
                    if cancelled():
                        raise GPTBlendError("GPT Blend task cancelled.")
                    progress(f"Executing {call.get('name')}...")
                    try:
                        if tool_executor is not None:
                            result = tool_executor(call.get("name"), arguments)
                        else:
                            result = run_tool(call.get("name"), arguments)

                        verify_key = VERIFY_OBJECT_ARGUMENT.get(call.get("name"))
                        if (
                            result.get("ok")
                            and verify_key
                            and arguments.get(verify_key)
                            and tool_executor is not None
                            and tool_call_count < max_total_tool_calls
                        ):
                            tool_call_count += 1
                            progress("Verifying the Blender change...")
                            verification_tool = (
                                "inspect_animation"
                                if call.get("name") == "animate_object_transform"
                                else "inspect_object"
                            )
                            verification_args = (
                                {"object_name": arguments[verify_key]}
                                if verification_tool == "inspect_animation"
                                else {"name": arguments[verify_key]}
                            )
                            verification = tool_executor(
                                verification_tool,
                                verification_args,
                            )
                            if verification.get("ok"):
                                result["verification"] = (
                                    verification
                                    if verification_tool == "inspect_animation"
                                    else verification.get("object")
                                )
                    except Exception as exc:
                        result = {"ok": False, "message": f"Tool execution error: {exc}"}

            tool_outputs.append({
                "type": "function_call_output",
                "call_id": call.get("call_id"),
                "output": json.dumps(result),
            })

        payload = {
            "model": model,
            "instructions": instructions,
            "previous_response_id": data.get("id"),
            "input": tool_outputs,
            "tools": get_tools(),
            "parallel_tool_calls": False,
        }

    raise GPTBlendError(
        f"GPT Blend reached the configured maximum of {max_tool_rounds} agent rounds."
    )
