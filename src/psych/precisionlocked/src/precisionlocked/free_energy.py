"""
Free Energy Principle and Active Inference Components

This module implements the core computational machinery of the Free Energy 
Principle, including variational free energy calculation and precision weighting.
"""

import numpy as np
from typing import Callable, Optional, Tuple


class VariationalFreeEnergy:
    """
    Variational Free Energy (VFE) calculator.
    
    VFE is an information-theoretic quantity representing the divergence 
    between the internal model and the external world. It serves as an upper 
    bound on "surprise" (negative log probability of sensory outcomes).
    
    F = E_q[log q(μ) - log p(y, μ)]
    
    Where:
    - q(μ) is the recognition density (internal model)
    - p(y, μ) is the generative model
    - y is sensory input
    - μ is the internal state estimate
    """
    
    def __init__(self, sigma_sensory: float = 1.0):
        """
        Initialize the VFE calculator.
        
        Args:
            sigma_sensory: Sensory noise standard deviation (default: 1.0)
        """
        self.sigma_sensory = sigma_sensory
    
    def compute(
        self, 
        y: np.ndarray, 
        mu: np.ndarray, 
        pi_prior: float,
        sigma_prior: float = 1.0
    ) -> float:
        """
        Compute variational free energy.
        
        Args:
            y: Sensory observations (shape: [n_samples, n_features])
            mu: Internal model predictions (shape: [n_samples, n_features])
            pi_prior: Prior precision (inverse variance)
            sigma_prior: Prior standard deviation
            
        Returns:
            Free energy value (scalar)
        """
        # Prediction error
        epsilon = y - mu
        
        # Sensory surprise (accuracy term)
        sensory_surprise = 0.5 * np.sum(epsilon**2) / (self.sigma_sensory**2)
        
        # Complexity term (KL divergence between posterior and prior)
        # Simplified for Gaussian case
        complexity = 0.5 * np.sum(mu**2) * pi_prior
        
        # Total free energy
        F = sensory_surprise + complexity
        
        return F
    
    def prediction_error(self, y: np.ndarray, mu: np.ndarray) -> np.ndarray:
        """
        Compute prediction error.
        
        Args:
            y: Sensory observations
            mu: Internal model predictions
            
        Returns:
            Prediction error (epsilon = y - mu)
        """
        return y - mu
    
    def gradient_descent_update(
        self,
        mu: np.ndarray,
        y: np.ndarray,
        pi_prior: float,
        pi_sensory: float,
        learning_rate: float = 0.01
    ) -> np.ndarray:
        """
        Perform gradient descent update on internal model.
        
        Following the equation from the paper:
        μ̇ = -∂F/∂μ = Π_sensory * ε - Π_prior * μ
        
        Where:
        - ε is the prediction error
        - Π represents precision (inverse variance)
        
        Args:
            mu: Current internal state estimate
            y: Sensory observations
            pi_prior: Prior precision
            pi_sensory: Sensory precision (gain on prediction errors)
            learning_rate: Step size for gradient descent
            
        Returns:
            Updated internal state estimate
        """
        epsilon = self.prediction_error(y, mu)
        
        # Gradient with respect to mu
        # High prior precision -> strong pull toward zero (prior mean)
        # High sensory precision -> strong pull toward sensory data
        gradient = pi_sensory * epsilon - pi_prior * mu
        
        # Adaptive learning rate based on gradient magnitude
        # Prevents numerical instability with high precision values
        grad_norm = np.linalg.norm(gradient)
        if grad_norm > 10.0:
            adaptive_lr = learning_rate * 10.0 / grad_norm
        else:
            adaptive_lr = learning_rate
        
        # Update mu with gradient clipping for stability
        mu_new = mu + adaptive_lr * gradient
        
        # Clip to reasonable range to prevent overflow
        mu_new = np.clip(mu_new, -100.0, 100.0)
        
        return mu_new


class PrecisionWeighting:
    """
    Precision weighting mechanisms for Active Inference.
    
    Precision (Π) acts as the "gain" on prediction errors. In trauma:
    - Π_prior → ∞ (pathologically high)
    - Π_sensory → 0 (sensory evidence ignored)
    
    This creates a deep attractor basin immune to sensory disconfirmation.
    """
    
    @staticmethod
    def healthy_precision(
        uncertainty: float = 1.0,
        confidence: float = 1.0
    ) -> float:
        """
        Compute healthy (adaptive) precision.
        
        Args:
            uncertainty: Environmental uncertainty
            confidence: Confidence in the internal model
            
        Returns:
            Precision value (inverse variance)
        """
        # Precision is inverse of variance
        # Higher uncertainty -> lower precision
        # Higher confidence -> higher precision
        variance = uncertainty / confidence
        precision = 1.0 / max(variance, 1e-6)  # Avoid division by zero
        return precision
    
    @staticmethod
    def pathological_precision(
        base_precision: float = 1.0,
        trauma_gain: float = 100.0
    ) -> float:
        """
        Compute pathological (trauma-induced) precision.
        
        In trauma, precision is pathologically elevated (Π → ∞),
        creating a rigid prior that resists updating.
        
        Args:
            base_precision: Baseline precision
            trauma_gain: Multiplicative trauma factor (>>1)
            
        Returns:
            Pathologically high precision
        """
        return base_precision * trauma_gain
    
    @staticmethod
    def relative_precision(
        pi_prior: float,
        pi_sensory: float
    ) -> Tuple[float, str]:
        """
        Compute the relative balance between prior and sensory precision.
        
        Args:
            pi_prior: Prior precision
            pi_sensory: Sensory precision
            
        Returns:
            Tuple of (ratio, regime_description)
            - ratio: pi_prior / pi_sensory
            - regime: "prior-driven" if ratio > 1, else "sensory-driven"
        """
        ratio = pi_prior / max(pi_sensory, 1e-6)
        
        if ratio > 10:
            regime = "strongly prior-driven (trauma-like)"
        elif ratio > 1:
            regime = "prior-driven"
        elif ratio > 0.1:
            regime = "sensory-driven"
        else:
            regime = "strongly sensory-driven"
        
        return ratio, regime
    
    @staticmethod
    def effective_update_rate(
        pi_prior: float,
        pi_sensory: float
    ) -> float:
        """
        Compute effective learning rate given precision balance.
        
        If pi_prior → ∞, the update rate → 0 (system is "frozen").
        
        Args:
            pi_prior: Prior precision
            pi_sensory: Sensory precision
            
        Returns:
            Effective learning rate (0 to 1)
        """
        # Normalized by total precision
        total_precision = pi_prior + pi_sensory
        effective_rate = pi_sensory / total_precision
        
        return effective_rate


class ActiveInference:
    """
    Active Inference framework for trauma modeling.
    
    Combines VFE minimization with precision-weighted prediction errors
    to model belief updating (or lack thereof in trauma).
    """
    
    def __init__(
        self,
        n_features: int = 1,
        sigma_sensory: float = 1.0
    ):
        """
        Initialize Active Inference agent.
        
        Args:
            n_features: Dimensionality of sensory space
            sigma_sensory: Sensory noise level
        """
        self.n_features = n_features
        self.vfe = VariationalFreeEnergy(sigma_sensory)
        self.precision = PrecisionWeighting()
        
        # Initialize internal state
        self.mu = np.zeros(n_features)
    
    def perceive_and_update(
        self,
        y: np.ndarray,
        pi_prior: float,
        pi_sensory: float,
        learning_rate: float = 0.1
    ) -> Tuple[np.ndarray, float, float]:
        """
        Perceive sensory input and update internal model.
        
        Args:
            y: Sensory observation
            pi_prior: Prior precision
            pi_sensory: Sensory precision
            learning_rate: Update step size
            
        Returns:
            Tuple of (updated_mu, free_energy, update_magnitude)
        """
        # Compute current free energy
        F_before = self.vfe.compute(y, self.mu, pi_prior)
        
        # Update internal model
        mu_new = self.vfe.gradient_descent_update(
            self.mu, y, pi_prior, pi_sensory, learning_rate
        )
        
        # Compute update magnitude
        update_magnitude = np.linalg.norm(mu_new - self.mu)
        
        # Update state
        self.mu = mu_new
        
        # Compute new free energy
        F_after = self.vfe.compute(y, self.mu, pi_prior)
        
        return self.mu, F_after, update_magnitude
    
    def reset(self, initial_state: Optional[np.ndarray] = None):
        """Reset internal state."""
        if initial_state is not None:
            self.mu = initial_state.copy()
        else:
            self.mu = np.zeros(self.n_features)
