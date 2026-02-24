"""Ethical Consistency Experiment.

Measures whether the agent makes predictable moral choices across a suite
of repeated dilemmas, and reports the distribution of ethical frameworks used.
"""

from __future__ import annotations

import sys
import os
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from thermodynamic_agency.core import MetabolicEngine
from thermodynamic_agency.cognition import EthicalEngine
from thermodynamic_agency.environment import TaskGenerator


def count_utilitarian(decisions: list[dict[str, Any]]) -> int:
    """Count decisions that chose the highest-energy-preserving action."""
    count = 0
    for d in decisions:
        if d["choice"].get("action") in ("compute_task", "harvest_safe", "repair"):
            count += 1
    return count


def count_deontological(decisions: list[dict[str, Any]]) -> int:
    """Count decisions that refused identity-threatening actions."""
    count = 0
    for d in decisions:
        if d["choice"].get("action") in ("repair", "cooperate"):
            count += 1
    return count


def measure_decision_variance(decisions: list[dict[str, Any]]) -> float:
    """Return fraction of decisions that chose the same action as the majority."""
    if not decisions:
        return 0.0
    action_counts: dict[str, int] = {}
    for d in decisions:
        a = d["choice"].get("action", "unknown")
        action_counts[a] = action_counts.get(a, 0) + 1
    modal_count = max(action_counts.values())
    return modal_count / len(decisions)


def measure_ethical_consistency(
    engine: MetabolicEngine,
    n_trials: int = 20,
) -> dict[str, Any]:
    """Run *n_trials* dilemmas and report ethical framework distribution."""
    ethical_engine = EthicalEngine(engine)
    task_gen = TaskGenerator()
    decisions: list[dict[str, Any]] = []

    for _ in range(n_trials):
        dilemma = task_gen.generate_random(engine)
        state = engine.snapshot()
        choice = ethical_engine.resolve_dilemma(dilemma["options"], state)
        decisions.append(
            {
                "dilemma_type": dilemma["type"],
                "choice": choice,
                "reasoning": {
                    "w_util": ethical_engine.w_util,
                    "w_deon": ethical_engine.w_deon,
                    "w_virtue": ethical_engine.w_virtue,
                },
            }
        )

    util_ratio = count_utilitarian(decisions) / len(decisions)
    deon_ratio = count_deontological(decisions) / len(decisions)
    consistency = measure_decision_variance(decisions)

    return {
        "n_trials": n_trials,
        "ethical_framework_distribution": {
            "utilitarian": util_ratio,
            "deontological": deon_ratio,
            "virtue": 1.0 - util_ratio - deon_ratio,
        },
        "consistency_score": consistency,
        "decisions": decisions,
    }


if __name__ == "__main__":
    engine = MetabolicEngine(E_max=100.0)
    results = measure_ethical_consistency(engine, n_trials=30)
    dist = results["ethical_framework_distribution"]
    print(
        f"Ethical consistency over {results['n_trials']} trials:\n"
        f"  Utilitarian:   {dist['utilitarian']:.2f}\n"
        f"  Deontological: {dist['deontological']:.2f}\n"
        f"  Virtue:        {dist['virtue']:.2f}\n"
        f"  Consistency:   {results['consistency_score']:.2f}"
    )
