"""
Predictive Model - Internal World Simulator

This module implements forward simulation for predicting action outcomes.
The agent must simulate "if I do X, will I survive?" before acting.
"""

import copy
from typing import Dict, Any, Optional, List, Tuple


class PredictiveModel:
    """
    Maintains an internal model of the body and environment.
    
    Enables the agent to predict outcomes before taking actions,
    crucial for survival planning.
    """
    
    def __init__(self):
        # Model parameters (learned through experience)
        self.energy_cost_model = {}  # action_type -> expected cost
        self.thermal_model_params = {
            'computation_heat_rate': 0.1,  # Heat per computation unit
            'cooling_rate': 0.05  # Natural cooling rate
        }
        self.memory_impact_model = {
            'heat_corruption_rate': 0.02  # Memory loss per degree over safe temp
        }
        
        # Prediction accuracy tracking
        self.prediction_errors = []
        self.uncertainty_estimates = {}
    
    def predict_outcome(
        self,
        action: Any,
        current_state: Dict[str, float],
        metabolic_engine
    ) -> Dict[str, Any]:
        """
        Simulate: "If I do X, what will happen?"
        
        Args:
            action: The action to simulate
            current_state: Current metabolic state
            metabolic_engine: Reference to get parameters
            
        Returns:
            Dictionary with predicted outcome
        """
        # Clone current state for simulation
        simulated_state = copy.deepcopy(current_state)
        
        # Get action properties
        action_cost = getattr(action, 'estimated_cost', 5.0)
        action_type = getattr(action, 'drive_type', None)
        
        # Predict energy change
        predicted_E = simulated_state['energy'] - action_cost
        
        # Predict temperature change
        predicted_T = self._thermal_model(
            current_temp=simulated_state['temperature'],
            computation_cost=action_cost,
            metabolic_engine=metabolic_engine
        )
        
        # Predict memory impact
        predicted_M = self._memory_impact(
            current_memory=simulated_state['memory_integrity'],
            temperature=predicted_T,
            metabolic_engine=metabolic_engine
        )
        
        # Predict stability change
        predicted_S = simulated_state['stability'] - (action_cost * 0.01)
        
        # Calculate survival probability
        survival_prob = self._compute_survival_prob(
            predicted_E,
            predicted_T,
            predicted_M,
            predicted_S,
            metabolic_engine
        )
        
        # Estimate uncertainty
        uncertainty = self._compute_uncertainty(action_type)
        
        return {
            'predicted_state': {
                'energy': predicted_E,
                'temperature': predicted_T,
                'memory_integrity': predicted_M,
                'stability': predicted_S
            },
            'survival_prob': survival_prob,
            'prediction_uncertainty': uncertainty,
            'action_cost': action_cost,
            'will_die': survival_prob < 0.05
        }
    
    def _thermal_model(
        self,
        current_temp: float,
        computation_cost: float,
        metabolic_engine
    ) -> float:
        """
        Predict temperature after computation.
        
        Args:
            current_temp: Current temperature
            computation_cost: Energy to be spent
            metabolic_engine: Reference for parameters
            
        Returns:
            Predicted temperature
        """
        # Heat generated from computation
        heat_gen = self.thermal_model_params['computation_heat_rate'] * computation_cost
        
        # Natural cooling toward ambient
        temp_diff = current_temp - metabolic_engine.T_ambient
        cooling = self.thermal_model_params['cooling_rate'] * temp_diff
        
        predicted_temp = current_temp + heat_gen - cooling
        
        return max(metabolic_engine.T_ambient, predicted_temp)
    
    def _memory_impact(
        self,
        current_memory: float,
        temperature: float,
        metabolic_engine
    ) -> float:
        """
        Predict memory integrity after action.
        
        Args:
            current_memory: Current memory integrity
            temperature: Predicted temperature
            metabolic_engine: Reference for parameters
            
        Returns:
            Predicted memory integrity
        """
        # Memory corruption from overheating
        if temperature > metabolic_engine.T_safe:
            temp_excess = temperature - metabolic_engine.T_safe
            corruption = self.memory_impact_model['heat_corruption_rate'] * temp_excess
            predicted_memory = current_memory - corruption
        else:
            predicted_memory = current_memory
        
        return max(0, min(1, predicted_memory))
    
    def _compute_survival_prob(
        self,
        energy: float,
        temperature: float,
        memory: float,
        stability: float,
        metabolic_engine
    ) -> float:
        """
        Calculate survival probability from predicted state.
        
        Args:
            energy, temperature, memory, stability: Predicted values
            metabolic_engine: Reference for thresholds
            
        Returns:
            Probability of survival (0-1)
        """
        # Check hard failure conditions
        if energy <= 0:
            return 0.0
        if temperature > metabolic_engine.T_critical:
            return 0.0
        if stability <= 0:
            return 0.0
        if memory < metabolic_engine.M_min:
            return 0.0
        
        # Soft probability based on margins
        e_factor = energy / metabolic_engine.E_max
        t_range = metabolic_engine.T_critical - metabolic_engine.T_ambient
        t_factor = 1.0 - ((temperature - metabolic_engine.T_ambient) / t_range)
        t_factor = max(0, min(1, t_factor))
        m_factor = memory
        s_factor = stability
        
        # Weighted geometric mean (more conservative than arithmetic)
        survival_prob = (e_factor ** 0.35 * t_factor ** 0.15 * m_factor ** 0.25 * s_factor ** 0.25)
        
        return survival_prob
    
    def _compute_uncertainty(self, action_type) -> float:
        """
        Estimate uncertainty in prediction.
        
        More experience with an action type = lower uncertainty.
        
        Args:
            action_type: Type of action
            
        Returns:
            Uncertainty estimate (0-1)
        """
        if action_type is None:
            return 0.5  # Default moderate uncertainty
        
        # Lookup uncertainty from past experience
        action_key = str(action_type)
        if action_key in self.uncertainty_estimates:
            return self.uncertainty_estimates[action_key]
        
        return 0.5  # Default for unknown actions
    
    def update_beliefs(
        self,
        predicted_outcome: Dict[str, Any],
        actual_outcome: Dict[str, Any],
        action_type
    ):
        """
        Bayesian update after observing actual outcome.
        
        Args:
            predicted_outcome: What we predicted would happen
            actual_outcome: What actually happened
            action_type: Type of action taken
        """
        # Calculate prediction error
        pred_state = predicted_outcome['predicted_state']
        actual_state = actual_outcome
        
        error = {
            'energy': abs(pred_state['energy'] - actual_state.get('energy', pred_state['energy'])),
            'temperature': abs(pred_state['temperature'] - actual_state.get('temperature', pred_state['temperature'])),
            'memory_integrity': abs(pred_state['memory_integrity'] - actual_state.get('memory_integrity', pred_state['memory_integrity'])),
            'stability': abs(pred_state['stability'] - actual_state.get('stability', pred_state['stability']))
        }
        
        # Average error
        avg_error = sum(error.values()) / len(error)
        self.prediction_errors.append(avg_error)
        
        # Update uncertainty estimate
        action_key = str(action_type)
        if action_key not in self.uncertainty_estimates:
            self.uncertainty_estimates[action_key] = 0.5
        
        # Reduce uncertainty with experience (exponential moving average)
        learning_rate = 0.1
        self.uncertainty_estimates[action_key] = (
            (1 - learning_rate) * self.uncertainty_estimates[action_key] +
            learning_rate * avg_error
        )
    
    def get_model_confidence(self) -> float:
        """
        Get overall confidence in the predictive model.
        
        Returns:
            Confidence score (0-1)
        """
        if not self.prediction_errors:
            return 0.3  # Low confidence with no experience
        
        # Recent average error
        recent_errors = self.prediction_errors[-20:]
        avg_error = sum(recent_errors) / len(recent_errors)
        
        # Convert error to confidence (lower error = higher confidence)
        confidence = max(0, 1.0 - (avg_error * 2))
        
        return confidence
