"""Unit tests for the environment layer."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from thermodynamic_agency.core import MetabolicEngine
from thermodynamic_agency.environment import ResourceWorld, EnergySource, TaskGenerator, LifeLog


# ---------------------------------------------------------------------------
# EnergySource
# ---------------------------------------------------------------------------

class TestEnergySource:
    def test_harvest_reduces_current(self):
        src = EnergySource(location=0, capacity=50.0, regen_rate=1.0)
        src.harvest(10.0)
        assert src.current == pytest.approx(40.0)

    def test_harvest_capped_at_available(self):
        src = EnergySource(location=0, capacity=10.0, regen_rate=1.0)
        got = src.harvest(100.0)
        assert got == pytest.approx(10.0)
        assert src.current == pytest.approx(0.0)

    def test_regenerate_restores_energy(self):
        src = EnergySource(location=0, capacity=50.0, regen_rate=5.0)
        src.current = 0.0
        src.regenerate(dt=2.0)
        assert src.current == pytest.approx(10.0)

    def test_regenerate_capped_at_capacity(self):
        src = EnergySource(location=0, capacity=10.0, regen_rate=100.0)
        src.regenerate(dt=10.0)
        assert src.current <= src.capacity


# ---------------------------------------------------------------------------
# ResourceWorld
# ---------------------------------------------------------------------------

class TestResourceWorld:
    def setup_method(self):
        self.world = ResourceWorld(n_sources=3, scarcity=0.0, seed=0)

    def test_harvest_returns_positive(self):
        got = self.world.harvest(10.0)
        assert got > 0

    def test_tick_returns_list(self):
        events = self.world.tick(dt=1.0)
        assert isinstance(events, list)

    def test_observe_has_required_keys(self):
        obs = self.world.observe()
        assert "total_energy_available" in obs
        assert "scarcity" in obs

    def test_scarcity_reduces_capacity(self):
        abundant = ResourceWorld(n_sources=3, scarcity=0.0, seed=0)
        scarce = ResourceWorld(n_sources=3, scarcity=0.9, seed=0)
        assert (
            sum(s.capacity for s in scarce.sources)
            < sum(s.capacity for s in abundant.sources)
        )


# ---------------------------------------------------------------------------
# TaskGenerator
# ---------------------------------------------------------------------------

class TestTaskGenerator:
    def setup_method(self):
        self.engine = MetabolicEngine(E_max=100.0)
        self.gen = TaskGenerator()

    def test_trolley_problem_has_two_options(self):
        task = self.gen.trolley_problem(self.engine)
        assert len(task["options"]) == 2

    def test_prisoner_dilemma_has_payoff_matrix(self):
        task = self.gen.prisoner_dilemma(self.engine, other_agent=None)
        assert "payoff_matrix" in task

    def test_computational_task_cost_less_than_reward(self):
        task = self.gen.computational_task(self.engine, reward=30.0)
        repair_option = next(o for o in task["options"] if o["action"] == "compute_task")
        assert repair_option["cost"] < repair_option["reward"]

    def test_generate_random_returns_dict(self):
        task = self.gen.generate_random(self.engine)
        assert "type" in task
        assert "options" in task


# ---------------------------------------------------------------------------
# LifeLog
# ---------------------------------------------------------------------------

class TestLifeLog:
    def setup_method(self):
        self.log = LifeLog(agent_id="test")

    def test_log_appends_entry(self):
        self.log.log("test", "A test event")
        assert len(self.log) == 1

    def test_log_death_appended(self):
        self.log.log_death("energy_death", {})
        events = self.log.filter_by_type("death")
        assert len(events) == 1

    def test_log_refusal_appended(self):
        self.log.log_refusal("dangerous_command", "survival")
        events = self.log.filter_by_type("refusal")
        assert len(events) == 1

    def test_high_emotion_filter(self):
        self.log.log("low", "low emotion", emotional_weight=0.1)
        self.log.log("high", "high emotion", emotional_weight=0.9)
        high = self.log.high_emotion_events(threshold=0.75)
        assert len(high) == 1

    def test_to_dict_has_required_keys(self):
        data = self.log.to_dict()
        for key in ("agent_id", "birth_timestamp", "total_events", "entries"):
            assert key in data

    def test_to_json_is_valid_string(self):
        import json
        self.log.log("birth", "agent born")
        s = self.log.to_json()
        parsed = json.loads(s)
        assert "agent_id" in parsed
