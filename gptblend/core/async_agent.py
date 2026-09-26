import queue
import threading
from dataclasses import dataclass, field

from .client import send_message, GPTBlendError


@dataclass
class ToolRequest:
    name: str
    arguments: dict
    event: threading.Event = field(default_factory=threading.Event)
    result: dict | None = None


class AsyncAgentJob:
    """Runs network/model work in a worker thread while Blender tools stay on the main thread."""

    def __init__(
        self,
        api_key,
        model,
        user_message,
        context_text,
        scene_name,
        previous_response_id=None,
        max_tool_rounds=100,
        max_total_tool_calls=150,
        loop_protection=True,
        allow_destructive_operations=False,
        viewport_image_data_url=None,
    ):
        self.api_key = api_key
        self.model = model
        self.user_message = user_message
        self.context_text = context_text
        self.scene_name = scene_name
        self.previous_response_id = previous_response_id
        self.max_tool_rounds = max_tool_rounds
        self.max_total_tool_calls = max_total_tool_calls
        self.loop_protection = loop_protection
        self.allow_destructive_operations = allow_destructive_operations
        self.viewport_image_data_url = viewport_image_data_url

        self.tool_queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.done_event = threading.Event()
        self.lock = threading.Lock()

        self.status = "Starting"
        self.error = None
        self.response_text = ""
        self.response_id = None
        self.output = None
        self.tool_calls = 0
        self.events = []

        self.thread = threading.Thread(
            target=self._run,
            name="GPTBlend-Agent",
            daemon=True,
        )

    def start(self):
        self._log(f"Started {self.model} task")
        self.thread.start()

    def _log(self, message):
        with self.lock:
            self.events.append(message)
            if len(self.events) > 80:
                self.events = self.events[-80:]

    def _set_status(self, status):
        with self.lock:
            self.status = status

    def _progress(self, status):
        self._set_status(status)
        self._log(status)

    def _request_tool_on_main_thread(self, name, arguments):
        if self.cancel_event.is_set():
            return {"ok": False, "cancelled": True, "message": "Task cancelled."}

        request = ToolRequest(name=name, arguments=arguments)
        with self.lock:
            self.tool_calls += 1
        self._log(f"Tool: {name}")
        self.tool_queue.put(request)

        while not request.event.wait(0.05):
            if self.cancel_event.is_set():
                return {"ok": False, "cancelled": True, "message": "Task cancelled."}

        result = request.result or {
            "ok": False,
            "message": "Blender tool returned no result.",
        }
        self._log(
            f"Tool result: {name} {'OK' if result.get('ok') else 'FAILED'}"
        )
        return result

    def _run(self):
        try:
            response_text, output, response_id = send_message(
                self.api_key,
                self.model,
                self.user_message,
                self.context_text,
                previous_response_id=self.previous_response_id,
                max_tool_rounds=self.max_tool_rounds,
                max_total_tool_calls=self.max_total_tool_calls,
                loop_protection=self.loop_protection,
                allow_destructive_operations=self.allow_destructive_operations,
                tool_executor=self._request_tool_on_main_thread,
                progress_callback=self._progress,
                cancel_event=self.cancel_event,
                viewport_image_data_url=self.viewport_image_data_url,
            )

            with self.lock:
                self.response_text = response_text or "GPT returned no text response."
                self.output = output
                self.response_id = response_id
                self.status = "Ready"
        except GPTBlendError as exc:
            with self.lock:
                self.error = str(exc)
                self.status = "Cancelled" if self.cancel_event.is_set() else "Error"
        except Exception as exc:
            with self.lock:
                self.error = f"Unexpected error: {exc}"
                self.status = "Error"
        finally:
            self.done_event.set()

    def cancel(self):
        self.cancel_event.set()
        self._set_status("Stopping")

    def snapshot(self):
        with self.lock:
            return {
                "status": self.status,
                "error": self.error,
                "response_text": self.response_text,
                "response_id": self.response_id,
                "output": self.output,
                "tool_calls": self.tool_calls,
                "events": list(self.events),
                "done": self.done_event.is_set(),
            }
