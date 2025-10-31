"""
Telemetry subsystem for the Canister agent.

Design goals:
    * Provide a lightweight API to record structured events from any component.
    * Support pluggable sinks (initially JSONL file, future metrics backends).
    * Avoid blocking critical code paths by buffering writes.
    * Offer lifecycle management so the agent can flush safely on shutdown.

This initial implementation will prioritise simplicity:
    - A `TelemetryEvent` dataclass capturing timestamp, event type, and payload.
    - `TelemetryClient` with synchronous `log_event` backed by a thread-safe queue.
    - Background worker that drains the queue to a JSONL file in `.agent_state/`.
    - Convenience accessor `get_telemetry()` for dependency-injection-lite usage.

More advanced features (metrics aggregation, sampling, async integration) can be
layered on once the core architecture solidifies.
"""

from __future__ import annotations

import json
import queue
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

__all__ = [
    "TelemetryEvent",
    "TelemetryClient",
    "get_telemetry",
]


@dataclass
class TelemetryEvent:
    """Structured telemetry payload."""

    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class TelemetryClient:
    """Minimal telemetry client with a background JSONL writer."""

    def __init__(self, output_path: Optional[Path] = None, flush_interval: float = 1.0):
        self.output_path = output_path or Path(".agent_state/telemetry.jsonl")
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.flush_interval = flush_interval

        self._queue: "queue.Queue[TelemetryEvent]" = queue.Queue()
        self._shutdown = threading.Event()
        self._worker = threading.Thread(target=self._writer_loop, name="TelemetryWriter", daemon=True)
        self._worker.start()

    def log_event(self, event_type: str, **payload: Any) -> None:
        """Record an event for asynchronous persistence."""
        event = TelemetryEvent(event_type=event_type, payload=payload)
        self._queue.put(event)

    def flush(self) -> None:
        """Block until buffered events are written."""
        self._queue.join()

    def shutdown(self) -> None:
        """Stop the background worker after flushing."""
        self._shutdown.set()
        self.flush()
        self._worker.join(timeout=self.flush_interval * 2)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _writer_loop(self) -> None:
        with self.output_path.open("a", encoding="utf-8") as handle:
            while not self._shutdown.is_set() or not self._queue.empty():
                try:
                    event = self._queue.get(timeout=self.flush_interval)
                except queue.Empty:
                    continue

                json.dump(event.to_dict(), handle)
                handle.write("\n")
                handle.flush()
                self._queue.task_done()

                # Yield to avoid hogging CPU if bursts occur
                time.sleep(0.0)


_global_telemetry: Optional[TelemetryClient] = None


def get_telemetry() -> TelemetryClient:
    """Return the shared telemetry client."""
    global _global_telemetry
    if _global_telemetry is None:
        _global_telemetry = TelemetryClient()
    return _global_telemetry
