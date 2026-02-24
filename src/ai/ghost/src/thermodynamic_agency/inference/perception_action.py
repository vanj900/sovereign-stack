"""Sensorimotor interface — action definitions and environment perception."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Action:
    """Represents a candidate action the agent may execute.

    Attributes
    ----------
    name:
        Human-readable label (e.g. ``"harvest_energy"``).
    energy_cost:
        Energy units consumed when the action is executed.
    energy_gain:
        Expected energy gain from the action (e.g. harvest amount).
    information_gain:
        Epistemic value — how much uncertainty it resolves [0, 1].
    metadata:
        Arbitrary extra data (repair targets, harvest amounts, …).
    """

    name: str
    energy_cost: float = 0.0
    energy_gain: float = 0.0
    information_gain: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def thermodynamic_cost(self) -> float:
        """Alias kept for compatibility with the architecture spec."""
        return self.energy_cost


# ------------------------------------------------------------------
# Pre-built action catalogue
# ------------------------------------------------------------------

def harvest_energy_action(amount: float = 20.0) -> Action:
    return Action(
        name="harvest_energy",
        energy_cost=1.0,     # small locomotion cost
        energy_gain=amount,  # expected energy harvested
        information_gain=0.0,
        metadata={"harvest_amount": amount},
    )


def repair_memory_action(effort: float = 0.1) -> Action:
    return Action(
        name="repair_memory",
        energy_cost=effort * 2,
        information_gain=0.0,
        metadata={"repair_effort": effort},
    )


def repair_stability_action(effort: float = 0.1) -> Action:
    return Action(
        name="repair_stability",
        energy_cost=effort * 2,
        information_gain=0.0,
        metadata={"repair_effort": effort},
    )


def idle_cool_action(dt: float = 1.0) -> Action:
    return Action(
        name="idle_cool",
        energy_cost=0.1 * dt,
        information_gain=0.0,
        metadata={"dt": dt},
    )


def explore_action() -> Action:
    return Action(
        name="explore",
        energy_cost=2.0,
        information_gain=0.3,
        metadata={},
    )


# Mapping from goal-manager action names → constructors
ACTION_REGISTRY: dict[str, Any] = {
    "harvest_energy": harvest_energy_action,
    "repair_memory": repair_memory_action,
    "repair_stability": repair_stability_action,
    "idle_cool": idle_cool_action,
    "explore": explore_action,
}


class PerceptionAction:
    """Bridge between the environment and the agent's decision machinery.

    Translates raw environment observations into an :class:`Action` catalogue
    and applies chosen actions back to the :class:`MetabolicEngine`.
    """

    def __init__(self, engine: Any, environment: Any | None = None):
        self._engine = engine
        self._environment = environment

    def perceive(self) -> dict[str, Any]:
        """Sample the current state from the engine (and optionally the env)."""
        obs: dict[str, Any] = self._engine.snapshot()
        if self._environment is not None:
            obs["env"] = self._environment.observe()
        return obs

    def available_actions(self) -> list[Action]:
        """Return the standard action catalogue."""
        return [factory() for factory in ACTION_REGISTRY.values()]

    def execute(self, action: Action, resource_world: Any | None = None) -> dict[str, Any]:
        """Apply *action* to the engine and (optionally) the resource world.

        Returns a dict with the post-action engine snapshot.
        """
        name = action.name
        meta = action.metadata

        if name == "harvest_energy":
            amount = meta.get("harvest_amount", 20.0)
            if resource_world is not None:
                amount = resource_world.harvest(amount)
            self._engine.replenish_energy(amount)

        elif name == "repair_memory":
            effort = meta.get("repair_effort", 0.1)
            self._engine.repair_memory(effort)

        elif name == "repair_stability":
            effort = meta.get("repair_effort", 0.1)
            self._engine.repair_stability(effort)

        elif name in ("idle_cool", "explore"):
            dt = meta.get("dt", 1.0)
            # Generic compute call with minimal cost
            self._engine.compute(lambda: None, action.energy_cost)

        else:
            # Unknown action — default minimal-cost compute
            self._engine.compute(lambda: None, action.energy_cost)

        return self._engine.snapshot()
