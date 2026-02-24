"""
Tests for Trauma Model components
"""

import numpy as np
import pytest
from precisionlocked.trauma_model import (
    TraumaAttractor,
    AllostaticLoad,
    TraumaSimulator
)


class TestTraumaAttractor:
    """Tests for trauma attractor basin model."""
    
    def test_basin_depth(self):
        """Test attractor basin depth calculation."""
        attractor = TraumaAttractor(
            trauma_prior_mean=-1.0,
            trauma_prior_precision=100.0
        )
        
        # At the trauma prior, depth should be minimal
        depth_at_prior = attractor.basin_depth(
            np.array([-1.0]),
            trauma_state=True
        )
        
        # Away from prior, depth should be higher
        depth_away = attractor.basin_depth(
            np.array([0.5]),
            trauma_state=True
        )
        
        assert depth_away > depth_at_prior
    
    def test_escape_probability(self):
        """Test escape probability calculation."""
        attractor = TraumaAttractor()
        
        # High temperature (high uncertainty) -> higher escape probability
        prob_high_temp = attractor.escape_probability(
            sensory_evidence=np.array([1.0]),
            current_belief=np.array([-1.0]),
            temperature=10.0
        )
        
        # Low temperature (low uncertainty) -> lower escape probability
        prob_low_temp = attractor.escape_probability(
            sensory_evidence=np.array([1.0]),
            current_belief=np.array([-1.0]),
            temperature=0.1
        )
        
        assert 0 <= prob_high_temp <= 1
        assert 0 <= prob_low_temp <= 1
    
    def test_is_trapped(self):
        """Test trapped state detection."""
        attractor = TraumaAttractor()
        
        # High prior precision vs low sensory -> trapped
        assert attractor.is_trapped(
            pi_prior=100.0,
            pi_sensory=1.0,
            threshold=10.0
        )
        
        # Balanced precision -> not trapped
        assert not attractor.is_trapped(
            pi_prior=1.0,
            pi_sensory=10.0,
            threshold=10.0
        )


class TestAllostaticLoad:
    """Tests for allostatic load model."""
    
    def test_prediction_error_magnitude(self):
        """Test prediction error calculation."""
        allostatic = AllostaticLoad()
        
        y = np.array([1.0])
        mu = np.array([-1.0])
        
        mag = allostatic.prediction_error_magnitude(y, mu)
        
        assert mag == pytest.approx(2.0)
    
    def test_suppression_cost(self):
        """Test metabolic cost of error suppression."""
        allostatic = AllostaticLoad(
            base_metabolic_rate=1.0,
            suppression_cost_factor=2.0
        )
        
        # Higher error magnitude -> higher cost
        cost_high = allostatic.suppression_cost(
            epsilon_magnitude=2.0,
            pi_prior=100.0
        )
        
        cost_low = allostatic.suppression_cost(
            epsilon_magnitude=0.5,
            pi_prior=100.0
        )
        
        assert cost_high > cost_low
        
        # Higher precision -> higher cost
        cost_high_precision = allostatic.suppression_cost(
            epsilon_magnitude=2.0,
            pi_prior=100.0
        )
        
        cost_low_precision = allostatic.suppression_cost(
            epsilon_magnitude=2.0,
            pi_prior=1.0
        )
        
        assert cost_high_precision > cost_low_precision
    
    def test_cumulative_load(self):
        """Test cumulative load calculation."""
        allostatic = AllostaticLoad()
        
        error_history = [2.0, 2.0, 2.0, 2.0, 2.0]
        
        load = allostatic.cumulative_load(error_history, pi_prior=100.0)
        
        # Should be sum of individual costs
        assert load > 0
    
    def test_is_exhausted(self):
        """Test exhaustion detection."""
        allostatic = AllostaticLoad()
        
        assert allostatic.is_exhausted(
            cumulative_load=150.0,
            threshold=100.0
        )
        
        assert not allostatic.is_exhausted(
            cumulative_load=50.0,
            threshold=100.0
        )


class TestTraumaSimulator:
    """Tests for trauma dynamics simulator."""
    
    def test_initialization(self):
        """Test simulator initialization."""
        sim = TraumaSimulator(
            n_features=2,
            trauma_precision=100.0
        )
        
        assert sim.n_features == 2
        assert sim.trauma_precision == 100.0
        assert len(sim.mu) == 2
    
    def test_simulate_timestep(self):
        """Test single timestep simulation."""
        sim = TraumaSimulator()
        
        error, load, trapped = sim.simulate_timestep()
        
        # All outputs should be valid
        assert error >= 0
        assert load >= 0
        assert isinstance(trapped, bool)
        
        # In trauma state, should be trapped
        assert trapped
    
    def test_run_simulation(self):
        """Test full simulation run."""
        sim = TraumaSimulator()
        
        results = sim.run_simulation(n_timesteps=10)
        
        # Check structure
        assert 'errors' in results
        assert 'loads' in results
        assert 'cumulative_load' in results
        assert 'trapped' in results
        
        # Check lengths
        assert len(results['errors']) == 10
        assert len(results['loads']) == 10
        assert len(results['cumulative_load']) == 10
        assert len(results['trapped']) == 10
        
        # All should be trapped in trauma state
        assert all(results['trapped'])
        
        # Cumulative load should increase
        assert results['cumulative_load'][-1] > results['cumulative_load'][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
