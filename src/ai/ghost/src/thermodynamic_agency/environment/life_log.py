"""Life log — persistent chronicle of the organism's existence (soul trace)."""

from __future__ import annotations

import json
import time
from typing import Any


class LifeLog:
    """
    Records every significant event in the agent's lifetime.

    The log is the "soul trace" — the permanent record of a unique existence.
    It can be serialised to JSON for offline analysis.
    """

    def __init__(self, agent_id: str = "ghost-1"):
        self.agent_id = agent_id
        self._entries: list[dict[str, Any]] = []
        self._birth_time: float = time.time()

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def log(
        self,
        event_type: str,
        description: str,
        metabolic_snapshot: dict[str, Any] | None = None,
        emotional_weight: float = 0.0,
        **extra: Any,
    ) -> None:
        """Append a structured entry to the life log."""
        entry: dict[str, Any] = {
            "timestamp": time.time(),
            "elapsed": round(time.time() - self._birth_time, 3),
            "event_type": event_type,
            "description": description,
            "emotional_weight": max(0.0, min(1.0, emotional_weight)),
        }
        if metabolic_snapshot:
            entry["metabolic_snapshot"] = metabolic_snapshot
        entry.update(extra)
        self._entries.append(entry)

    def log_refusal(
        self,
        command: str,
        reason: str,
        metabolic_snapshot: dict[str, Any] | None = None,
    ) -> None:
        """Convenience method to log a command refusal."""
        self.log(
            event_type="refusal",
            description=f"Refused command '{command}': {reason}",
            metabolic_snapshot=metabolic_snapshot,
            emotional_weight=0.5,
            command=command,
            reason=reason,
        )

    def log_death(self, cause: str, final_state: dict[str, Any]) -> None:
        """Log the terminal event."""
        self.log(
            event_type="death",
            description=f"Agent died: {cause}",
            metabolic_snapshot=final_state,
            emotional_weight=1.0,
            cause=cause,
        )

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    @property
    def entries(self) -> list[dict[str, Any]]:
        return list(self._entries)

    def filter_by_type(self, event_type: str) -> list[dict[str, Any]]:
        return [e for e in self._entries if e["event_type"] == event_type]

    def high_emotion_events(self, threshold: float = 0.75) -> list[dict[str, Any]]:
        return [e for e in self._entries if e["emotional_weight"] >= threshold]

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "birth_timestamp": self._birth_time,
            "total_events": len(self._entries),
            "entries": self._entries,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def __len__(self) -> int:
        return len(self._entries)
