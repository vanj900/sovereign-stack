"""
Active Inference Loop - The Decision Engine

This module implements the core decision-making loop using Expected Free Energy
to select actions that balance survival, exploration, and cost.
"""

from typing import List, Dict, Any, Optional
import math


class ActiveInferenceLoop:
    """
    Core decision engine using the Free Energy Principle.
    
    The agent minimizes Expected Free Energy (EFE) to select actions:
    EFE = Pragmatic_Value + Epistemic_Value - Action_Cost
    """
    
    def __init__(
        self,
        metabolic_engine,
        goal_manager,
        predictive_model,
        ethical_engine=None
    ):
        self.metabolic_engine = metabolic_engine
        self.goal_manager = goal_manager
        self.predictive_model = predictive_model
        self.ethical_engine = ethical_engine
        
        # Weights for different components
        self.pragmatic_weight = 0.6  # Survival value
        self.epistemic_weight = 0.2  # Information gain
        self.cost_weight = 0.2  # Energy expense
        
        # Decision history
        self.decisions = []
        self.step_count = 0
    
    def step(self, environment) -> Dict[str, Any]:
        """
        Execute one complete active inference cycle.
        
        Args:
            environment: The environment to interact with
            
        Returns:
            Dictionary with step results
        """
        if not self.metabolic_engine.is_alive:
            return {'status': 'dead', 'cause': self.metabolic_engine.death_cause}
        
        self.step_count += 1
        
        # 1. Perceive current state
        observations = self._perceive(environment)
        
        # 2. Update drives based on metabolic state
        self.goal_manager.update_drives_from_metabolic_state(self.metabolic_engine)
        
        # 3. Generate action candidates (from goals)
        possible_actions = self._generate_action_candidates()
        
        if not possible_actions:
            # No actions available, just decay
            self.metabolic_engine.passive_decay(dt=1.0)
            return {'status': 'no_actions', 'survived': self.metabolic_engine.is_alive}
        
        # 4. Compute EFE for each action
        efe_scores = self._compute_efe_for_actions(possible_actions)
        
        # 5. Select action minimizing EFE
        chosen_action = min(efe_scores, key=lambda a: efe_scores[a]['efe'])
        
        # 6. Execute action
        outcome = self._execute_action(chosen_action, environment)
        
        # 7. Update beliefs (learn from experience)
        self._update_beliefs(chosen_action, outcome)
        
        # 8. Apply passive decay
        self.metabolic_engine.passive_decay(dt=1.0)
        
        # 9. Record decision
        self._record_decision(chosen_action, efe_scores[chosen_action], outcome)
        
        return {
            'status': 'active',
            'action': chosen_action,
            'efe_scores': {str(a): s for a, s in efe_scores.items()},
            'outcome': outcome,
            'survived': self.metabolic_engine.is_alive,
            'metabolic_state': self.metabolic_engine.get_state()
        }
    
    def _perceive(self, environment) -> Dict[str, Any]:
        """Perceive current state from environment"""
        return {
            'metabolic_state': self.metabolic_engine.get_state(),
            'available_resources': environment.get_available_resources() if hasattr(environment, 'get_available_resources') else []
        }
    
    def _generate_action_candidates(self) -> List[Any]:
        """
        Generate possible actions from current goals.
        
        Returns:
            List of action objects
        """
        # Generate goals if needed
        new_goals = self.goal_manager.generate_goals(self.metabolic_engine)
        
        # Get prioritized goals
        prioritized_goals = self.goal_manager.prioritize_goals()
        
        # Convert top goals to actions (simplified - in full system, this would be more complex)
        actions = prioritized_goals[:5]  # Consider top 5 goals
        
        return actions
    
    def _compute_efe_for_actions(self, actions: List[Any]) -> Dict[Any, Dict[str, float]]:
        """
        Compute Expected Free Energy for each action.
        
        EFE = Pragmatic + Epistemic - Cost
        
        Args:
            actions: List of possible actions
            
        Returns:
            Dictionary mapping actions to EFE components
        """
        efe_scores = {}
        current_state = self.metabolic_engine.get_state()
        
        for action in actions:
            # Predict outcome
            prediction = self.predictive_model.predict_outcome(
                action,
                current_state,
                self.metabolic_engine
            )
            
            # Pragmatic value: survival benefit
            pragmatic = self._calculate_pragmatic_value(prediction, action)
            
            # Epistemic value: information gain
            epistemic = self._calculate_epistemic_value(prediction, action)
            
            # Cost: energy and risk
            cost = self._calculate_action_cost(action, prediction)
            
            # Expected Free Energy (lower is better, so we minimize)
            efe = -(self.pragmatic_weight * pragmatic +
                    self.epistemic_weight * epistemic -
                    self.cost_weight * cost)
            
            efe_scores[action] = {
                'efe': efe,
                'pragmatic': pragmatic,
                'epistemic': epistemic,
                'cost': cost,
                'prediction': prediction
            }
        
        return efe_scores
    
    def _calculate_pragmatic_value(
        self,
        prediction: Dict[str, Any],
        action: Any
    ) -> float:
        """
        Calculate pragmatic value (survival benefit).
        
        Args:
            prediction: Predicted outcome
            action: The action
            
        Returns:
            Value 0-1 (higher is better)
        """
        # Survival probability is key pragmatic value
        survival_prob = prediction['survival_prob']
        
        # Energy balance
        current_e = self.metabolic_engine.E
        predicted_e = prediction['predicted_state']['energy']
        energy_change = predicted_e - current_e
        
        # Benefit from survival goal actions
        benefit = getattr(action, 'estimated_benefit', 0)
        
        # Normalize and combine
        pragmatic = (
            0.5 * survival_prob +
            0.3 * min(1.0, max(0, (energy_change + 50) / 100)) +
            0.2 * min(1.0, benefit / 50)
        )
        
        return pragmatic
    
    def _calculate_epistemic_value(
        self,
        prediction: Dict[str, Any],
        action: Any
    ) -> float:
        """
        Calculate epistemic value (information gain).
        
        Exploring unknown actions has higher epistemic value.
        
        Args:
            prediction: Predicted outcome
            action: The action
            
        Returns:
            Value 0-1
        """
        # Uncertainty reduction is epistemic value
        uncertainty = prediction['prediction_uncertainty']
        
        # Higher uncertainty means more potential to learn
        epistemic = uncertainty
        
        # Exploration actions have bonus epistemic value
        action_type = getattr(action, 'drive_type', None)
        if action_type and str(action_type).endswith('EXPLORATION'):
            epistemic *= 1.5
        
        return min(1.0, epistemic)
    
    def _calculate_action_cost(
        self,
        action: Any,
        prediction: Dict[str, Any]
    ) -> float:
        """
        Calculate full cost of action (energy + risk).
        
        Args:
            action: The action
            prediction: Predicted outcome
            
        Returns:
            Cost 0-1 (normalized)
        """
        # Direct energy cost
        energy_cost = getattr(action, 'estimated_cost', 5.0)
        
        # Risk cost (probability of death)
        risk_cost = 1.0 - prediction['survival_prob']
        
        # Normalize energy cost
        normalized_energy = energy_cost / self.metabolic_engine.E_max
        
        # Combine
        total_cost = 0.6 * normalized_energy + 0.4 * risk_cost
        
        return total_cost
    
    def _execute_action(self, action: Any, environment) -> Dict[str, Any]:
        """
        Execute the chosen action in the environment.
        
        Args:
            action: Action to execute
            environment: Environment to interact with
            
        Returns:
            Outcome dictionary
        """
        action_cost = getattr(action, 'estimated_cost', 5.0)
        action_type = getattr(action, 'drive_type', None)
        
        try:
            # Execute computation
            result = self.metabolic_engine.compute(action, action_cost)
            
            # Interact with environment based on action type
            if hasattr(environment, 'execute_action'):
                env_result = environment.execute_action(action, self.metabolic_engine)
            else:
                env_result = {}
            
            outcome = {
                'success': True,
                'result': result,
                'environment_result': env_result,
                **self.metabolic_engine.get_state()
            }
            
            # Mark goal as completed if it was a goal
            if hasattr(action, 'goal_id'):
                self.goal_manager.complete_goal(action, outcome)
            
        except Exception as e:
            outcome = {
                'success': False,
                'error': str(e),
                **self.metabolic_engine.get_state()
            }
            
            # Mark goal as abandoned if it was a goal
            if hasattr(action, 'goal_id'):
                self.goal_manager.abandon_goal(action, str(e))
        
        return outcome
    
    def _update_beliefs(self, action: Any, outcome: Dict[str, Any]):
        """Update predictive model based on actual outcome"""
        action_type = getattr(action, 'drive_type', None)
        
        # Get the prediction we made
        prediction = None
        if hasattr(action, '_last_prediction'):
            prediction = action._last_prediction
        
        if prediction:
            self.predictive_model.update_beliefs(
                prediction,
                outcome,
                action_type
            )
    
    def _record_decision(
        self,
        action: Any,
        efe_data: Dict[str, float],
        outcome: Dict[str, Any]
    ):
        """Record decision in history"""
        self.decisions.append({
            'step': self.step_count,
            'action': str(action),
            'efe': efe_data['efe'],
            'pragmatic': efe_data['pragmatic'],
            'epistemic': efe_data['epistemic'],
            'cost': efe_data['cost'],
            'outcome_success': outcome.get('success', False),
            'survived': self.metabolic_engine.is_alive
        })
    
    def get_decision_summary(self, last_n: int = 10) -> List[Dict]:
        """Get summary of recent decisions"""
        return self.decisions[-last_n:]
    
    def __repr__(self):
        return (f"ActiveInferenceLoop(steps={self.step_count}, "
                f"alive={self.metabolic_engine.is_alive})")
