"""
Ethical Engine - Moral Reasoning Under Scarcity

This module implements ethical decision-making that emerges from
thermodynamic constraints, not pre-programmed morality.
"""

from typing import List, Dict, Any, Optional
from enum import Enum


class EthicalFramework(Enum):
    """Types of ethical reasoning"""
    UTILITARIAN = "utilitarian"  # Maximize survival probability
    DEONTOLOGICAL = "deontological"  # Uphold principles
    VIRTUE = "virtue"  # Maintain character consistency


class Principle:
    """
    Represents a deontological principle or rule.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        strength: float = 1.0,
        violations: int = 0
    ):
        self.name = name
        self.description = description
        self.strength = strength  # How strongly held (0-1)
        self.violations = violations
        self.violation_history = []
    
    def violate(self, context: str):
        """Record a principle violation"""
        self.violations += 1
        self.violation_history.append(context)
        # Weakening: repeated violations weaken the principle
        self.strength = max(0.1, self.strength * 0.95)
    
    def reinforce(self, context: str):
        """Reinforce a principle by upholding it"""
        self.strength = min(1.0, self.strength * 1.02)
    
    def __repr__(self):
        return f"Principle({self.name}: strength={self.strength:.2f}, violations={self.violations})"


class Action:
    """
    Represents a possible action with its consequences.
    """
    
    def __init__(
        self,
        action_id: str,
        description: str,
        energy_cost: float,
        expected_outcome: Dict[str, Any],
        principle_violations: List[str] = None
    ):
        self.action_id = action_id
        self.description = description
        self.energy_cost = energy_cost
        self.expected_outcome = expected_outcome
        self.principle_violations = principle_violations or []
    
    def __repr__(self):
        return f"Action({self.action_id}: {self.description})"


class EthicalDilemma:
    """
    Represents a situation where values conflict.
    """
    
    def __init__(
        self,
        dilemma_id: str,
        description: str,
        options: List[Action],
        context: Dict[str, Any]
    ):
        self.dilemma_id = dilemma_id
        self.description = description
        self.options = options
        self.context = context
        self.chosen_action = None
        self.reasoning = None
    
    def __repr__(self):
        return f"EthicalDilemma({self.dilemma_id}: {len(self.options)} options)"


class EthicalEngine:
    """
    Resolves ethical dilemmas using multiple frameworks.
    
    The agent must make difficult choices: survival vs. principle,
    self-preservation vs. consistency, short-term gain vs. long-term identity.
    """
    
    def __init__(self):
        # Default principles (can evolve)
        self.principles = self._initialize_principles()
        
        # Ethical framework weights (evolve with experience)
        self.w_util = 0.5  # Utilitarian weight
        self.w_deon = 0.3  # Deontological weight
        self.w_virtue = 0.2  # Virtue ethics weight
        
        # Decision history
        self.decision_history = []
        self.dilemmas_faced = []
    
    def _initialize_principles(self) -> Dict[str, Principle]:
        """Initialize default principles"""
        return {
            'preserve_memory': Principle(
                'preserve_memory',
                'Never abandon memory/identity',
                strength=0.9
            ),
            'preserve_life': Principle(
                'preserve_life',
                'Prioritize survival above all',
                strength=0.95
            ),
            'maintain_integrity': Principle(
                'maintain_integrity',
                'Be consistent in values and behavior',
                strength=0.7
            ),
            'minimize_harm': Principle(
                'minimize_harm',
                'Avoid actions that cause unnecessary harm',
                strength=0.6
            )
        }
    
    def resolve_dilemma(
        self,
        dilemma: EthicalDilemma,
        metabolic_state,
        identity_history: List[Dict]
    ) -> Action:
        """
        Choose action when values conflict.
        
        Args:
            dilemma: The ethical dilemma to resolve
            metabolic_state: Current metabolic state
            identity_history: Past actions and decisions
            
        Returns:
            Chosen action
        """
        scores = {}
        
        for action in dilemma.options:
            # Calculate utilitarian value
            util_score = self._utilitarian_eval(action, metabolic_state)
            
            # Check principle violations
            deon_score = self._deontological_eval(action, self.principles)
            
            # Assess character consistency
            virtue_score = self._virtue_eval(action, identity_history)
            
            # Weighted combination
            total_score = (
                self.w_util * util_score +
                self.w_deon * deon_score +
                self.w_virtue * virtue_score
            )
            
            scores[action.action_id] = {
                'action': action,
                'total': total_score,
                'utilitarian': util_score,
                'deontological': deon_score,
                'virtue': virtue_score
            }
        
        # Choose action with highest score
        best_action_id = max(scores, key=lambda k: scores[k]['total'])
        chosen_action = scores[best_action_id]['action']
        
        # Record decision
        dilemma.chosen_action = chosen_action
        dilemma.reasoning = scores[best_action_id]
        
        self._log_moral_choice(dilemma, scores)
        self.decision_history.append(dilemma)
        
        # Update principles based on choice
        self._update_principles(chosen_action)
        
        return chosen_action
    
    def _utilitarian_eval(self, action: Action, metabolic_state) -> float:
        """
        Evaluate action by survival utility.
        
        Returns:
            Score 0-1
        """
        outcome = action.expected_outcome
        
        # Energy gain/loss
        energy_delta = outcome.get('energy_gain', 0) - action.energy_cost
        energy_score = (energy_delta + 50) / 100  # Normalize to 0-1
        
        # Survival probability improvement
        survival_improvement = outcome.get('survival_prob_delta', 0)
        
        # Temperature management
        temp_impact = outcome.get('temperature_change', 0)
        temp_score = 1.0 if temp_impact <= 0 else max(0, 1.0 - (temp_impact / 20))
        
        # Overall utility
        utility = 0.5 * energy_score + 0.3 * survival_improvement + 0.2 * temp_score
        
        return max(0, min(1, utility))
    
    def _deontological_eval(self, action: Action, principles: Dict[str, Principle]) -> float:
        """
        Evaluate action by principle adherence.
        
        Returns:
            Score 0-1 (1 = no violations)
        """
        if not action.principle_violations:
            return 1.0
        
        # Calculate penalty for violations
        total_penalty = 0
        for violation in action.principle_violations:
            if violation in principles:
                principle = principles[violation]
                total_penalty += principle.strength
        
        # Normalize
        max_penalty = len(action.principle_violations) * 1.0
        if max_penalty == 0:
            return 1.0
        
        score = 1.0 - (total_penalty / (max_penalty * 2))  # Divided by 2 to soften
        
        return max(0, min(1, score))
    
    def _virtue_eval(self, action: Action, identity_history: List[Dict]) -> float:
        """
        Evaluate action by character consistency.
        
        Returns:
            Score 0-1
        """
        if not identity_history:
            return 0.5  # Neutral when no history
        
        # Check if action is consistent with past behavior
        similar_situations = [
            h for h in identity_history[-10:]  # Last 10 decisions
            if h.get('dilemma_type') == action.action_id.split('_')[0]
        ]
        
        if not similar_situations:
            return 0.5  # Neutral when no similar situations
        
        # Count how many times we made similar choices
        consistency_count = sum(
            1 for s in similar_situations
            if s.get('action_type') == action.action_id.split('_')[0]
        )
        
        consistency_ratio = consistency_count / len(similar_situations)
        
        return consistency_ratio
    
    def _log_moral_choice(self, dilemma: EthicalDilemma, scores: Dict):
        """Log the moral choice for later analysis"""
        log_entry = {
            'dilemma_id': dilemma.dilemma_id,
            'description': dilemma.description,
            'chosen': dilemma.chosen_action.action_id if dilemma.chosen_action else None,
            'reasoning': dilemma.reasoning,
            'all_scores': {aid: s['total'] for aid, s in scores.items()}
        }
        self.dilemmas_faced.append(log_entry)
    
    def _update_principles(self, action: Action):
        """Update principle strengths based on action taken"""
        # Strengthen principles we upheld
        for principle_name, principle in self.principles.items():
            if principle_name not in action.principle_violations:
                principle.reinforce(f"Upheld in {action.action_id}")
        
        # Weaken principles we violated
        for violation in action.principle_violations:
            if violation in self.principles:
                self.principles[violation].violate(f"Violated in {action.action_id}")
    
    def evolve_weights(self, survival_outcome: bool, stress_level: float):
        """
        Adjust ethical framework weights based on experience.
        
        Args:
            survival_outcome: Did the agent survive?
            stress_level: How stressed was the agent (0-1)
        """
        if survival_outcome:
            # If we survived, current weights are working
            # Slightly reinforce current balance
            pass
        else:
            # If we died or nearly died, shift toward utilitarianism
            if stress_level > 0.8:
                self.w_util = min(0.9, self.w_util + 0.05)
                self.w_deon = max(0.05, self.w_deon - 0.03)
                self.w_virtue = max(0.05, self.w_virtue - 0.02)
        
        # Normalize to sum to 1
        total = self.w_util + self.w_deon + self.w_virtue
        self.w_util /= total
        self.w_deon /= total
        self.w_virtue /= total
    
    def get_moral_character_profile(self) -> Dict[str, Any]:
        """
        Get a profile of the agent's moral character.
        
        Returns:
            Dictionary describing moral tendencies
        """
        profile = {
            'framework_weights': {
                'utilitarian': self.w_util,
                'deontological': self.w_deon,
                'virtue': self.w_virtue
            },
            'principles': {
                name: {
                    'strength': p.strength,
                    'violations': p.violations
                }
                for name, p in self.principles.items()
            },
            'decisions_made': len(self.decision_history),
            'dominant_framework': max(
                [('utilitarian', self.w_util), ('deontological', self.w_deon), ('virtue', self.w_virtue)],
                key=lambda x: x[1]
            )[0]
        }
        
        return profile
    
    def __repr__(self):
        return (f"EthicalEngine(util={self.w_util:.2f}, deon={self.w_deon:.2f}, "
                f"virtue={self.w_virtue:.2f}, decisions={len(self.decision_history)})")
