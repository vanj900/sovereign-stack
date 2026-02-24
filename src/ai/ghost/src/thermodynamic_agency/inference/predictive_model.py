"""Internal world simulator — forward-models action outcomes."""

from __future__ import annotations

import math
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.metabolic_engine import MetabolicEngine
    from .perception_action import Action


class PredictiveModel:
    """
    Maintains an internal model of the agent's body and the environment to
    answer: *"If I do X, will I survive?"*

    Prediction errors drive Bayesian belief updates.
    """

    def __init__(self, engine: "MetabolicEngine"):
        self._engine = engine
        # Simple learnable scale factors for prediction accuracy.
        self.model_parameters: dict[str, float] = {
            "heat_scale": 1.0,
            "memory_scale": 1.0,
            "entropy_scale": 1.0,
        }
        self._last_prediction: dict[str, Any] | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict_outcome(self, action: "Action") -> dict[str, Any]:
        """Simulate the metabolic consequence of executing *action*.

        Returns a dict with:
        - ``survival_prob`` — predicted probability of surviving the action.
        - ``final_state`` — predicted E, T, M, S after the action.
        - ``prediction_uncertainty`` — current model uncertainty [0, 1].
        - ``information_gain`` — estimated epistemic value [0, 1].
        """
        e = self._engine
        dyn = e._dynamics

        # Forward-simulate the state after this action
        cost = action.energy_cost
        gain = getattr(action, "energy_gain", 0.0)
        pred_E = max(0.0, min(e.E - cost + gain, e.p["E_max"]))
        pred_T = e.T + dyn.heat_generated(cost) * self.model_parameters["heat_scale"]
        pred_M = max(
            0.0,
            e.M
            - dyn.memory_corruption(pred_T) * self.model_parameters["memory_scale"],
        )
        pred_S = max(
            0.0,
            e.S
            - dyn.entropy_increase(cost) * self.model_parameters["entropy_scale"],
        )

        survival_prob = dyn.survival_probability(pred_E, pred_T, pred_M, pred_S)
        uncertainty = self._compute_uncertainty()
        info_gain = action.information_gain

        result: dict[str, Any] = {
            "survival_prob": survival_prob,
            "final_state": {
                "E": pred_E,
                "T": pred_T,
                "M": pred_M,
                "S": pred_S,
            },
            "prediction_uncertainty": uncertainty,
            "information_gain": info_gain,
        }
        self._last_prediction = result
        return result

    def update_beliefs(self, actual_outcome: dict[str, Any]) -> None:
        """Bayesian-style update of model parameters after an action.

        Parameters
        ----------
        actual_outcome:
            Dict with actual E, T, M, S after the action (from engine snapshot).
        """
        if self._last_prediction is None:
            return

        pred_state = self._last_prediction["final_state"]
        # Compute normalised prediction errors
        errors = {
            "heat_scale": self._prediction_error(
                actual_outcome.get("temperature", self._engine.T),
                pred_state.get("T", self._engine.T),
            ),
            "memory_scale": self._prediction_error(
                actual_outcome.get("memory_integrity", self._engine.M),
                pred_state.get("M", self._engine.M),
            ),
            "entropy_scale": self._prediction_error(
                actual_outcome.get("stability", self._engine.S),
                pred_state.get("S", self._engine.S),
            ),
        }

        learning_rate = 0.1
        for key, error in errors.items():
            self.model_parameters[key] = max(
                0.1,
                self.model_parameters[key] - learning_rate * error,
            )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _compute_uncertainty(self) -> float:
        """Heuristic uncertainty based on deviation of model params from 1.0."""
        deviations = [abs(v - 1.0) for v in self.model_parameters.values()]
        return min(1.0, sum(deviations) / len(deviations))

    @staticmethod
    def _prediction_error(actual: float, predicted: float) -> float:
        """Signed normalised prediction error."""
        return actual - predicted
