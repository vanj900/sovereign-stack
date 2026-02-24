"""Core thermodynamic state machine — the body of the organism."""

from __future__ import annotations

import time
from typing import Any, Callable

from .entropy_dynamics import DEFAULTS, EntropyDynamics
from .failure_modes import (
    EnergyDeathException,
    EntropyDeathException,
    MemoryCollapseException,
    ThermalDeathException,
)


class MetabolicEngine:
    """
    Maintains E, T, M, S and enforces thermodynamic laws on every operation.

    Parameters
    ----------
    E_max:
        Maximum (and initial) energy level.
    T_critical:
        Temperature at which thermal death occurs.
    params:
        Override any value from ``entropy_dynamics.DEFAULTS``.
    """

    def __init__(
        self,
        E_max: float = DEFAULTS["E_max"],
        T_critical: float = DEFAULTS["T_critical"],
        params: dict[str, float] | None = None,
    ):
        p = dict(DEFAULTS)
        if params:
            p.update(params)
        p["E_max"] = E_max
        p["T_critical"] = T_critical

        self._dynamics = EntropyDynamics(p)
        self.p = self._dynamics.p

        # State variables
        self.E: float = E_max
        self.T: float = self.p["T_ambient"]
        self.M: float = 1.0
        self.S: float = 1.0

        self._birth_time: float = time.time()
        self._age: float = 0.0
        self._alive: bool = True
        self._fail_reason: str | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def alive(self) -> bool:
        """True while the organism has not entered a fatal failure mode."""
        return self._alive

    @property
    def age(self) -> float:
        """Simulated age in seconds since birth."""
        return self._age

    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-serialisable snapshot of the current metabolic state."""
        return {
            "timestamp": time.time(),
            "energy": round(self.E, 4),
            "temperature": round(self.T, 4),
            "memory_integrity": round(self.M, 4),
            "stability": round(self.S, 4),
            "age": round(self._age, 2),
            "alive": self._alive,
            "fail_reason": self._fail_reason,
        }

    def compute(self, task: Any, cost: float) -> Any:
        """Execute *task* under a thermodynamic cost of *cost* energy units.

        Raises an appropriate :class:`MetabolicFailure` sub-class if a
        failure condition is triggered before or after execution.
        """
        self._require_alive()

        if self.E < cost:
            self._die("energy_death")
            raise EnergyDeathException(
                f"Insufficient energy: have {self.E:.2f}, need {cost:.2f}",
                self.snapshot(),
            )

        # Apply thermodynamic costs
        self.E -= cost
        self.T += self._dynamics.heat_generated(cost)
        self.M -= self._dynamics.memory_corruption(self.T)
        self.M -= self._dynamics.memory_age_decay(0)  # instantaneous age factor
        self.S -= self._dynamics.entropy_increase(cost)

        # Clamp to valid ranges
        self.M = max(0.0, min(1.0, self.M))
        self.S = max(0.0, min(1.0, self.S))

        self._check_failure_modes()

        result = task() if callable(task) else task
        return result

    def passive_decay(self, dt: float) -> None:
        """Simulate entropy and passive decay over *dt* seconds."""
        self._require_alive()

        self._age += dt
        self.E -= self._dynamics.energy_leak(dt)
        self.T -= self._dynamics.heat_dissipated(self.T, dt)
        self.T = max(self.p["T_ambient"], self.T)
        self.M -= self._dynamics.memory_age_decay(dt)
        self.S -= self._dynamics.stability_passive_decay(dt)

        self.M = max(0.0, min(1.0, self.M))
        self.S = max(0.0, min(1.0, self.S))

        self._check_failure_modes()

    def replenish_energy(self, amount: float) -> float:
        """Add up to *amount* energy, capped at E_max.  Returns actual gained."""
        self._require_alive()
        before = self.E
        self.E = min(self.E + amount, self.p["E_max"])
        return self.E - before

    def repair_memory(self, effort: float) -> float:
        """Restore memory integrity by *effort* (costs the same in energy)."""
        self._require_alive()
        cost = effort
        if self.E < cost:
            effort = self.E
            cost = self.E
        self.E -= cost
        before = self.M
        self.M = min(1.0, self.M + effort)
        return self.M - before

    def repair_stability(self, effort: float) -> float:
        """Restore stability by *effort* (costs the same in energy)."""
        self._require_alive()
        cost = effort
        if self.E < cost:
            effort = self.E
            cost = self.E
        self.E -= cost
        before = self.S
        self.S = min(1.0, self.S + effort)
        return self.S - before

    def survival_probability(self) -> float:
        """Heuristic survival probability [0, 1]."""
        return self._dynamics.survival_probability(self.E, self.T, self.M, self.S)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _heat_generated(self, cost: float) -> float:
        return self._dynamics.heat_generated(cost)

    def _memory_corruption(self, T: float) -> float:
        return self._dynamics.memory_corruption(T)

    def _entropy_increase(self, cost: float) -> float:
        return self._dynamics.entropy_increase(cost)

    def _check_failure_modes(self) -> None:
        if self.E <= 0:
            self._die("energy_death")
            raise EnergyDeathException(
                "Energy exhausted", self.snapshot()
            )
        if self.T > self.p["T_critical"]:
            self._die("thermal_death")
            raise ThermalDeathException(
                f"Temperature {self.T:.2f} K exceeds critical {self.p['T_critical']:.2f} K",
                self.snapshot(),
            )
        if self.S <= 0:
            self._die("entropy_death")
            raise EntropyDeathException(
                "Stability exhausted — entropy death", self.snapshot()
            )
        if self.M < self.p["M_min"]:
            self._die("memory_collapse")
            raise MemoryCollapseException(
                f"Memory integrity {self.M:.3f} below minimum {self.p['M_min']:.3f}",
                self.snapshot(),
            )

    def _die(self, reason: str) -> None:
        self._alive = False
        self._fail_reason = reason

    def _require_alive(self) -> None:
        if not self._alive:
            raise RuntimeError(
                f"Agent is dead (cause: {self._fail_reason}).  No resurrection."
            )

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"MetabolicEngine(E={self.E:.1f}, T={self.T:.1f}K, "
            f"M={self.M:.3f}, S={self.S:.3f}, alive={self._alive})"
        )
