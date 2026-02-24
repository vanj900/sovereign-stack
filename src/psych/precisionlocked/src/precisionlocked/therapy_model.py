"""
Therapy Model: Bayesian Annealing

This module implements therapeutic intervention as controlled precision modulation
to facilitate belief updating within the reconsolidation window.
"""

import numpy as np
from typing import Tuple, Dict, Callable, Optional
from .free_energy import VariationalFreeEnergy, ActiveInference


class BayesianAnnealing:
    """
    Bayesian Annealing: Therapeutic intervention as precision modulation.
    
    Therapy is analogous to Simulated Annealing in optimization:
    - Introduce controlled uncertainty (lower Π_prior)
    - Increase sensory evidence gain (increase Π_sensory)
    - Allow system to escape local minimum (trauma attractor)
    
    Goal: Shift from "prior-driven" to "sensory-driven" regime.
    """
    
    def __init__(
        self,
        initial_prior_precision: float = 100.0,  # Trauma state
        target_prior_precision: float = 1.0,     # Healthy state
        initial_sensory_precision: float = 0.1,
        target_sensory_precision: float = 10.0
    ):
        """
        Initialize Bayesian Annealing process.
        
        Args:
            initial_prior_precision: Starting Π_prior (high in trauma)
            target_prior_precision: Target Π_prior (healthy level)
            initial_sensory_precision: Starting Π_sensory (low in trauma)
            target_sensory_precision: Target Π_sensory (elevated in therapy)
        """
        self.pi_prior_initial = initial_prior_precision
        self.pi_prior_target = target_prior_precision
        self.pi_sensory_initial = initial_sensory_precision
        self.pi_sensory_target = target_sensory_precision
        
        # Current precision values
        self.pi_prior = initial_prior_precision
        self.pi_sensory = initial_sensory_precision
    
    def annealing_schedule(
        self,
        t: int,
        T: int,
        schedule_type: str = "exponential"
    ) -> Tuple[float, float]:
        """
        Compute precision values according to annealing schedule.
        
        The "temperature" in annealing corresponds to uncertainty.
        As therapy progresses:
        - Π_prior decreases (prior becomes less certain)
        - Π_sensory increases (sensory evidence gains weight)
        
        Args:
            t: Current timestep
            T: Total duration of annealing
            schedule_type: Type of schedule ("linear", "exponential", "sigmoid")
            
        Returns:
            Tuple of (pi_prior, pi_sensory) at time t
        """
        # Normalized time (0 to 1)
        tau = t / max(T, 1)
        
        if schedule_type == "linear":
            alpha = tau
        elif schedule_type == "exponential":
            # Exponential decay for prior, exponential growth for sensory
            alpha = 1 - np.exp(-3 * tau)
        elif schedule_type == "sigmoid":
            # Smooth transition
            alpha = 1 / (1 + np.exp(-10 * (tau - 0.5)))
        else:
            alpha = tau
        
        # Interpolate precision values
        pi_prior = (
            self.pi_prior_initial * (1 - alpha) + 
            self.pi_prior_target * alpha
        )
        pi_sensory = (
            self.pi_sensory_initial * (1 - alpha) + 
            self.pi_sensory_target * alpha
        )
        
        return pi_prior, pi_sensory
    
    def update_precision(
        self,
        t: int,
        T: int,
        schedule_type: str = "exponential"
    ):
        """
        Update current precision values according to schedule.
        
        Args:
            t: Current timestep
            T: Total duration
            schedule_type: Annealing schedule type
        """
        self.pi_prior, self.pi_sensory = self.annealing_schedule(
            t, T, schedule_type
        )
    
    def is_complete(self, tolerance: float = 0.1) -> bool:
        """
        Check if annealing process is complete.
        
        Args:
            tolerance: Tolerance for reaching target precision
            
        Returns:
            True if current precision is close to target
        """
        prior_close = (
            abs(self.pi_prior - self.pi_prior_target) < tolerance
        )
        sensory_close = (
            abs(self.pi_sensory - self.pi_sensory_target) < tolerance
        )
        
        return prior_close and sensory_close


class NeuromodulationControl:
    """
    Neuromodulatory control unit for precision regulation.
    
    Maps the annealing schedule to specific neuromodulator dynamics:
    - Noradrenaline (NE): Signals unexpected uncertainty
    - Acetylcholine (ACh): Increases sensory prediction error gain
    - Dopamine (DA): Encodes precision of action policies
    - Oxytocin: Reduces precision of social threat priors
    """
    
    @staticmethod
    def noradrenaline_signal(
        prediction_error: float,
        baseline: float = 0.1,
        gain: float = 1.0
    ) -> float:
        """
        Model noradrenaline (NE) release.
        
        NE signals unexpected uncertainty - released phasically
        in response to large prediction errors.
        
        Args:
            prediction_error: Magnitude of prediction error
            baseline: Tonic NE level
            gain: Phasic response gain
            
        Returns:
            NE level
        """
        # Phasic release proportional to error
        phasic = gain * abs(prediction_error)
        total_ne = baseline + phasic
        
        return total_ne
    
    @staticmethod
    def acetylcholine_signal(
        precision_sensory: float,
        context_uncertainty: float = 0.5
    ) -> float:
        """
        Model acetylcholine (ACh) release.
        
        ACh increases the gain on sensory prediction errors.
        High ACh = high sensory precision.
        
        Args:
            precision_sensory: Target sensory precision
            context_uncertainty: Environmental uncertainty
            
        Returns:
            ACh level
        """
        # ACh tracks sensory precision, modulated by context
        ach = precision_sensory * (1 - context_uncertainty)
        
        return ach
    
    @staticmethod
    def oxytocin_modulation(
        social_threat_prior: float,
        therapeutic_context: bool = True
    ) -> float:
        """
        Model oxytocin effect on social threat priors.
        
        Oxytocin reduces precision of social threat priors,
        facilitating updating in safe social contexts.
        
        Args:
            social_threat_prior: Initial social threat precision
            therapeutic_context: Whether in therapeutic (safe) context
            
        Returns:
            Modulated precision
        """
        if therapeutic_context:
            # Oxytocin reduces threat prior precision
            reduction_factor = 0.5
            modulated = social_threat_prior * reduction_factor
        else:
            modulated = social_threat_prior
        
        return modulated


class ReconsolidationWindow:
    """
    Memory reconsolidation window constraint.
    
    Biological constraint: Memory updating requires:
    1. Retrieval (activation) of the memory
    2. Prediction error violation
    3. Time-limited window (~3-6 hours) for reconsolidation
    
    Outside this window, the memory re-stabilizes.
    """
    
    def __init__(
        self,
        window_duration: int = 360,  # minutes (6 hours)
        activation_threshold: float = 0.5
    ):
        """
        Initialize reconsolidation window.
        
        Args:
            window_duration: Duration of reconsolidation window (minutes)
            activation_threshold: Threshold for memory activation
        """
        self.window_duration = window_duration
        self.activation_threshold = activation_threshold
        
        self.is_open = False
        self.time_opened = 0
        self.time_elapsed = 0
    
    def activate(
        self,
        cue_strength: float,
        current_time: int = 0
    ) -> bool:
        """
        Activate (retrieve) the traumatic memory.
        
        Args:
            cue_strength: Strength of retrieval cue (0 to 1)
            current_time: Current time point
            
        Returns:
            True if memory is activated and window opens
        """
        if cue_strength > self.activation_threshold:
            self.is_open = True
            self.time_opened = current_time
            return True
        return False
    
    def check_violation(
        self,
        expected: np.ndarray,
        observed: np.ndarray,
        violation_threshold: float = 0.5
    ) -> bool:
        """
        Check for prediction error violation.
        
        Requirement: Safety in presence of threat cues.
        The observed outcome must violate the trauma prediction.
        
        Args:
            expected: Expected outcome (from trauma prior, e.g., danger)
            observed: Observed outcome (e.g., safety)
            violation_threshold: Minimum violation magnitude
            
        Returns:
            True if violation detected
        """
        error = np.linalg.norm(observed - expected)
        return error > violation_threshold
    
    def update(
        self,
        current_time: int,
        allow_update: bool = True
    ) -> bool:
        """
        Update reconsolidation window state.
        
        Args:
            current_time: Current time point
            allow_update: Whether updating is permitted
            
        Returns:
            True if window is still open and updating can occur
        """
        if not self.is_open:
            return False
        
        # Check if window has expired
        self.time_elapsed = current_time - self.time_opened
        
        if self.time_elapsed > self.window_duration:
            self.is_open = False
            return False
        
        return allow_update and self.is_open
    
    def close(self):
        """Manually close the reconsolidation window."""
        self.is_open = False


class TherapeuticIntervention:
    """
    Complete therapeutic intervention model.
    
    Integrates:
    1. Bayesian Annealing (precision modulation)
    2. Neuromodulation control
    3. Reconsolidation window constraint
    
    Safely guides the system from trauma attractor to healthy state.
    """
    
    def __init__(
        self,
        n_features: int = 1,
        trauma_precision: float = 100.0,
        safe_sensory_mean: float = 1.0
    ):
        """
        Initialize therapeutic intervention.
        
        Args:
            n_features: Dimensionality of state space
            trauma_precision: Initial (trauma) prior precision
            safe_sensory_mean: Mean of safe sensory input
        """
        self.n_features = n_features
        self.safe_sensory = np.full(n_features, safe_sensory_mean)
        
        # Components
        self.annealing = BayesianAnnealing(
            initial_prior_precision=trauma_precision
        )
        self.reconsolidation = ReconsolidationWindow()
        self.agent = ActiveInference(n_features)
        
        # Initialize agent with trauma prior
        self.agent.mu = np.full(n_features, -1.0)  # Danger
        
        # History
        self.history = {
            'mu': [],
            'pi_prior': [],
            'pi_sensory': [],
            'free_energy': [],
            'update_magnitude': []
        }
    
    def run_session(
        self,
        duration: int = 100,
        schedule_type: str = "exponential",
        safety_scaffold: bool = True
    ) -> Dict:
        """
        Run a complete therapeutic session.
        
        Args:
            duration: Duration of session (timesteps)
            schedule_type: Annealing schedule type
            safety_scaffold: Whether safe context is maintained
            
        Returns:
            Dictionary with session results
        """
        # Activate reconsolidation window (retrieval)
        self.reconsolidation.activate(cue_strength=1.0, current_time=0)
        
        for t in range(duration):
            # Update precision according to annealing schedule
            self.annealing.update_precision(t, duration, schedule_type)
            
            # Get current precision values
            pi_prior = self.annealing.pi_prior
            pi_sensory = self.annealing.pi_sensory
            
            # Present safe sensory input (with safety scaffold)
            if safety_scaffold:
                y = self.safe_sensory
            else:
                # Without scaffold, might reinforce trauma
                y = np.full(self.n_features, -0.5)
            
            # Check reconsolidation window
            can_update = self.reconsolidation.update(
                current_time=t,
                allow_update=safety_scaffold
            )
            
            # Update belief if window is open
            if can_update:
                mu, F, update_mag = self.agent.perceive_and_update(
                    y, pi_prior, pi_sensory, learning_rate=0.01
                )
            else:
                # Window closed, no updating
                mu = self.agent.mu
                F = self.agent.vfe.compute(y, mu, pi_prior)
                update_mag = 0.0
            
            # Record history
            self.history['mu'].append(mu.copy())
            self.history['pi_prior'].append(pi_prior)
            self.history['pi_sensory'].append(pi_sensory)
            self.history['free_energy'].append(F)
            self.history['update_magnitude'].append(update_mag)
        
        return self.history
    
    def assess_outcome(self) -> Dict[str, float]:
        """
        Assess therapeutic outcome.
        
        Returns:
            Dictionary with outcome metrics
        """
        final_mu = self.history['mu'][-1] if self.history['mu'] else None
        final_F = self.history['free_energy'][-1] if self.history['free_energy'] else np.inf
        
        # Compute convergence to safety
        if final_mu is not None:
            convergence = np.linalg.norm(final_mu - self.safe_sensory)
        else:
            convergence = np.inf
        
        # Total belief shift
        if len(self.history['mu']) > 1:
            initial_mu = self.history['mu'][0]
            belief_shift = np.linalg.norm(final_mu - initial_mu)
        else:
            belief_shift = 0.0
        
        outcome = {
            'final_belief': final_mu,
            'final_free_energy': final_F,
            'convergence_to_safety': convergence,
            'total_belief_shift': belief_shift,
            'annealing_complete': self.annealing.is_complete()
        }
        
        return outcome
