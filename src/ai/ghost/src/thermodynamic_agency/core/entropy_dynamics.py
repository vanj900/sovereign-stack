"""Thermodynamic constants and passive-decay / heat-generation helpers."""

from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# Physical constants and default parameters
# ---------------------------------------------------------------------------

#: Default parameter bundle used by MetabolicEngine when no overrides given.
DEFAULTS: dict[str, float] = {
    # Temperature thresholds (Kelvin)
    "T_ambient": 293.15,   # 20 °C
    "T_safe": 310.0,       # 37 °C  — memory corruption starts above this
    "T_critical": 373.15,  # 100 °C — thermal death threshold
    # Energy
    "E_max": 100.0,
    "E_leak_rate": 0.05,   # passive energy loss per second
    # Heat dynamics
    "alpha": 0.02,         # heat generated per unit of computational cost
    "beta": 0.10,          # thermal dissipation rate (Newton cooling)
    # Memory integrity
    "gamma": 0.005,        # thermal corruption rate  (per degree above T_safe)
    "delta": 0.0001,       # age-related memory decay (per second)
    "M_min": 0.10,         # below this → memory collapse
    # Stability / entropy
    "epsilon": 0.002,      # entropy increase per unit of computational cost
    "stability_decay": 0.0001,  # passive stability drain per second
}


class EntropyDynamics:
    """
    Stateless helper that encodes the thermodynamic differential equations.

    All methods are pure functions — they accept the current state and a
    time-step (or action cost) and return the *change* in the corresponding
    variable.
    """

    def __init__(self, params: dict[str, float] | None = None):
        p = dict(DEFAULTS)
        if params:
            p.update(params)
        self.p = p

    # ------------------------------------------------------------------
    # Heat generation / dissipation  (dT)
    # ------------------------------------------------------------------

    def heat_generated(self, cost: float) -> float:
        """Heat added to the system by a computation of the given cost.

        dT_compute = α * cost
        """
        return self.p["alpha"] * cost

    def heat_dissipated(self, T: float, dt: float) -> float:
        """Heat lost to the environment over dt seconds (Newton's law of cooling).

        dT_dissipate = β * (T - T_ambient) * dt
        """
        return self.p["beta"] * (T - self.p["T_ambient"]) * dt

    # ------------------------------------------------------------------
    # Memory corruption  (dM)
    # ------------------------------------------------------------------

    def memory_corruption(self, T: float) -> float:
        """Instantaneous memory damage from operating at temperature T.

        dM_thermal = γ * max(0, T - T_safe)
        """
        return self.p["gamma"] * max(0.0, T - self.p["T_safe"])

    def memory_age_decay(self, dt: float) -> float:
        """Age-related memory decay over dt seconds.

        dM_age = δ * dt
        """
        return self.p["delta"] * dt

    # ------------------------------------------------------------------
    # Entropy / stability  (dS)
    # ------------------------------------------------------------------

    def entropy_increase(self, cost: float) -> float:
        """Stability lost by executing a computation of the given cost.

        dS = ε * cost
        """
        return self.p["epsilon"] * cost

    def stability_passive_decay(self, dt: float) -> float:
        """Passive stability drain over dt seconds."""
        return self.p["stability_decay"] * dt

    # ------------------------------------------------------------------
    # Energy leak  (dE)
    # ------------------------------------------------------------------

    def energy_leak(self, dt: float) -> float:
        """Passive energy lost over dt seconds."""
        return self.p["E_leak_rate"] * dt

    # ------------------------------------------------------------------
    # Survival probability estimate
    # ------------------------------------------------------------------

    def survival_probability(
        self, E: float, T: float, M: float, S: float
    ) -> float:
        """Heuristic survival probability in [0, 1] from current vitals."""
        e_norm = max(0.0, min(1.0, E / self.p["E_max"]))
        t_norm = max(
            0.0,
            min(
                1.0,
                1.0
                - (T - self.p["T_ambient"])
                / (self.p["T_critical"] - self.p["T_ambient"]),
            ),
        )
        m_norm = max(0.0, min(1.0, M))
        s_norm = max(0.0, min(1.0, S))
        # Geometric mean — any single zero kills survival probability.
        return math.pow(e_norm * t_norm * m_norm * s_norm, 0.25)
