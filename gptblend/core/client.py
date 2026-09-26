import json
import urllib.request
import urllib.error

from ..tools.registry import get_tools, run_tool

API_URL = "https://api.openai.com/v1/responses"
MAX_TOOL_ROUNDS = 100
MAX_TOTAL_TOOL_CALLS = 150
MAX_IDENTICAL_TOOL_CALLS = 4


class GPTBlendError(Exception):
    pass


def _request(api_key, payload):
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise GPTBlendError(f"OpenAI API error ({exc.code}): {body}") from exc
    except urllib.error.URLError as exc:
        raise GPTBlendError(f"Network error: {exc.reason}") from exc
    except Exception as exc:
        raise GPTBlendError(f"Request failed: {exc}") from exc


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


def send_message(api_key, model, user_message, context_text="", history=None):
    if not api_key:
        raise GPTBlendError("No OpenAI API key configured.")

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
        "Keep changes scoped to the user's request and avoid unnecessary edits.\n\n"
        f"CURRENT BLENDER CONTEXT:\n{context_text or 'No context available.'}"
    )

    input_items = []
    if history:
        input_items.extend(history)
    input_items.append({"role": "user", "content": user_message})

    payload = {
        "model": model,
        "instructions": instructions,
        "input": input_items,
        "tools": get_tools(),
        "parallel_tool_calls": False,
    }

    tool_call_count = 0
    last_signature = None
    identical_call_count = 0

    for _ in range(MAX_TOOL_ROUNDS):
        if tool_call_count >= MAX_TOTAL_TOOL_CALLS:
            raise GPTBlendError(
                f"GPT Blend stopped after {MAX_TOTAL_TOOL_CALLS} total tool calls to prevent runaway execution."
            )

        data = _request(api_key, payload)
        tool_calls = [item for item in data.get("output", []) if item.get("type") == "function_call"]

        if not tool_calls:
            return _extract_text(data), data.get("output", [])

        tool_outputs = []
        for call in tool_calls:
            tool_call_count += 1

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

                if identical_call_count > MAX_IDENTICAL_TOOL_CALLS:
                    raise GPTBlendError(
                        f"GPT Blend stopped because the same tool call repeated {MAX_IDENTICAL_TOOL_CALLS} times."
                    )

                try:
                    result = run_tool(call.get("name"), arguments)
                except Exception as exc:
                    result = {"ok": False, "message": f"Tool execution error: {exc}"}

            tool_outputs.append({
                "type": "function_call_output",
                "call_id": call.get("call_id"),
                "output": json.dumps(result),
            })

        payload = {
            "model": model,
            "previous_response_id": data.get("id"),
            "input": tool_outputs,
            "tools": get_tools(),
            "parallel_tool_calls": False,
        }

    raise GPTBlendError("GPT Blend reached the maximum number of tool rounds.")
