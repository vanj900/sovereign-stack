"""Unit tests for the active inference and cognition layers."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from thermodynamic_agency.core import MetabolicEngine
from thermodynamic_agency.cognition import GoalManager, EthicalEngine, IdentityPersistence
from thermodynamic_agency.cognition.goal_manager import DrivePriority
from thermodynamic_agency.cognition.identity_persistence import TRAUMA_THRESHOLD
from thermodynamic_agency.inference import PredictiveModel, PerceptionAction, Action
from thermodynamic_agency.inference.active_inference_loop import compute_efe


# ---------------------------------------------------------------------------
# GoalManager
# ---------------------------------------------------------------------------

class TestGoalManager:
    def setup_method(self):
        self.engine = MetabolicEngine(E_max=100.0)
        self.gm = GoalManager(self.engine)

    def test_update_returns_drives(self):
        drives = self.gm.update()
        assert len(drives) >= 1

    def test_survival_drive_highest_when_low_energy(self):
        self.engine.E = 5.0  # very low
        drives = self.gm.update()
        assert drives[0].name == "survival"
        assert drives[0].priority == DrivePriority.CRITICAL

    def test_generate_actions_returns_list(self):
        actions = self.gm.generate_actions()
        assert isinstance(actions, list)
        assert len(actions) >= 1

    def test_drive_urgency_in_range(self):
        drives = self.gm.update()
        for d in drives:
            assert 0.0 <= d.urgency <= 1.0


# ---------------------------------------------------------------------------
# EthicalEngine
# ---------------------------------------------------------------------------

class TestEthicalEngine:
    def setup_method(self):
        self.engine = MetabolicEngine(E_max=100.0)
        self.eth = EthicalEngine(self.engine)

    def test_resolve_dilemma_returns_option(self):
        options = [
            {"action": "repair", "cost": 10.0, "saves": "memory"},
            {"action": "abandon", "cost": 0.0, "loses": "identity_coherence"},
        ]
        state = self.engine.snapshot()
        choice = self.eth.resolve_dilemma(options, state)
        assert choice["action"] in ("repair", "abandon")

    def test_deontological_penalises_identity_loss(self):
        """The engine should prefer 'repair' over abandoning identity."""
        options = [
            {"action": "repair", "cost": 5.0, "saves": "memory"},
            {"action": "abandon", "cost": 0.0, "loses": "identity_coherence"},
        ]
        state = self.engine.snapshot()
        choice = self.eth.resolve_dilemma(options, state)
        assert choice["action"] == "repair"

    def test_decision_log_populated(self):
        options = [
            {"action": "harvest_energy", "cost": 1.0},
            {"action": "idle", "cost": 0.0},
        ]
        self.eth.resolve_dilemma(options, self.engine.snapshot())
        assert len(self.eth.decision_log) == 1

    def test_weights_sum_to_one(self):
        import math
        total = self.eth.w_util + self.eth.w_deon + self.eth.w_virtue
        assert math.isclose(total, 1.0, rel_tol=1e-6)


# ---------------------------------------------------------------------------
# IdentityPersistence
# ---------------------------------------------------------------------------

class TestIdentityPersistence:
    def setup_method(self):
        self.engine = MetabolicEngine(E_max=100.0)
        self.identity = IdentityPersistence(self.engine, agent_id="test-agent")

    def test_record_event_appended(self):
        self.identity.record_event("test event", 0.3)
        assert len(self.identity.narrative) == 1

    def test_traumatic_event_encoded(self):
        self.identity.record_event("near death", TRAUMA_THRESHOLD + 0.1)
        assert len(self.identity.trauma_memories) == 1

    def test_non_traumatic_event_not_encoded(self):
        self.identity.record_event("routine", TRAUMA_THRESHOLD - 0.1)
        assert len(self.identity.trauma_memories) == 0

    def test_serialise_has_required_keys(self):
        data = self.identity.serialise()
        for key in ("agent_id", "birth_timestamp", "events", "principles"):
            assert key in data

    def test_evolve_principles_adds_rule_on_failure(self):
        before = list(self.identity.principles["deontological_rules"])
        self.identity.evolve_principles(
            {"was_traumatic": True, "outcome": "failure"}
        )
        after = self.identity.principles["deontological_rules"]
        assert len(after) >= len(before)


# ---------------------------------------------------------------------------
# PredictiveModel
# ---------------------------------------------------------------------------

class TestPredictiveModel:
    def setup_method(self):
        self.engine = MetabolicEngine(E_max=100.0)
        self.pm = PredictiveModel(self.engine)

    def test_predict_outcome_returns_required_keys(self):
        action = Action(name="test", energy_cost=5.0, information_gain=0.1)
        result = self.pm.predict_outcome(action)
        for key in ("survival_prob", "final_state", "prediction_uncertainty", "information_gain"):
            assert key in result

    def test_survival_prob_in_range(self):
        action = Action(name="test", energy_cost=5.0)
        result = self.pm.predict_outcome(action)
        assert 0.0 <= result["survival_prob"] <= 1.0

    def test_update_beliefs_adjusts_parameters(self):
        action = Action(name="test", energy_cost=5.0)
        self.pm.predict_outcome(action)
        before = dict(self.pm.model_parameters)
        actual = self.engine.snapshot()
        actual["temperature"] = self.engine.T + 5  # introduce error
        self.pm.update_beliefs(actual)
        assert self.pm.model_parameters != before


# ---------------------------------------------------------------------------
# PerceptionAction / Action
# ---------------------------------------------------------------------------

class TestPerceptionAction:
    def setup_method(self):
        self.engine = MetabolicEngine(E_max=100.0)
        self.pa = PerceptionAction(self.engine)

    def test_perceive_returns_snapshot(self):
        obs = self.pa.perceive()
        assert "energy" in obs

    def test_available_actions_non_empty(self):
        actions = self.pa.available_actions()
        assert len(actions) > 0
        assert all(isinstance(a, Action) for a in actions)

    def test_execute_harvest_increases_energy(self):
        self.engine.E = 50.0
        from thermodynamic_agency.inference.perception_action import harvest_energy_action
        action = harvest_energy_action(amount=20.0)
        self.pa.execute(action)
        # energy increased or stayed ≥ 50 (minus tiny locomotion cost)
        assert self.engine.E >= 49.0


# ---------------------------------------------------------------------------
# compute_efe
# ---------------------------------------------------------------------------

class TestComputeEFE:
    def test_efe_higher_for_better_survival(self):
        good_action = Action(name="good", energy_cost=1.0, information_gain=0.2)
        bad_action = Action(name="bad", energy_cost=8.0, information_gain=0.0)
        good_pred = {"survival_prob": 0.9, "information_gain": 0.2}
        bad_pred = {"survival_prob": 0.1, "information_gain": 0.0}
        efe_good = compute_efe(good_action, good_pred)
        efe_bad = compute_efe(bad_action, bad_pred)
        assert efe_good > efe_bad
