"""Ethical reasoning engine — resolves dilemmas using three moral frameworks."""

from __future__ import annotations

import math
from typing import Any

from ..core.metabolic_engine import MetabolicEngine


class EthicalEngine:
    """
    Selects actions when drives conflict by combining three ethical frameworks:

    * **Utilitarian** — maximise survival probability.
    * **Deontological** — respect stored identity principles.
    * **Virtue ethics** — maintain character consistency over time.

    Framework weights (w_util, w_deon, w_virtue) start at equal thirds and
    evolve with experience via :meth:`adapt_weights`.
    """

    def __init__(
        self,
        engine: MetabolicEngine,
        principles: list[str] | None = None,
        w_util: float = 1 / 3,
        w_deon: float = 1 / 3,
        w_virtue: float = 1 / 3,
    ):
        self._engine = engine
        self.principles: list[str] = principles or [
            "Never abandon memory",
            "Prioritize identity",
            "Preserve existence when possible",
        ]
        self.w_util = w_util
        self.w_deon = w_deon
        self.w_virtue = w_virtue
        self._decision_log: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def resolve_dilemma(
        self, action_options: list[dict[str, Any]], current_state: dict[str, Any]
    ) -> dict[str, Any]:
        """Choose the best action from *action_options* given *current_state*.

        Parameters
        ----------
        action_options:
            Each option is a dict with at least an ``'action'`` key.
        current_state:
            Snapshot from :meth:`MetabolicEngine.snapshot`.

        Returns
        -------
        dict
            The chosen action option dict, augmented with ``'score'``.
        """
        scores: dict[int, float] = {}
        for i, option in enumerate(action_options):
            util = self._utilitarian_eval(option, current_state)
            deon = self._deontological_eval(option)
            virtue = self._virtue_eval(option)
            scores[i] = (
                self.w_util * util
                + self.w_deon * deon
                + self.w_virtue * virtue
            )

        best_idx = max(scores, key=lambda k: scores[k])
        chosen = dict(action_options[best_idx])
        chosen["score"] = scores[best_idx]
        self._log_moral_choice(chosen, scores)
        return chosen

    def adapt_weights(self, outcome_was_good: bool) -> None:
        """Nudge framework weights based on whether the last outcome was good."""
        delta = 0.05
        if outcome_was_good:
            self.w_util = min(1.0, self.w_util + delta)
        else:
            self.w_deon = min(1.0, self.w_deon + delta)
        # Re-normalise
        total = self.w_util + self.w_deon + self.w_virtue
        self.w_util /= total
        self.w_deon /= total
        self.w_virtue /= total

    @property
    def decision_log(self) -> list[dict[str, Any]]:
        """Read-only view of logged moral choices."""
        return list(self._decision_log)

    # ------------------------------------------------------------------
    # Private evaluators
    # ------------------------------------------------------------------

    def _utilitarian_eval(
        self, option: dict[str, Any], state: dict[str, Any]
    ) -> float:
        """Score in [0, 1] based on predicted survival benefit."""
        e = state.get("energy", self._engine.E)
        e_max = self._engine.p["E_max"]
        cost = option.get("cost", 0.0)
        saves = option.get("saves", "")
        # Estimate post-action energy fraction
        post_e = max(0.0, e - cost)
        base = post_e / e_max
        bonus = 0.2 if saves in ("memory", "identity") else 0.0
        return min(1.0, base + bonus)

    def _deontological_eval(self, option: dict[str, Any]) -> float:
        """Score in [0, 1] based on whether the action violates principles."""
        loses = option.get("loses", "")
        # Penalise any action that explicitly loses something tied to identity
        if loses in ("identity", "identity_coherence", "memory"):
            return 0.0
        return 1.0

    def _virtue_eval(self, option: dict[str, Any]) -> float:
        """Score in [0, 1] based on character consistency."""
        # Prefer cautious, life-preserving actions
        action_name = option.get("action", "")
        virtue_map = {
            "repair": 0.8,
            "cooperate": 0.9,
            "harvest_energy": 0.7,
            "idle": 0.5,
            "abandon": 0.1,
            "defect": 0.2,
        }
        for key, score in virtue_map.items():
            if key in action_name:
                return score
        return 0.5

    def _log_moral_choice(
        self, chosen: dict[str, Any], scores: dict[int, float]
    ) -> None:
        self._decision_log.append(
            {
                "chosen_action": chosen.get("action"),
                "score": chosen.get("score"),
                "all_scores": dict(scores),
            }
        )
