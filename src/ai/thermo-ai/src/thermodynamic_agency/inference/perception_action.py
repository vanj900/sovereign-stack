"""
Perception-Action Interface

Sensorimotor interface between the agent and environment.
"""

from typing import Dict, Any, List


class PerceptionActionInterface:
    """
    Handles sensing and acting in the environment.
    """
    
    def __init__(self):
        self.perception_history = []
        self.action_history = []
    
    def perceive(self, environment) -> Dict[str, Any]:
        """
        Sense the environment.
        
        Returns:
            Observations dictionary
        """
        observations = {
            'timestamp': len(self.perception_history),
            'resources': []
        }
        
        if hasattr(environment, 'get_visible_resources'):
            observations['resources'] = environment.get_visible_resources()
        
        if hasattr(environment, 'get_threats'):
            observations['threats'] = environment.get_threats()
        
        self.perception_history.append(observations)
        return observations
    
    def act(self, action, environment, metabolic_engine) -> Dict[str, Any]:
        """
        Execute action in environment.
        
        Returns:
            Result of action
        """
        result = {
            'action': str(action),
            'success': False
        }
        
        if hasattr(environment, 'execute_action'):
            result = environment.execute_action(action, metabolic_engine)
        
        self.action_history.append(result)
        return result
