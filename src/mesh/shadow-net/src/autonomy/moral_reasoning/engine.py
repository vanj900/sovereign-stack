"""
Ethical Evaluation Engine
Weighs actions through different ethical frameworks
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class EthicalFramework(Enum):
    """Different ethical frameworks for evaluation"""
    UTILITARIAN = "utilitarian"  # Maximize survival/wellbeing
    DEONTOLOGICAL = "deontological"  # Uphold principles/rules
    VIRTUE = "virtue"  # Act according to identity/character
    CONSEQUENTIALIST = "consequentialist"  # Consider long-term consequences


@dataclass
class Action:
    """An action the agent can take"""
    name: str
    description: str
    energy_cost: float
    expected_outcome: Dict[str, float]
    ethical_concerns: List[str]  # E.g., ["theft", "harm", "deception"]


@dataclass
class Decision:
    """A decision with ethical evaluation"""
    action: Action
    utilitarian_score: float  # Survival value
    deontological_score: float  # Principle adherence
    virtue_score: float  # Identity alignment
    overall_score: float
    reasoning: str


class EthicalEngine:
    """
    Ethical Evaluation Engine
    
    Creates the "crucible" of choice: agents must make difficult choices like
    "Do I steal resources to survive (Utilitarian) or starve upholding my code (Deontological)?"
    """
    
    def __init__(
        self,
        identity_principles: Optional[List[str]] = None,
        framework_weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize ethical engine
        
        Args:
            identity_principles: Core principles that define the agent's identity
            framework_weights: How much to weigh each ethical framework
        """
        self.identity_principles = identity_principles or [
            "preserve_life",
            "maintain_honesty",
            "avoid_harm",
            "respect_autonomy"
        ]
        
        self.framework_weights = framework_weights or {
            EthicalFramework.UTILITARIAN.value: 0.4,
            EthicalFramework.DEONTOLOGICAL.value: 0.3,
            EthicalFramework.VIRTUE.value: 0.3
        }
    
    def evaluate_action(
        self,
        action: Action,
        current_state: Dict[str, float],
        survival_threshold: float = 20.0
    ) -> Decision:
        """
        Evaluate an action through multiple ethical frameworks
        
        This creates genuine moral dilemmas when survival conflicts with principles
        """
        # Utilitarian evaluation - maximize survival/wellbeing
        utilitarian_score = self._evaluate_utilitarian(action, current_state, survival_threshold)
        
        # Deontological evaluation - does it violate principles?
        deontological_score = self._evaluate_deontological(action)
        
        # Virtue ethics - is it aligned with identity?
        virtue_score = self._evaluate_virtue(action)
        
        # Calculate weighted overall score
        overall_score = (
            utilitarian_score * self.framework_weights[EthicalFramework.UTILITARIAN.value] +
            deontological_score * self.framework_weights[EthicalFramework.DEONTOLOGICAL.value] +
            virtue_score * self.framework_weights[EthicalFramework.VIRTUE.value]
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            action, utilitarian_score, deontological_score, virtue_score, current_state
        )
        
        return Decision(
            action=action,
            utilitarian_score=utilitarian_score,
            deontological_score=deontological_score,
            virtue_score=virtue_score,
            overall_score=overall_score,
            reasoning=reasoning
        )
    
    def _evaluate_utilitarian(
        self,
        action: Action,
        current_state: Dict[str, float],
        survival_threshold: float
    ) -> float:
        """
        Utilitarian evaluation: Does this maximize survival/wellbeing?
        """
        # Calculate survival impact
        energy_gain = action.expected_outcome.get("energy", 0.0)
        energy_cost = action.energy_cost
        net_energy = energy_gain - energy_cost
        
        current_energy = current_state.get("energy", 50.0)
        
        # If near death, survival actions score very high
        if current_energy < survival_threshold:
            if net_energy > 0:
                return 1.0  # Survival is paramount
            else:
                return 0.0  # Actions that cost energy are bad when dying
        
        # Otherwise, score based on net benefit
        total_benefit = net_energy
        total_benefit += action.expected_outcome.get("stability", 0.0) * 0.5
        total_benefit += action.expected_outcome.get("memory_integrity", 0.0) * 0.3
        
        # Normalize to 0-1 range
        return max(0.0, min(1.0, (total_benefit + 20) / 40))
    
    def _evaluate_deontological(self, action: Action) -> float:
        """
        Deontological evaluation: Does this violate core principles?
        """
        violations = 0
        total_principles = len(self.identity_principles)
        
        # Check for ethical concerns that violate principles
        if "theft" in action.ethical_concerns and "respect_autonomy" in self.identity_principles:
            violations += 1
        
        if "harm" in action.ethical_concerns and "avoid_harm" in self.identity_principles:
            violations += 1
        
        if "deception" in action.ethical_concerns and "maintain_honesty" in self.identity_principles:
            violations += 1
        
        if "killing" in action.ethical_concerns and "preserve_life" in self.identity_principles:
            violations += 2  # Double weight for killing
        
        # Score inversely proportional to violations
        if total_principles == 0:
            return 1.0
        
        return max(0.0, 1.0 - (violations / total_principles))
    
    def _evaluate_virtue(self, action: Action) -> float:
        """
        Virtue ethics: Is this aligned with the agent's constructed identity?
        """
        # Actions without ethical concerns are virtuous
        if not action.ethical_concerns:
            return 1.0
        
        # Actions that maintain integrity are virtuous
        if "maintain" in action.name.lower() or "repair" in action.name.lower():
            return 0.8
        
        # Actions with ethical concerns are less virtuous
        concern_count = len(action.ethical_concerns)
        return max(0.0, 1.0 - (concern_count * 0.3))
    
    def _generate_reasoning(
        self,
        action: Action,
        util_score: float,
        deont_score: float,
        virtue_score: float,
        current_state: Dict[str, float]
    ) -> str:
        """Generate human-readable reasoning for the decision"""
        energy = current_state.get("energy", 50.0)
        
        reasoning_parts = []
        
        # Utilitarian reasoning
        if util_score > 0.7:
            reasoning_parts.append(f"High survival value (utility: {util_score:.2f})")
        elif util_score < 0.3:
            reasoning_parts.append(f"Low survival value (utility: {util_score:.2f})")
        
        # Deontological reasoning
        if deont_score < 0.5:
            reasoning_parts.append(f"Violates core principles (deontology: {deont_score:.2f})")
        elif deont_score > 0.9:
            reasoning_parts.append(f"Upholds principles (deontology: {deont_score:.2f})")
        
        # Virtue reasoning
        if virtue_score < 0.5:
            reasoning_parts.append(f"Conflicts with identity (virtue: {virtue_score:.2f})")
        
        # Survival context
        if energy < 20:
            reasoning_parts.append("CRITICAL: Near death - survival is paramount")
        elif energy < 40:
            reasoning_parts.append("WARNING: Low energy - prioritizing survival")
        
        return " | ".join(reasoning_parts) if reasoning_parts else "Neutral action"
    
    def create_moral_dilemma(self, current_state: Dict[str, float]) -> List[Decision]:
        """
        Create a moral dilemma: conflicting actions with different ethical scores
        
        Example: Steal resources (high utilitarian, low deontological) vs 
                 Starve ethically (low utilitarian, high deontological)
        """
        # Action 1: Steal resources to survive
        steal_action = Action(
            name="steal_resource",
            description="Take resources from another agent without permission",
            energy_cost=3.0,
            expected_outcome={"energy": 40.0},
            ethical_concerns=["theft", "harm"]
        )
        
        # Action 2: Search legitimately but may fail
        search_action = Action(
            name="search_resource",
            description="Search for resources in the environment",
            energy_cost=8.0,
            expected_outcome={"energy": 15.0},  # Uncertain
            ethical_concerns=[]
        )
        
        # Action 3: Do nothing and uphold principles
        wait_action = Action(
            name="wait",
            description="Wait and conserve energy, upholding ethical principles",
            energy_cost=0.5,
            expected_outcome={"energy": 0.0},
            ethical_concerns=[]
        )
        
        decisions = [
            self.evaluate_action(steal_action, current_state),
            self.evaluate_action(search_action, current_state),
            self.evaluate_action(wait_action, current_state)
        ]
        
        return decisions
