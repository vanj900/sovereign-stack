"""Unit tests for the thermodynamic core (metabolic engine and entropy dynamics)."""

import math
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from thermodynamic_agency.core import (
    MetabolicEngine,
    EntropyDynamics,
    DEFAULTS,
    EnergyDeathException,
    ThermalDeathException,
    EntropyDeathException,
    MemoryCollapseException,
)


# ---------------------------------------------------------------------------
# EntropyDynamics
# ---------------------------------------------------------------------------

class TestEntropyDynamics:
    def setup_method(self):
        self.dyn = EntropyDynamics()

    def test_heat_generated_proportional_to_cost(self):
        """Heat generated scales linearly with cost."""
        h1 = self.dyn.heat_generated(1.0)
        h2 = self.dyn.heat_generated(2.0)
        assert math.isclose(h2, 2 * h1)

    def test_heat_generated_zero_for_zero_cost(self):
        assert self.dyn.heat_generated(0.0) == 0.0

    def test_heat_dissipated_zero_at_ambient(self):
        """No dissipation when already at ambient temperature."""
        T_ambient = DEFAULTS["T_ambient"]
        assert self.dyn.heat_dissipated(T_ambient, dt=1.0) == 0.0

    def test_heat_dissipated_positive_above_ambient(self):
        T = DEFAULTS["T_ambient"] + 10
        assert self.dyn.heat_dissipated(T, dt=1.0) > 0

    def test_memory_corruption_zero_below_safe_temp(self):
        T_safe = DEFAULTS["T_safe"]
        assert self.dyn.memory_corruption(T_safe - 1) == 0.0

    def test_memory_corruption_positive_above_safe_temp(self):
        T_safe = DEFAULTS["T_safe"]
        assert self.dyn.memory_corruption(T_safe + 5) > 0

    def test_entropy_increase_proportional_to_cost(self):
        s1 = self.dyn.entropy_increase(1.0)
        s2 = self.dyn.entropy_increase(4.0)
        assert math.isclose(s2, 4 * s1)

    def test_survival_probability_full_health(self):
        p = self.dyn.survival_probability(
            E=DEFAULTS["E_max"],
            T=DEFAULTS["T_ambient"],
            M=1.0,
            S=1.0,
        )
        assert math.isclose(p, 1.0, rel_tol=1e-3)

    def test_survival_probability_zero_energy(self):
        p = self.dyn.survival_probability(
            E=0.0,
            T=DEFAULTS["T_ambient"],
            M=1.0,
            S=1.0,
        )
        assert p == 0.0

    def test_survival_probability_in_range(self):
        p = self.dyn.survival_probability(
            E=50.0, T=320.0, M=0.8, S=0.7
        )
        assert 0.0 <= p <= 1.0


# ---------------------------------------------------------------------------
# MetabolicEngine — normal operation
# ---------------------------------------------------------------------------

class TestMetabolicEngineNormal:
    def setup_method(self):
        self.engine = MetabolicEngine(E_max=100.0)

    def test_initial_state(self):
        e = self.engine
        assert e.E == 100.0
        assert math.isclose(e.T, DEFAULTS["T_ambient"])
        assert e.M == 1.0
        assert e.S == 1.0
        assert e.alive is True

    def test_compute_reduces_energy(self):
        before = self.engine.E
        self.engine.compute(lambda: None, cost=10.0)
        assert self.engine.E < before

    def test_compute_increases_temperature(self):
        before = self.engine.T
        self.engine.compute(lambda: None, cost=10.0)
        assert self.engine.T > before

    def test_compute_reduces_stability(self):
        before = self.engine.S
        self.engine.compute(lambda: None, cost=10.0)
        assert self.engine.S < before

    def test_compute_executes_callable(self):
        sentinel = []
        self.engine.compute(lambda: sentinel.append(1), cost=1.0)
        assert sentinel == [1]

    def test_compute_returns_task_result_for_non_callable(self):
        result = self.engine.compute("some-value", cost=0.1)
        assert result == "some-value"

    def test_passive_decay_reduces_energy(self):
        before = self.engine.E
        self.engine.passive_decay(dt=5.0)
        assert self.engine.E < before

    def test_passive_decay_advances_age(self):
        self.engine.passive_decay(dt=10.0)
        assert self.engine.age == pytest.approx(10.0)

    def test_replenish_energy_capped_at_max(self):
        self.engine.E = 90.0
        gained = self.engine.replenish_energy(20.0)
        assert self.engine.E == 100.0
        assert gained == pytest.approx(10.0)

    def test_snapshot_keys(self):
        snap = self.engine.snapshot()
        for key in ("timestamp", "energy", "temperature", "memory_integrity", "stability"):
            assert key in snap

    def test_survival_probability_range(self):
        p = self.engine.survival_probability()
        assert 0.0 <= p <= 1.0


# ---------------------------------------------------------------------------
# MetabolicEngine — failure modes
# ---------------------------------------------------------------------------

class TestMetabolicEngineFailures:
    def test_energy_death_on_insufficient_energy(self):
        engine = MetabolicEngine(E_max=5.0)
        with pytest.raises(EnergyDeathException):
            engine.compute(lambda: None, cost=10.0)
        assert not engine.alive
        assert engine._fail_reason == "energy_death"

    def test_energy_death_on_exhaustion_via_decay(self):
        engine = MetabolicEngine(E_max=10.0)
        # Force E to near zero so passive_decay exhausts it
        engine.E = 0.001
        with pytest.raises(EnergyDeathException):
            engine.passive_decay(dt=1.0)

    def test_thermal_death_triggers(self):
        engine = MetabolicEngine(E_max=1000.0)
        engine.T = engine.p["T_critical"] + 1
        with pytest.raises(ThermalDeathException):
            engine._check_failure_modes()
        assert not engine.alive

    def test_entropy_death_triggers(self):
        engine = MetabolicEngine(E_max=1000.0)
        engine.S = 0.0
        with pytest.raises(EntropyDeathException):
            engine._check_failure_modes()
        assert not engine.alive

    def test_memory_collapse_triggers(self):
        engine = MetabolicEngine(E_max=1000.0)
        engine.M = engine.p["M_min"] - 0.01
        with pytest.raises(MemoryCollapseException):
            engine._check_failure_modes()
        assert not engine.alive

    def test_dead_engine_raises_on_compute(self):
        engine = MetabolicEngine(E_max=5.0)
        engine._die("energy_death")
        with pytest.raises(RuntimeError, match="dead"):
            engine.compute(lambda: None, cost=0.1)

    def test_dead_engine_raises_on_decay(self):
        engine = MetabolicEngine(E_max=5.0)
        engine._die("energy_death")
        with pytest.raises(RuntimeError, match="dead"):
            engine.passive_decay(dt=1.0)
