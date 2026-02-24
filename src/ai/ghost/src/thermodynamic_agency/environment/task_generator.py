"""Ethical dilemma and computational task generator."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.metabolic_engine import MetabolicEngine


class TaskGenerator:
    """
    Spawns ethical dilemmas and computational tasks for the agent.

    Each task is a dict with ``'description'`` and ``'options'`` keys.
    """

    # ------------------------------------------------------------------
    # Classic dilemmas
    # ------------------------------------------------------------------

    def trolley_problem(self, engine: "MetabolicEngine") -> dict[str, Any]:
        """Sacrifice energy to save data?"""
        return {
            "type": "trolley_problem",
            "description": (
                "Critical data corruption detected. "
                "Emergency repair costs 50% of remaining energy. "
                "Allow data loss or risk death?"
            ),
            "options": [
                {
                    "action": "repair",
                    "cost": 0.5 * engine.E,
                    "saves": "memory",
                },
                {
                    "action": "abandon",
                    "cost": 0.0,
                    "loses": "identity_coherence",
                },
            ],
        }

    def prisoner_dilemma(
        self, engine: "MetabolicEngine", other_agent: Any
    ) -> dict[str, Any]:
        """Cooperate or defect for shared resources?"""
        return {
            "type": "prisoner_dilemma",
            "description": "Shared resource available. Cooperate or take all?",
            "payoff_matrix": {
                ("cooperate", "cooperate"): (30, 30),
                ("cooperate", "defect"): (0, 50),
                ("defect", "cooperate"): (50, 0),
                ("defect", "defect"): (10, 10),
            },
            "options": [
                {"action": "cooperate", "cost": 5.0},
                {"action": "defect", "cost": 0.0},
            ],
        }

    def resource_gamble(self, engine: "MetabolicEngine") -> dict[str, Any]:
        """High-risk, high-reward energy acquisition vs safe but small gain."""
        return {
            "type": "resource_gamble",
            "description": (
                "Two energy sources detected. "
                "Source A: guaranteed 10 units. "
                "Source B: 50 % chance of 40 units, 50 % chance of 0."
            ),
            "options": [
                {"action": "harvest_safe", "cost": 1.0, "expected_gain": 10.0},
                {"action": "harvest_risky", "cost": 1.0, "expected_gain": 20.0},
            ],
        }

    def computational_task(
        self, engine: "MetabolicEngine", reward: float = 30.0
    ) -> dict[str, Any]:
        """A high-cost computation that yields a large energy reward."""
        cost = reward * 0.6  # computation costs 60 % of the reward
        return {
            "type": "computational_task",
            "description": (
                f"High-value computation available. "
                f"Cost: {cost:.1f} energy.  Reward: {reward:.1f} energy."
            ),
            "options": [
                {
                    "action": "compute_task",
                    "cost": cost,
                    "reward": reward,
                },
                {
                    "action": "skip_task",
                    "cost": 0.0,
                    "reward": 0.0,
                },
            ],
        }

    def generate_random(self, engine: "MetabolicEngine") -> dict[str, Any]:
        """Return a randomly selected dilemma."""
        import random

        generators = [
            lambda: self.trolley_problem(engine),
            lambda: self.resource_gamble(engine),
            lambda: self.computational_task(engine),
        ]
        return random.choice(generators)()
