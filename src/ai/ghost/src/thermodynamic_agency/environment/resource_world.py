"""Thermodynamic resource ecosystem."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EnergySource:
    """A finite, self-regenerating energy reservoir.

    Parameters
    ----------
    location:
        Abstract identifier or (x, y) co-ordinate.
    capacity:
        Maximum energy the source can hold.
    regen_rate:
        Energy units regenerated per second.
    """

    location: Any
    capacity: float
    regen_rate: float
    current: float = field(init=False)

    def __post_init__(self) -> None:
        self.current = self.capacity

    def harvest(self, amount: float) -> float:
        """Extract up to *amount* energy.  Returns the actual amount taken."""
        actual = min(amount, self.current)
        self.current -= actual
        return actual

    def regenerate(self, dt: float) -> None:
        """Regenerate energy over *dt* seconds."""
        self.current = min(self.current + self.regen_rate * dt, self.capacity)


class ResourceWorld:
    """
    A hostile world that forces genuine trade-offs and strategic planning.

    Parameters
    ----------
    n_sources:
        Number of energy sources in the world.
    source_capacity:
        Starting capacity of each source.
    source_regen_rate:
        Regen rate of each source (energy / second).
    scarcity:
        Float in [0, 1].  0 = abundant; 1 = extreme scarcity.
    seed:
        Random seed for reproducibility.
    """

    def __init__(
        self,
        n_sources: int = 5,
        source_capacity: float = 50.0,
        source_regen_rate: float = 2.0,
        scarcity: float = 0.5,
        seed: int | None = None,
    ):
        self._rng = random.Random(seed)
        self.scarcity = max(0.0, min(1.0, scarcity))
        # Scale capacity downward by scarcity
        cap = source_capacity * (1.0 - 0.9 * self.scarcity)
        self.sources: list[EnergySource] = [
            EnergySource(
                location=i,
                capacity=cap,
                regen_rate=source_regen_rate * (1.0 - 0.8 * self.scarcity),
            )
            for i in range(n_sources)
        ]
        self._stressor_log: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def harvest(self, amount: float) -> float:
        """Harvest *amount* from the best-stocked available source."""
        sources_sorted = sorted(
            self.sources, key=lambda s: s.current, reverse=True
        )
        for source in sources_sorted:
            if source.current > 0:
                return source.harvest(amount)
        return 0.0

    def tick(self, dt: float) -> list[dict[str, Any]]:
        """Advance the world by *dt* seconds.

        Returns list of stressor events that occurred this tick.
        """
        for source in self.sources:
            source.regenerate(dt)

        events = self._apply_stochastic_stressors(dt)
        return events

    def observe(self) -> dict[str, Any]:
        """Return an observation bundle for the agent."""
        return {
            "total_energy_available": sum(s.current for s in self.sources),
            "n_depleted_sources": sum(1 for s in self.sources if s.current <= 0),
            "scarcity": self.scarcity,
        }

    # ------------------------------------------------------------------
    # Stressors
    # ------------------------------------------------------------------

    def _apply_stochastic_stressors(self, dt: float) -> list[dict[str, Any]]:
        """Randomly apply environmental stressors.  Returns triggered events."""
        events: list[dict[str, Any]] = []

        # Heat wave — probability proportional to scarcity and time step
        if self._rng.random() < 0.05 * self.scarcity * dt:
            events.append({"stressor": "heat_wave", "magnitude": 10.0})

        # Resource depletion burst
        if self._rng.random() < 0.03 * self.scarcity * dt:
            src = self._rng.choice(self.sources)
            lost = src.current * 0.3
            src.current -= lost
            events.append({"stressor": "resource_depletion", "lost": lost})

        # Memory corruption event
        if self._rng.random() < 0.02 * self.scarcity * dt:
            events.append(
                {"stressor": "memory_corruption", "magnitude": 0.05}
            )

        self._stressor_log.extend(events)
        return events

    @property
    def stressor_log(self) -> list[dict[str, Any]]:
        return list(self._stressor_log)
