"""
Tests for Therapy Model components
"""

import numpy as np
import pytest
from precisionlocked.therapy_model import (
    BayesianAnnealing,
    NeuromodulationControl,
    ReconsolidationWindow,
    TherapeuticIntervention
)


class TestBayesianAnnealing:
    """Tests for Bayesian Annealing mechanism."""
    
    def test_initialization(self):
        """Test annealing initialization."""
        annealing = BayesianAnnealing(
            initial_prior_precision=100.0,
            target_prior_precision=1.0
        )
        
        assert annealing.pi_prior == 100.0
        assert annealing.pi_prior_target == 1.0
    
    def test_annealing_schedule_linear(self):
        """Test linear annealing schedule."""
        annealing = BayesianAnnealing(
            initial_prior_precision=100.0,
            target_prior_precision=1.0
        )
        
        # At t=0, should be at initial
        pi_prior, pi_sensory = annealing.annealing_schedule(
            t=0, T=100, schedule_type="linear"
        )
        assert pi_prior == pytest.approx(100.0, abs=1.0)
        
        # At t=T, should be at target
        pi_prior, pi_sensory = annealing.annealing_schedule(
            t=100, T=100, schedule_type="linear"
        )
        assert pi_prior == pytest.approx(1.0, abs=1.0)
    
    def test_annealing_schedule_exponential(self):
        """Test exponential annealing schedule."""
        annealing = BayesianAnnealing()
        
        pi_prior_start, _ = annealing.annealing_schedule(
            t=0, T=100, schedule_type="exponential"
        )
        
        pi_prior_end, _ = annealing.annealing_schedule(
            t=100, T=100, schedule_type="exponential"
        )
        
        # Prior precision should decrease
        assert pi_prior_start > pi_prior_end
    
    def test_is_complete(self):
        """Test completion detection."""
        annealing = BayesianAnnealing(
            initial_prior_precision=100.0,
            target_prior_precision=1.0
        )
        
        # Initially not complete
        assert not annealing.is_complete(tolerance=0.1)
        
        # Manually set to target
        annealing.pi_prior = 1.0
        annealing.pi_sensory = 10.0
        
        # Should be complete
        assert annealing.is_complete(tolerance=1.0)


class TestNeuromodulationControl:
    """Tests for neuromodulatory control."""
    
    def test_noradrenaline_signal(self):
        """Test NE signal calculation."""
        # Large error -> large NE release
        ne_high = NeuromodulationControl.noradrenaline_signal(
            prediction_error=5.0,
            baseline=0.1,
            gain=1.0
        )
        
        # Small error -> small NE release
        ne_low = NeuromodulationControl.noradrenaline_signal(
            prediction_error=0.1,
            baseline=0.1,
            gain=1.0
        )
        
        assert ne_high > ne_low
    
    def test_acetylcholine_signal(self):
        """Test ACh signal calculation."""
        ach = NeuromodulationControl.acetylcholine_signal(
            precision_sensory=10.0,
            context_uncertainty=0.5
        )
        
        # ACh should reflect sensory precision
        assert ach > 0
    
    def test_oxytocin_modulation(self):
        """Test oxytocin effect on threat priors."""
        initial_threat = 100.0
        
        # In therapeutic context, oxytocin reduces threat precision
        modulated = NeuromodulationControl.oxytocin_modulation(
            social_threat_prior=initial_threat,
            therapeutic_context=True
        )
        
        assert modulated < initial_threat
        
        # Outside therapeutic context, no modulation
        not_modulated = NeuromodulationControl.oxytocin_modulation(
            social_threat_prior=initial_threat,
            therapeutic_context=False
        )
        
        assert not_modulated == initial_threat


class TestReconsolidationWindow:
    """Tests for reconsolidation window."""
    
    def test_activation(self):
        """Test window activation."""
        window = ReconsolidationWindow(
            window_duration=360,
            activation_threshold=0.5
        )
        
        # Strong cue should activate
        assert window.activate(cue_strength=0.8, current_time=0)
        assert window.is_open
        
        # Weak cue should not activate
        window2 = ReconsolidationWindow(activation_threshold=0.5)
        assert not window2.activate(cue_strength=0.3, current_time=0)
        assert not window2.is_open
    
    def test_check_violation(self):
        """Test prediction error violation."""
        window = ReconsolidationWindow()
        
        # Large mismatch -> violation
        assert window.check_violation(
            expected=np.array([-1.0]),
            observed=np.array([1.0]),
            violation_threshold=0.5
        )
        
        # Small mismatch -> no violation
        assert not window.check_violation(
            expected=np.array([1.0]),
            observed=np.array([1.1]),
            violation_threshold=0.5
        )
    
    def test_window_expiration(self):
        """Test window expiration."""
        window = ReconsolidationWindow(window_duration=10)
        
        window.activate(cue_strength=1.0, current_time=0)
        
        # Within window
        assert window.update(current_time=5, allow_update=True)
        
        # After expiration
        assert not window.update(current_time=15, allow_update=True)
        assert not window.is_open


class TestTherapeuticIntervention:
    """Tests for complete therapeutic intervention."""
    
    def test_initialization(self):
        """Test intervention initialization."""
        intervention = TherapeuticIntervention(
            n_features=2,
            trauma_precision=100.0
        )
        
        assert intervention.n_features == 2
        assert len(intervention.agent.mu) == 2
    
    def test_run_session(self):
        """Test therapeutic session."""
        intervention = TherapeuticIntervention()
        
        history = intervention.run_session(
            duration=50,
            schedule_type="exponential",
            safety_scaffold=True
        )
        
        # Check history structure
        assert 'mu' in history
        assert 'pi_prior' in history
        assert 'pi_sensory' in history
        assert 'free_energy' in history
        
        # Check lengths
        assert len(history['mu']) == 50
        
        # Prior precision should decrease
        assert history['pi_prior'][-1] < history['pi_prior'][0]
        
        # Sensory precision should increase
        assert history['pi_sensory'][-1] > history['pi_sensory'][0]
    
    def test_assess_outcome(self):
        """Test outcome assessment."""
        intervention = TherapeuticIntervention()
        
        # Run a session
        intervention.run_session(duration=50, safety_scaffold=True)
        
        # Assess outcome
        outcome = intervention.assess_outcome()
        
        # Check outcome structure
        assert 'final_belief' in outcome
        assert 'final_free_energy' in outcome
        assert 'convergence_to_safety' in outcome
        assert 'total_belief_shift' in outcome
        
        # Belief should have shifted
        assert outcome['total_belief_shift'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
