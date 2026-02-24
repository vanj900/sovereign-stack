"""Physiologically-coupled drive system for the GhostMesh cognitive layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.metabolic_engine import MetabolicEngine


class DrivePriority(Enum):
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1


@dataclass
class Drive:
    """A single physiological drive with urgency derived from metabolic state."""

    name: str
    priority: DrivePriority
    urgency: float = 0.0
    description: str = ""

    def __lt__(self, other: "Drive") -> bool:
        return (self.priority.value, self.urgency) < (
            other.priority.value,
            other.urgency,
        )


class GoalManager:
    """
    Generates and ranks goals that are directly coupled to metabolic variables.

    Drive urgency is recomputed on every call to :meth:`update`.
    """

    def __init__(self, engine: "MetabolicEngine"):
        self._engine = engine

    def update(self) -> list[Drive]:
        """Recompute all drive urgencies from current metabolic state.

        Returns the list of drives sorted by combined (priority, urgency),
        highest urgency first.
        """
        e = self._engine
        p = e.p
        drives = [
            Drive(
                name="survival",
                priority=DrivePriority.CRITICAL,
                urgency=1.0 - (e.E / p["E_max"]),
                description="Acquire energy to avoid death",
            ),
            Drive(
                name="coherence",
                priority=DrivePriority.HIGH,
                urgency=1.0 - e.M,
                description="Repair memory to preserve identity",
            ),
            Drive(
                name="stability",
                priority=DrivePriority.HIGH,
                urgency=1.0 - e.S,
                description="Reduce entropy to avoid system incoherence",
            ),
            Drive(
                name="cooling",
                priority=DrivePriority.HIGH,
                urgency=max(
                    0.0,
                    (e.T - p["T_safe"]) / (p["T_critical"] - p["T_safe"]),
                ),
                description="Dissipate heat to prevent thermal damage",
            ),
            Drive(
                name="exploration",
                priority=DrivePriority.MEDIUM,
                urgency=0.5,  # constant baseline; epistemic engine may raise this
                description="Gather information about the environment",
            ),
        ]
        drives.sort(key=lambda d: (d.priority.value, d.urgency), reverse=True)
        return drives

    def generate_actions(self) -> list[str]:
        """Return action names ordered by current drive urgency."""
        drives = self.update()
        action_map = {
            "survival": "harvest_energy",
            "coherence": "repair_memory",
            "stability": "repair_stability",
            "cooling": "idle_cool",
            "exploration": "explore",
        }
        return [action_map[d.name] for d in drives]
