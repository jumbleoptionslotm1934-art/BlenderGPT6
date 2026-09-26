import json
import urllib.request
import urllib.error

API_URL = "https://api.openai.com/v1/responses"

class GPTBlendError(Exception):
    pass

def send_message(api_key, model, user_message, context_text=""):
    if not api_key:
        raise GPTBlendError("No OpenAI API key configured.")

    instructions = (
        "You are GPT Blend, an AI assistant inside Blender. "
        "Answer clearly and concisely. You are currently in prototype mode: "
        "you can inspect the provided Blender context but cannot execute Blender changes yet.\n\n"
        f"BLENDER CONTEXT:\n{context_text or 'No context available.'}"
    )
    payload = {"model": model, "instructions": instructions, "input": user_message}
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise GPTBlendError(f"OpenAI API error ({exc.code}): {body}") from exc
    except urllib.error.URLError as exc:
        raise GPTBlendError(f"Network error: {exc.reason}") from exc
    except Exception as exc:
        raise GPTBlendError(f"Request failed: {exc}") from exc

    output = data.get("output_text")
    if output:
        return output

    chunks = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                chunks.append(content["text"])
    if chunks:
        return "\n".join(chunks)
    raise GPTBlendError("The API returned no text output.")
