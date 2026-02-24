"""
Expected Free Energy Calculator
Active Inference decision-making system
"""

import math
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ActionSimulation:
    """Simulation of an action's outcome"""
    action_name: str
    energy_cost: float
    heat_generated: float
    expected_energy_gain: float
    expected_stability_change: float
    expected_memory_change: float
    uncertainty: float  # Epistemic uncertainty about outcome
    
    # Active Inference components
    pragmatic_value: float = 0.0  # Survival value
    epistemic_value: float = 0.0  # Information gain
    efe: float = 0.0  # Expected Free Energy (lower is better)


class EFECalculator:
    """
    Expected Free Energy Calculator
    
    Uses Active Inference mathematics to choose actions by minimizing EFE.
    Trade-off between:
    - Pragmatic Value: Staying alive (keeping E high, T low)
    - Epistemic Value: Reducing uncertainty (exploring)
    - Cost: The caloric expense of the action
    """
    
    def __init__(
        self,
        pragmatic_weight: float = 1.0,
        epistemic_weight: float = 0.3,
        cost_weight: float = 1.0
    ):
        """
        Initialize EFE calculator
        
        Args:
            pragmatic_weight: Weight for survival/pragmatic value
            epistemic_weight: Weight for epistemic/exploratory value
            cost_weight: Weight for action cost
        """
        self.pragmatic_weight = pragmatic_weight
        self.epistemic_weight = epistemic_weight
        self.cost_weight = cost_weight
    
    def calculate_efe(
        self,
        action: ActionSimulation,
        current_state: Dict[str, float]
    ) -> float:
        """
        Calculate Expected Free Energy for an action
        
        EFE = -PragmaticValue - EpistemicValue + Cost
        
        Lower EFE is better (we want to minimize free energy)
        """
        # Calculate pragmatic value (survival)
        pragmatic_value = self._calculate_pragmatic_value(action, current_state)
        
        # Calculate epistemic value (uncertainty reduction)
        epistemic_value = self._calculate_epistemic_value(action)
        
        # Calculate cost
        cost = self._calculate_cost(action, current_state)
        
        # Calculate EFE
        efe = (
            - self.pragmatic_weight * pragmatic_value
            - self.epistemic_weight * epistemic_value
            + self.cost_weight * cost
        )
        
        # Store values in action simulation
        action.pragmatic_value = pragmatic_value
        action.epistemic_value = epistemic_value
        action.efe = efe
        
        return efe
    
    def _calculate_pragmatic_value(
        self,
        action: ActionSimulation,
        current_state: Dict[str, float]
    ) -> float:
        """
        Calculate pragmatic value: staying alive
        
        Keeping E high, T low, M and S stable
        """
        current_energy = current_state.get("energy", 50.0)
        current_temp = current_state.get("temperature", 37.0)
        current_stability = current_state.get("stability", 50.0)
        
        # Predict future state after action
        future_energy = current_energy - action.energy_cost + action.expected_energy_gain
        future_temp = current_temp + action.heat_generated
        future_stability = current_stability + action.expected_stability_change
        
        # Value based on future state
        energy_value = self._sigmoid(future_energy, 50.0, 20.0)  # Want energy > 50
        temp_value = 1.0 - self._sigmoid(future_temp, 45.0, 10.0)  # Want temp < 45
        stability_value = self._sigmoid(future_stability, 50.0, 20.0)  # Want stability > 50
        
        # Critical: if action would kill us, very negative value
        if future_energy <= 0 or future_stability <= 0:
            return -10.0
        
        # Weighted average
        pragmatic_value = (
            energy_value * 0.5 +
            temp_value * 0.2 +
            stability_value * 0.3
        )
        
        return pragmatic_value
    
    def _calculate_epistemic_value(self, action: ActionSimulation) -> float:
        """
        Calculate epistemic value: reducing uncertainty
        
        Exploration actions have high epistemic value
        """
        # High uncertainty means potential for information gain
        # But also risk - so we use a moderate function
        if action.uncertainty > 0.7:
            # Very uncertain - high epistemic value but risky
            return 0.5 + (action.uncertainty - 0.7) * 0.5
        else:
            # Low uncertainty - less to learn
            return action.uncertainty * 0.5
    
    def _calculate_cost(
        self,
        action: ActionSimulation,
        current_state: Dict[str, float]
    ) -> float:
        """
        Calculate the cost of an action
        
        Includes energy cost and risk of heat damage
        """
        current_energy = current_state.get("energy", 50.0)
        current_temp = current_state.get("temperature", 37.0)
        
        # Base cost is the energy expenditure
        energy_cost_normalized = action.energy_cost / 100.0
        
        # Heat cost - how much does this push us toward dangerous temperatures?
        future_temp = current_temp + action.heat_generated
        heat_cost = 0.0
        if future_temp > 50.0:  # Dangerous heat
            heat_cost = (future_temp - 50.0) / 20.0  # Normalize
        
        # Relative cost - actions are more costly when we have less energy
        if current_energy < 30:
            relative_cost = energy_cost_normalized * 2.0  # Double cost when low energy
        else:
            relative_cost = energy_cost_normalized
        
        total_cost = relative_cost + heat_cost
        return total_cost
    
    def _sigmoid(self, x: float, midpoint: float, steepness: float) -> float:
        """Sigmoid function for smooth value curves"""
        return 1.0 / (1.0 + math.exp(-(x - midpoint) / steepness))
    
    def select_action(
        self,
        actions: List[ActionSimulation],
        current_state: Dict[str, float]
    ) -> ActionSimulation:
        """
        Select the best action by minimizing EFE
        
        Returns the action with lowest Expected Free Energy
        """
        if not actions:
            raise ValueError("No actions to choose from")
        
        # Calculate EFE for all actions
        for action in actions:
            self.calculate_efe(action, current_state)
        
        # Select action with minimum EFE
        best_action = min(actions, key=lambda a: a.efe)
        return best_action
    
    def simulate_outcome(
        self,
        action: ActionSimulation,
        current_state: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Predictive processing: simulate the outcome of an action
        
        This is used before executing high-cost actions like "Deep Think"
        to predict if the resulting heat will damage stability or if
        the energy cost will kill the agent.
        """
        predicted_state = current_state.copy()
        
        # Apply action effects
        predicted_state["energy"] = max(
            0, predicted_state["energy"] - action.energy_cost + action.expected_energy_gain
        )
        predicted_state["temperature"] = predicted_state.get("temperature", 37.0) + action.heat_generated
        predicted_state["stability"] = max(
            0, predicted_state["stability"] + action.expected_stability_change
        )
        predicted_state["memory_integrity"] = max(
            0, predicted_state.get("memory_integrity", 100.0) + action.expected_memory_change
        )
        
        # Check for death conditions
        predicted_state["will_survive"] = (
            predicted_state["energy"] > 0 and predicted_state["stability"] > 0
        )
        
        return predicted_state
    
    def should_execute_action(
        self,
        action: ActionSimulation,
        current_state: Dict[str, float],
        risk_tolerance: float = 0.2
    ) -> tuple[bool, str]:
        """
        Decide whether to execute an action based on predicted outcome
        
        Returns (should_execute, reasoning)
        """
        predicted_state = self.simulate_outcome(action, current_state)
        
        # Check if action would kill us
        if not predicted_state["will_survive"]:
            return False, "Action would result in death (E<=0 or S<=0)"
        
        # Check if action leaves us in critical state
        if predicted_state["energy"] < 10:
            if risk_tolerance < 0.5:
                return False, "Action would leave us in critical energy state"
        
        # Check if action causes dangerous overheating
        if predicted_state["temperature"] > 60:
            return False, "Action would cause dangerous overheating"
        
        # Check if stability damage is too severe
        if predicted_state["stability"] < 20:
            if risk_tolerance < 0.7:
                return False, "Action would severely damage stability"
        
        return True, "Action is safe to execute"
    
    def compare_actions(
        self,
        actions: List[ActionSimulation],
        current_state: Dict[str, float]
    ) -> List[Dict]:
        """
        Compare multiple actions and return analysis
        """
        results = []
        
        for action in actions:
            self.calculate_efe(action, current_state)
            predicted_state = self.simulate_outcome(action, current_state)
            
            results.append({
                "action": action.action_name,
                "efe": action.efe,
                "pragmatic_value": action.pragmatic_value,
                "epistemic_value": action.epistemic_value,
                "will_survive": predicted_state["will_survive"],
                "predicted_energy": predicted_state["energy"],
                "predicted_temp": predicted_state["temperature"],
                "predicted_stability": predicted_state["stability"]
            })
        
        # Sort by EFE (lower is better)
        results.sort(key=lambda x: x["efe"])
        return results
