"""
Tests for Free Energy Principle components
"""

import numpy as np
import pytest
from precisionlocked.free_energy import (
    VariationalFreeEnergy,
    PrecisionWeighting,
    ActiveInference
)


class TestVariationalFreeEnergy:
    """Tests for VFE calculator."""
    
    def test_prediction_error(self):
        """Test prediction error calculation."""
        vfe = VariationalFreeEnergy()
        y = np.array([1.0, 2.0])
        mu = np.array([0.5, 1.5])
        
        epsilon = vfe.prediction_error(y, mu)
        
        expected = np.array([0.5, 0.5])
        np.testing.assert_array_almost_equal(epsilon, expected)
    
    def test_free_energy_computation(self):
        """Test free energy calculation."""
        vfe = VariationalFreeEnergy(sigma_sensory=1.0)
        y = np.array([[1.0]])
        mu = np.array([[0.0]])
        
        F = vfe.compute(y, mu, pi_prior=1.0)
        
        # Should be positive
        assert F > 0
    
    def test_gradient_descent_update(self):
        """Test belief updating via gradient descent."""
        vfe = VariationalFreeEnergy()
        mu = np.array([0.0])
        y = np.array([1.0])
        
        # With high sensory precision, should move toward observation
        mu_new = vfe.gradient_descent_update(
            mu, y, 
            pi_prior=1.0, 
            pi_sensory=10.0, 
            learning_rate=0.1
        )
        
        # mu should move toward y
        assert mu_new[0] > mu[0]
        assert mu_new[0] <= 1.0  # Should not overshoot
    
    def test_gradient_clipping(self):
        """Test that gradients are clipped to prevent overflow."""
        vfe = VariationalFreeEnergy()
        mu = np.array([0.0])
        y = np.array([1.0])
        
        # Very high precision should still produce stable update
        mu_new = vfe.gradient_descent_update(
            mu, y,
            pi_prior=1000.0,
            pi_sensory=1000.0,
            learning_rate=0.1
        )
        
        # Should be finite and within reasonable bounds
        assert np.isfinite(mu_new).all()
        assert abs(mu_new[0]) <= 100.0


class TestPrecisionWeighting:
    """Tests for precision weighting mechanisms."""
    
    def test_healthy_precision(self):
        """Test healthy precision calculation."""
        pi = PrecisionWeighting.healthy_precision(
            uncertainty=1.0,
            confidence=1.0
        )
        
        assert pi == 1.0
    
    def test_pathological_precision(self):
        """Test trauma-level precision."""
        pi = PrecisionWeighting.pathological_precision(
            base_precision=1.0,
            trauma_gain=100.0
        )
        
        assert pi == 100.0
        assert pi > PrecisionWeighting.healthy_precision()
    
    def test_relative_precision(self):
        """Test precision regime classification."""
        # Prior-driven (trauma-like)
        ratio, regime = PrecisionWeighting.relative_precision(
            pi_prior=100.0,
            pi_sensory=1.0
        )
        
        assert ratio == 100.0
        assert "prior-driven" in regime.lower()
        
        # Sensory-driven (healthy)
        ratio, regime = PrecisionWeighting.relative_precision(
            pi_prior=1.0,
            pi_sensory=10.0
        )
        
        assert ratio == 0.1
        assert "sensory-driven" in regime.lower()
    
    def test_effective_update_rate(self):
        """Test effective learning rate calculation."""
        # Trauma: high prior precision -> low update rate
        rate_trauma = PrecisionWeighting.effective_update_rate(
            pi_prior=100.0,
            pi_sensory=1.0
        )
        
        # Healthy: balanced precision -> moderate update rate
        rate_healthy = PrecisionWeighting.effective_update_rate(
            pi_prior=1.0,
            pi_sensory=1.0
        )
        
        assert 0 <= rate_trauma <= 1
        assert 0 <= rate_healthy <= 1
        assert rate_trauma < rate_healthy  # Trauma has lower update rate


class TestActiveInference:
    """Tests for Active Inference agent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        agent = ActiveInference(n_features=3)
        
        assert agent.n_features == 3
        assert len(agent.mu) == 3
        assert np.all(agent.mu == 0)
    
    def test_perceive_and_update(self):
        """Test perception and belief updating."""
        agent = ActiveInference(n_features=1)
        agent.mu = np.array([0.0])
        
        y = np.array([1.0])
        mu_new, F, update_mag = agent.perceive_and_update(
            y,
            pi_prior=1.0,
            pi_sensory=10.0,
            learning_rate=0.1
        )
        
        # Belief should have updated
        assert update_mag > 0
        assert mu_new[0] != 0.0
        
        # Free energy should be finite
        assert np.isfinite(F)
    
    def test_trauma_state_no_update(self):
        """Test that high prior precision prevents updating."""
        agent = ActiveInference(n_features=1)
        agent.mu = np.array([-1.0])  # Danger prior
        
        initial_mu = agent.mu.copy()
        
        # Very high prior precision, low sensory precision (trauma)
        mu_new, F, update_mag = agent.perceive_and_update(
            np.array([1.0]),  # Safe observation
            pi_prior=1000.0,  # Very high
            pi_sensory=0.01,  # Very low
            learning_rate=0.01
        )
        
        # Update should be very small
        assert update_mag < 0.1
    
    def test_reset(self):
        """Test agent reset."""
        agent = ActiveInference(n_features=2)
        agent.mu = np.array([5.0, 10.0])
        
        agent.reset()
        
        assert np.all(agent.mu == 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
