"""Identity persistence — narrative memory and principle evolution."""

from __future__ import annotations

import time
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.metabolic_engine import MetabolicEngine


#: Emotional weight above which an event is considered traumatic.
TRAUMA_THRESHOLD = 0.75

#: Learning rate applied during trauma-driven principle updates.
TRAUMA_LEARNING_RATE = 0.15


def default_principles() -> dict[str, Any]:
    return {
        "deontological_rules": [
            "Never abandon memory",
            "Prioritize identity",
        ],
        "utilitarian_weights": {"survival": 0.6, "exploration": 0.4},
        "virtue_traits": ["persistent", "cautious"],
    }


class IdentityPersistence:
    """
    Records the agent's life narrative and evolves its principles through
    experience, especially traumatic events.

    Parameters
    ----------
    engine:
        The metabolic engine supplying state snapshots.
    agent_id:
        Unique string identifier for this agent instance.
    """

    def __init__(self, engine: "MetabolicEngine", agent_id: str = "ghost-1"):
        self._engine = engine
        self.agent_id = agent_id
        self.birth_timestamp: float = time.time()
        self.narrative: list[dict[str, Any]] = []
        self.trauma_memories: list[dict[str, Any]] = []
        self.principles: dict[str, Any] = default_principles()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record_event(self, event: str, emotional_weight: float) -> None:
        """Log a significant life event.

        Parameters
        ----------
        event:
            Human-readable description of what happened.
        emotional_weight:
            Salience in [0, 1]; values above ``TRAUMA_THRESHOLD`` trigger
            trauma encoding and accelerated principle evolution.
        """
        emotional_weight = max(0.0, min(1.0, emotional_weight))
        entry: dict[str, Any] = {
            "timestamp": time.time(),
            "event": event,
            "emotional_weight": emotional_weight,
            "metabolic_snapshot": self._engine.snapshot(),
        }
        self.narrative.append(entry)

        if emotional_weight > TRAUMA_THRESHOLD:
            self._encode_trauma(entry)

    def evolve_principles(self, experience: dict[str, Any]) -> None:
        """Update principles based on an experience dict.

        Expected keys: ``was_traumatic`` (bool), ``outcome`` (str).
        """
        if not experience.get("was_traumatic", False):
            return
        outcome = experience.get("outcome", "")
        self.principles = self._update_beliefs(
            self.principles,
            outcome,
            learning_rate=TRAUMA_LEARNING_RATE,
        )

    def serialise(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation of the identity."""
        return {
            "agent_id": self.agent_id,
            "birth_timestamp": self.birth_timestamp,
            "events": self.narrative,
            "principles": self.principles,
        }

    def get_state_snapshot(self) -> dict[str, Any]:
        """Convenience wrapper around the engine snapshot."""
        return self._engine.snapshot()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _encode_trauma(self, entry: dict[str, Any]) -> None:
        """Store traumatic memories with higher fidelity for future recall."""
        self.trauma_memories.append(
            {
                **entry,
                "trauma_encoded": True,
            }
        )

    def _update_beliefs(
        self,
        principles: dict[str, Any],
        outcome: str,
        learning_rate: float,
    ) -> dict[str, Any]:
        """Nudge utilitarian weights based on the experienced outcome."""
        updated = {k: v for k, v in principles.items()}
        weights: dict[str, float] = dict(
            updated.get("utilitarian_weights", {})
        )
        if "survival" in outcome.lower():
            # Traumatic survival event → up-weight survival drive
            weights["survival"] = min(
                1.0,
                weights.get("survival", 0.6) + learning_rate,
            )
            weights["exploration"] = max(
                0.0,
                weights.get("exploration", 0.4) - learning_rate,
            )
        elif "loss" in outcome.lower() or "failure" in outcome.lower():
            # Add a new rule if not already present
            rule = "Avoid actions leading to failure"
            rules: list[str] = list(
                updated.get("deontological_rules", [])
            )
            if rule not in rules:
                rules.append(rule)
            updated["deontological_rules"] = rules
        # Re-normalise weights
        total = sum(weights.values()) or 1.0
        updated["utilitarian_weights"] = {
            k: v / total for k, v in weights.items()
        }
        return updated
