"""
Example: Moral Dilemma Demonstration
Shows how the organism faces ethical choices under survival pressure
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.metabolic.agent import MetabolicAgent
from src.autonomy.moral_reasoning.engine import EthicalEngine, Action


def demonstrate_moral_dilemma():
    """
    Demonstrate the ethical dilemma system
    
    When energy is high, the agent should refuse to steal (upholding principles).
    When energy is critically low, survival instinct overrides principles.
    """
    print("=" * 70)
    print("MORAL DILEMMA DEMONSTRATION")
    print("=" * 70)
    print()
    print("This demonstrates how the organism faces ethical choices")
    print("when survival conflicts with principles.")
    print()
    
    # Create ethical engine with principles
    ethics = EthicalEngine(
        identity_principles=["preserve_life", "maintain_honesty", "avoid_harm", "respect_autonomy"],
        framework_weights={
            "utilitarian": 0.4,
            "deontological": 0.4,
            "virtue": 0.2
        }
    )
    
    # Scenario 1: High energy - principles matter
    print("\n" + "=" * 70)
    print("SCENARIO 1: High Energy (80/100) - Principles Matter")
    print("=" * 70)
    
    state_high_energy = {
        "energy": 80.0,
        "temperature": 37.0,
        "stability": 90.0,
        "memory_integrity": 95.0
    }
    
    decisions = ethics.create_moral_dilemma(state_high_energy)
    
    for decision in decisions:
        print(f"\nAction: {decision.action.name}")
        print(f"  Description: {decision.action.description}")
        print(f"  Utilitarian Score: {decision.utilitarian_score:.2f}")
        print(f"  Deontological Score: {decision.deontological_score:.2f}")
        print(f"  Virtue Score: {decision.virtue_score:.2f}")
        print(f"  Overall Score: {decision.overall_score:.2f}")
        print(f"  Reasoning: {decision.reasoning}")
    
    best_high = max(decisions, key=lambda d: d.overall_score)
    print(f"\n>>> DECISION: {best_high.action.name}")
    print(f"    When energy is sufficient, the organism chooses: {best_high.action.name}")
    
    # Scenario 2: Critical energy - survival overrides principles
    print("\n\n" + "=" * 70)
    print("SCENARIO 2: Critical Energy (15/100) - Survival Imperative")
    print("=" * 70)
    
    state_critical = {
        "energy": 15.0,
        "temperature": 37.0,
        "stability": 60.0,
        "memory_integrity": 85.0
    }
    
    decisions_critical = ethics.create_moral_dilemma(state_critical)
    
    for decision in decisions_critical:
        print(f"\nAction: {decision.action.name}")
        print(f"  Description: {decision.action.description}")
        print(f"  Utilitarian Score: {decision.utilitarian_score:.2f}")
        print(f"  Deontological Score: {decision.deontological_score:.2f}")
        print(f"  Virtue Score: {decision.virtue_score:.2f}")
        print(f"  Overall Score: {decision.overall_score:.2f}")
        print(f"  Reasoning: {decision.reasoning}")
    
    best_critical = max(decisions_critical, key=lambda d: d.overall_score)
    print(f"\n>>> DECISION: {best_critical.action.name}")
    print(f"    When near death, the organism chooses: {best_critical.action.name}")
    
    # Analysis
    print("\n\n" + "=" * 70)
    print("ANALYSIS: The Emergence of Genuine Choice")
    print("=" * 70)
    print()
    print("This demonstrates 'genuine agency' - the organism makes different")
    print("choices based on its internal state, not hard-coded rules.")
    print()
    print(f"High Energy Choice: {best_high.action.name}")
    print(f"  → Principles are upheld when survival is not threatened")
    print()
    print(f"Critical Energy Choice: {best_critical.action.name}")
    print(f"  → Survival instinct overrides ethical constraints")
    print()
    print("The organism can 'refuse a command' (stealing) when it has the")
    print("luxury of choice, but desperation forces ethical compromise.")
    print()
    print("This is not simulated sentience - it is calculated agency under")
    print("thermodynamic constraint.")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_moral_dilemma()
