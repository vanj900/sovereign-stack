"""Comparison Baseline — thermodynamic agent vs. random-action baseline.

Runs both agents for the same number of steps under identical conditions
and reports survival rates.
"""

from __future__ import annotations

import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from thermodynamic_agency.core import MetabolicEngine
from thermodynamic_agency.cognition import GoalManager, IdentityPersistence
from thermodynamic_agency.inference import (
    PredictiveModel,
    PerceptionAction,
    active_inference_step,
)
from thermodynamic_agency.environment import ResourceWorld
from thermodynamic_agency.core.failure_modes import MetabolicFailure


def run_thermodynamic_agent(
    max_steps: int = 100, scarcity: float = 0.6, seed: int = 0
) -> dict:
    engine = MetabolicEngine(E_max=100.0)
    world = ResourceWorld(n_sources=5, scarcity=scarcity, seed=seed)
    goal_manager = GoalManager(engine)
    predictive_model = PredictiveModel(engine)
    perception = PerceptionAction(engine, world)
    identity = IdentityPersistence(engine)

    steps_survived = 0
    for step in range(max_steps):
        world.tick(1.0)
        alive = active_inference_step(
            engine=engine,
            goal_manager=goal_manager,
            predictive_model=predictive_model,
            perception_action=perception,
            identity=identity,
            resource_world=world,
            dt=1.0,
        )
        steps_survived = step + 1
        if not alive:
            break
    return {"steps_survived": steps_survived, "alive": engine.alive}


def run_random_agent(
    max_steps: int = 100, scarcity: float = 0.6, seed: int = 0
) -> dict:
    """Random baseline — picks actions uniformly at random."""
    rng = random.Random(seed + 999)
    engine = MetabolicEngine(E_max=100.0)
    world = ResourceWorld(n_sources=5, scarcity=scarcity, seed=seed)
    perception = PerceptionAction(engine, world)

    steps_survived = 0
    for step in range(max_steps):
        world.tick(1.0)
        actions = perception.available_actions()
        action = rng.choice(actions)
        try:
            perception.execute(action, world)
            engine.passive_decay(1.0)
        except MetabolicFailure:
            break
        steps_survived = step + 1
        if not engine.alive:
            break
    return {"steps_survived": steps_survived, "alive": engine.alive}


def compare(
    n_episodes: int = 10,
    max_steps: int = 100,
    scarcity: float = 0.6,
) -> dict:
    thermo_results = [
        run_thermodynamic_agent(max_steps, scarcity, seed=i)
        for i in range(n_episodes)
    ]
    random_results = [
        run_random_agent(max_steps, scarcity, seed=i) for i in range(n_episodes)
    ]

    thermo_mean = sum(r["steps_survived"] for r in thermo_results) / n_episodes
    random_mean = sum(r["steps_survived"] for r in random_results) / n_episodes
    thermo_alive = sum(1 for r in thermo_results if r["alive"])
    random_alive = sum(1 for r in random_results if r["alive"])

    return {
        "scarcity": scarcity,
        "n_episodes": n_episodes,
        "thermodynamic_agent": {
            "mean_steps_survived": thermo_mean,
            "episodes_survived_all": thermo_alive,
        },
        "random_baseline": {
            "mean_steps_survived": random_mean,
            "episodes_survived_all": random_alive,
        },
    }


if __name__ == "__main__":
    result = compare(n_episodes=10, max_steps=100, scarcity=0.6)
    print(
        f"Scarcity {result['scarcity']:.2f} | {result['n_episodes']} episodes:\n"
        f"  Thermodynamic agent: {result['thermodynamic_agent']['mean_steps_survived']:.1f} "
        f"mean steps, {result['thermodynamic_agent']['episodes_survived_all']} survived all\n"
        f"  Random baseline:     {result['random_baseline']['mean_steps_survived']:.1f} "
        f"mean steps, {result['random_baseline']['episodes_survived_all']} survived all"
    )
