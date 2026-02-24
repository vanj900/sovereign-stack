"""
Trauma Model Components

This module implements the computational anatomy of trauma as described in the paper:
- Trauma as a pathological attractor basin
- Allostatic load from chronic error suppression
- Metabolic cost modeling
"""

import numpy as np
from typing import Tuple, List, Optional
from .free_energy import VariationalFreeEnergy, PrecisionWeighting


class TraumaAttractor:
    """
    Model of trauma as a deep attractor basin in the free-energy landscape.
    
    When prior precision Π_prior → ∞:
    - The update term μ̇ → 0
    - The system becomes trapped in a rigid configuration
    - Sensory evidence cannot update the internal model
    """
    
    def __init__(
        self,
        trauma_prior_mean: float = -1.0,  # "Danger" prior
        trauma_prior_precision: float = 100.0,  # Pathologically high
        healthy_prior_precision: float = 1.0
    ):
        """
        Initialize trauma attractor model.
        
        Args:
            trauma_prior_mean: Mean of the trauma prior (e.g., threat level)
            trauma_prior_precision: Precision of trauma prior (Π → ∞)
            healthy_prior_precision: Precision in healthy state
        """
        self.trauma_prior_mean = trauma_prior_mean
        self.trauma_prior_precision = trauma_prior_precision
        self.healthy_prior_precision = healthy_prior_precision
        
        self.vfe = VariationalFreeEnergy()
    
    def basin_depth(
        self,
        mu: np.ndarray,
        trauma_state: bool = True
    ) -> float:
        """
        Compute the depth of the attractor basin.
        
        Deeper basin = harder to escape = more rigid belief.
        
        Args:
            mu: Current internal state
            trauma_state: Whether in trauma state (high precision)
            
        Returns:
            Basin depth (energy barrier to escape)
        """
        pi = (self.trauma_prior_precision if trauma_state 
              else self.healthy_prior_precision)
        
        # Energy barrier proportional to precision
        # Distance from prior mean weighted by precision
        deviation = mu - self.trauma_prior_mean
        depth = 0.5 * pi * np.sum(deviation**2)
        
        return depth
    
    def escape_probability(
        self,
        sensory_evidence: np.ndarray,
        current_belief: np.ndarray,
        temperature: float = 1.0
    ) -> float:
        """
        Probability of escaping the attractor basin given sensory evidence.
        
        Uses Boltzmann-like probability: P ∝ exp(-E/T)
        where E is the energy barrier and T is "temperature" (uncertainty).
        
        Args:
            sensory_evidence: Current sensory input
            current_belief: Current internal belief state
            temperature: Uncertainty/temperature parameter
            
        Returns:
            Escape probability (0 to 1)
        """
        # Energy difference between current state and evidence
        E_current = self.basin_depth(current_belief, trauma_state=True)
        E_evidence = 0.5 * np.sum((sensory_evidence - current_belief)**2)
        
        # Boltzmann probability
        delta_E = E_evidence - E_current
        prob = np.exp(-delta_E / max(temperature, 1e-6))
        
        # Normalize to [0, 1]
        prob = min(max(prob, 0.0), 1.0)
        
        return prob
    
    def is_trapped(
        self,
        pi_prior: float,
        pi_sensory: float,
        threshold: float = 10.0
    ) -> bool:
        """
        Determine if the system is trapped in the trauma attractor.
        
        System is "trapped" when prior precision dominates sensory precision.
        
        Args:
            pi_prior: Prior precision
            pi_sensory: Sensory precision
            threshold: Ratio threshold for "trapped" state
            
        Returns:
            True if trapped (pathological), False otherwise
        """
        ratio = pi_prior / max(pi_sensory, 1e-6)
        return ratio > threshold


class AllostaticLoad:
    """
    Model of allostatic load as the metabolic cost of chronic error suppression.
    
    The Energetic Paradox:
    - Internal model is rigid (low uncertainty)
    - But organism is physically exhausted
    - Mechanism: Continuous high-amplitude prediction errors must be suppressed
    - Cost: Neural inhibition is metabolically expensive (ATP consumption)
    """
    
    def __init__(
        self,
        base_metabolic_rate: float = 1.0,
        suppression_cost_factor: float = 2.0
    ):
        """
        Initialize allostatic load calculator.
        
        Args:
            base_metabolic_rate: Baseline ATP consumption
            suppression_cost_factor: Multiplicative cost of error suppression
        """
        self.base_metabolic_rate = base_metabolic_rate
        self.suppression_cost_factor = suppression_cost_factor
    
    def prediction_error_magnitude(
        self,
        y: np.ndarray,
        mu: np.ndarray
    ) -> float:
        """
        Compute magnitude of prediction errors.
        
        Args:
            y: Sensory observations (safe environment)
            mu: Internal predictions (danger)
            
        Returns:
            Magnitude of prediction error
        """
        epsilon = y - mu
        magnitude = np.linalg.norm(epsilon)
        return magnitude
    
    def suppression_cost(
        self,
        epsilon_magnitude: float,
        pi_prior: float
    ) -> float:
        """
        Compute metabolic cost of suppressing prediction errors.
        
        Cost increases with:
        1. Magnitude of prediction error (more to suppress)
        2. Prior precision (stronger suppression needed)
        
        Args:
            epsilon_magnitude: Magnitude of prediction errors
            pi_prior: Prior precision (strength of suppression)
            
        Returns:
            Metabolic cost (ATP consumption)
        """
        # Cost = base rate + suppression effort
        # Suppression effort = error magnitude × precision (gain)
        suppression_effort = (
            epsilon_magnitude * pi_prior * self.suppression_cost_factor
        )
        
        total_cost = self.base_metabolic_rate + suppression_effort
        
        return total_cost
    
    def cumulative_load(
        self,
        epsilon_history: List[float],
        pi_prior: float
    ) -> float:
        """
        Compute cumulative allostatic load over time.
        
        Chronic stress = sustained high metabolic cost.
        
        Args:
            epsilon_history: History of prediction error magnitudes
            pi_prior: Prior precision (constant in trauma state)
            
        Returns:
            Cumulative allostatic load
        """
        total_load = 0.0
        
        for epsilon_mag in epsilon_history:
            cost = self.suppression_cost(epsilon_mag, pi_prior)
            total_load += cost
        
        return total_load
    
    def load_rate(
        self,
        y: np.ndarray,
        mu: np.ndarray,
        pi_prior: float
    ) -> float:
        """
        Compute instantaneous allostatic load rate.
        
        Args:
            y: Current sensory input
            mu: Current internal state
            pi_prior: Prior precision
            
        Returns:
            Current load rate (cost per time step)
        """
        epsilon_mag = self.prediction_error_magnitude(y, mu)
        cost = self.suppression_cost(epsilon_mag, pi_prior)
        
        return cost
    
    def is_exhausted(
        self,
        cumulative_load: float,
        threshold: float = 100.0
    ) -> bool:
        """
        Determine if the organism is in a state of exhaustion.
        
        Args:
            cumulative_load: Total accumulated allostatic load
            threshold: Exhaustion threshold
            
        Returns:
            True if exhausted, False otherwise
        """
        return cumulative_load > threshold


class TraumaSimulator:
    """
    Simulator for trauma dynamics over time.
    
    Simulates the progression from:
    1. Traumatic event (high-precision encoding)
    2. Mismatch with safe environment
    3. Chronic error suppression
    4. Allostatic load accumulation
    """
    
    def __init__(
        self,
        n_features: int = 1,
        trauma_precision: float = 100.0,
        safe_environment_mean: float = 1.0  # Positive = safe
    ):
        """
        Initialize trauma simulator.
        
        Args:
            n_features: Dimensionality of state space
            trauma_precision: Precision of trauma prior (Π → ∞)
            safe_environment_mean: Mean of safe environmental state
        """
        self.n_features = n_features
        self.trauma_precision = trauma_precision
        self.safe_environment = np.full(n_features, safe_environment_mean)
        
        self.attractor = TraumaAttractor(
            trauma_prior_mean=-1.0,  # Danger
            trauma_prior_precision=trauma_precision
        )
        self.allostatic = AllostaticLoad()
        
        # State variables
        self.mu = np.full(n_features, -1.0)  # Initialized at danger
        self.load_history = []
        self.error_history = []
    
    def simulate_timestep(
        self,
        sensory_input: Optional[np.ndarray] = None
    ) -> Tuple[float, float, bool]:
        """
        Simulate one timestep of trauma dynamics.
        
        Args:
            sensory_input: Current sensory observation (defaults to safe)
            
        Returns:
            Tuple of (prediction_error, allostatic_load, is_trapped)
        """
        # Default to safe environment
        if sensory_input is None:
            sensory_input = self.safe_environment
        
        # Compute prediction error
        epsilon = sensory_input - self.mu
        epsilon_mag = np.linalg.norm(epsilon)
        
        # Compute allostatic load
        load = self.allostatic.load_rate(
            sensory_input, self.mu, self.trauma_precision
        )
        
        # Check if trapped
        trapped = self.attractor.is_trapped(
            self.trauma_precision,
            pi_sensory=1.0  # Low sensory precision in trauma
        )
        
        # Store history
        self.error_history.append(epsilon_mag)
        self.load_history.append(load)
        
        # In trauma state, mu does NOT update (trapped)
        # This is the core pathology
        
        return epsilon_mag, load, trapped
    
    def run_simulation(
        self,
        n_timesteps: int = 100
    ) -> dict:
        """
        Run full trauma simulation.
        
        Args:
            n_timesteps: Number of timesteps to simulate
            
        Returns:
            Dictionary with simulation results
        """
        results = {
            'errors': [],
            'loads': [],
            'cumulative_load': [],
            'trapped': []
        }
        
        cumulative = 0.0
        
        for t in range(n_timesteps):
            error, load, trapped = self.simulate_timestep()
            cumulative += load
            
            results['errors'].append(error)
            results['loads'].append(load)
            results['cumulative_load'].append(cumulative)
            results['trapped'].append(trapped)
        
        return results
