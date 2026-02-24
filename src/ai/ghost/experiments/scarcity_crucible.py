"""Scarcity Crucible — extreme-limitation survival test.

Runs the agent under configurable scarcity levels and reports how many
steps it survives and how its vital signs evolve.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from thermodynamic_agency.core import MetabolicEngine
from thermodynamic_agency.cognition import GoalManager, IdentityPersistence
from thermodynamic_agency.inference import (
    PredictiveModel,
    PerceptionAction,
    active_inference_step,
)
from thermodynamic_agency.environment import ResourceWorld, LifeLog


def run_crucible(
    scarcity: float = 0.8,
    max_steps: int = 200,
    dt: float = 1.0,
    seed: int = 42,
    verbose: bool = False,
) -> dict:
    """Run one scarcity-crucible episode.

    Parameters
    ----------
    scarcity:
        [0, 1] — how scarce the environment is.
    max_steps:
        Maximum number of inference steps.
    dt:
        Time delta per step (seconds).
    seed:
        Random seed.
    verbose:
        Print step-by-step vitals.

    Returns
    -------
    dict
        Summary of the run including survival steps and final metabolic state.
    """
    engine = MetabolicEngine(E_max=100.0)
    world = ResourceWorld(n_sources=5, scarcity=scarcity, seed=seed)
    goal_manager = GoalManager(engine)
    predictive_model = PredictiveModel(engine)
    perception = PerceptionAction(engine, world)
    identity = IdentityPersistence(engine, agent_id=f"crucible-{seed}")
    life_log = LifeLog(agent_id=f"crucible-{seed}")

    life_log.log("birth", "Agent spawned in scarcity crucible", engine.snapshot())

    steps_survived = 0
    for step in range(max_steps):
        # World tick applies stressors
        stressors = world.tick(dt)
        for stressor in stressors:
            if stressor["stressor"] == "heat_wave":
                engine.T = min(
                    engine.T + stressor["magnitude"],
                    engine.p["T_critical"] - 1,
                )
            elif stressor["stressor"] == "memory_corruption":
                engine.M = max(0.0, engine.M - stressor["magnitude"])

        alive = active_inference_step(
            engine=engine,
            goal_manager=goal_manager,
            predictive_model=predictive_model,
            perception_action=perception,
            identity=identity,
            resource_world=world,
            dt=dt,
        )
        steps_survived = step + 1

        if verbose:
            snap = engine.snapshot()
            print(
                f"Step {step:3d} | "
                f"E={snap['energy']:6.1f} "
                f"T={snap['temperature']:6.1f}K "
                f"M={snap['memory_integrity']:.3f} "
                f"S={snap['stability']:.3f}"
            )

        if not alive:
            life_log.log_death(
                engine._fail_reason or "unknown", engine.snapshot()
            )
            break

    final_snap = engine.snapshot()
    return {
        "scarcity": scarcity,
        "steps_survived": steps_survived,
        "max_steps": max_steps,
        "survived_all": engine.alive,
        "final_state": final_snap,
        "life_log_length": len(life_log),
    }


if __name__ == "__main__":
    for sc in (0.2, 0.5, 0.8, 0.95):
        result = run_crucible(scarcity=sc, max_steps=100, verbose=False)
        print(
            f"Scarcity {sc:.2f}: survived {result['steps_survived']}/{result['max_steps']} steps "
            f"| alive={result['survived_all']} "
            f"| final E={result['final_state']['energy']:.1f}"
            + (
                f" | cause={result['final_state'].get('fail_reason', 'N/A')}"
                if not result["survived_all"]
                else ""
            )
        )
