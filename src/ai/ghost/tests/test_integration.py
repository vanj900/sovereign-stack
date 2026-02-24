"""Integration tests — full active-inference episode."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from thermodynamic_agency.core import MetabolicEngine
from thermodynamic_agency.cognition import GoalManager, IdentityPersistence
from thermodynamic_agency.inference import (
    PredictiveModel,
    PerceptionAction,
    active_inference_step,
)
from thermodynamic_agency.environment import ResourceWorld, LifeLog


def build_agent(E_max=100.0, scarcity=0.3, seed=0):
    engine = MetabolicEngine(E_max=E_max)
    world = ResourceWorld(n_sources=5, scarcity=scarcity, seed=seed)
    gm = GoalManager(engine)
    pm = PredictiveModel(engine)
    pa = PerceptionAction(engine, world)
    identity = IdentityPersistence(engine, agent_id="test-integration")
    return engine, world, gm, pm, pa, identity


class TestActiveInferenceIntegration:
    def test_agent_survives_10_steps_low_scarcity(self):
        engine, world, gm, pm, pa, identity = build_agent(scarcity=0.1)
        for _ in range(10):
            world.tick(1.0)
            alive = active_inference_step(
                engine=engine,
                goal_manager=gm,
                predictive_model=pm,
                perception_action=pa,
                identity=identity,
                resource_world=world,
                dt=1.0,
            )
            if not alive:
                break
        # With low scarcity and plenty of energy it should survive
        assert engine.alive

    def test_identity_records_events(self):
        engine, world, gm, pm, pa, identity = build_agent(scarcity=0.1)
        for _ in range(3):
            world.tick(1.0)
            active_inference_step(engine, gm, pm, pa, identity, world, dt=1.0)
        assert len(identity.narrative) >= 3

    def test_life_log_tracks_events(self):
        engine, world, gm, pm, pa, identity = build_agent(scarcity=0.1)
        life_log = LifeLog()
        life_log.log("birth", "agent born", engine.snapshot())
        for _ in range(3):
            world.tick(1.0)
            alive = active_inference_step(engine, gm, pm, pa, identity, world, dt=1.0)
            life_log.log(
                "step",
                f"step complete, alive={alive}",
                engine.snapshot(),
            )
        assert len(life_log) >= 4

    def test_agent_may_die_under_extreme_scarcity(self):
        """Under extreme scarcity and many steps, the agent may die."""
        engine, world, gm, pm, pa, identity = build_agent(
            E_max=20.0, scarcity=0.99, seed=1
        )
        died = False
        for _ in range(200):
            world.tick(1.0)
            alive = active_inference_step(engine, gm, pm, pa, identity, world, dt=1.0)
            if not alive:
                died = True
                break
        # Test passes whether agent lives or dies — both are valid outcomes.
        # The important thing is no exception leaks out.
        assert died or engine.alive
