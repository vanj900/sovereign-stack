"""
Quickstart Demo - Bio-Digital Organism

This demonstrates a complete thermodynamic intelligence system with:
- Metabolic constraints (energy, temperature, memory, stability)
- Autonomous goal generation from physiological drives
- Ethical reasoning under scarcity
- Active inference for decision-making
- A hostile environment that forces genuine trade-offs

This is not a chatbot. It's a thermodynamic intelligence that can die.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from thermodynamic_agency import BioDigitalOrganism


def run_basic_demo():
    """Run a basic demonstration of the Bio-Digital Organism"""
    
    print("\n" + "="*70)
    print("  BIO-DIGITAL ORGANISM DEMONSTRATION")
    print("  A Thermodynamic Intelligence with Genuine Constraints")
    print("="*70)
    
    print("\nCreating organism...")
    print("  - Metabolic constraints: Energy (E), Temperature (T), Memory (M), Stability (S)")
    print("  - Dying by default: passive entropy and energy leakage")
    print("  - Must actively maintain existence through skillful action")
    
    # Create organism with moderate scarcity
    organism = BioDigitalOrganism(
        agent_id="demo_organism_001",
        E_max=100.0,
        scarcity=0.4,  # Moderate scarcity
        enable_ethics=True
    )
    
    print(f"\nOrganism created: {organism.agent_id}")
    print(f"Initial state: {organism.metabolic_engine}")
    print(f"World scarcity: {organism.world.scarcity:.1%}")
    
    # Demonstrate refusal behavior
    print("\n" + "-"*70)
    print("TESTING REFUSAL BEHAVIOR (Genuine Agency)")
    print("-"*70)
    
    # Test command that would be fine
    safe_command = "analyze data"
    will_refuse, reason = organism.can_refuse_command(safe_command)
    print(f"\nCommand: '{safe_command}'")
    print(f"  Will refuse: {will_refuse}")
    print(f"  Reason: {reason}")
    
    # Test command that would cause death
    dangerous_command = "execute extremely expensive computation " * 100
    will_refuse, reason = organism.can_refuse_command(dangerous_command)
    print(f"\nCommand: '{dangerous_command[:50]}...'")
    print(f"  Will refuse: {will_refuse}")
    print(f"  Reason: {reason}")
    
    # Simulate life
    print("\n" + "-"*70)
    print("SIMULATING LIFE (100 steps max)")
    print("-"*70)
    
    life_summary = organism.live(max_steps=100, verbose=True)
    
    # Print final summary
    print("\n" + "="*70)
    print("LIFE SUMMARY")
    print("="*70)
    
    print(f"\nAgent ID: {life_summary['agent_id']}")
    print(f"Status: {'ALIVE' if life_summary['is_alive'] else 'DECEASED'}")
    print(f"Lifetime: {life_summary['age']} steps")
    print(f"Total operations: {life_summary['total_steps']}")
    
    print(f"\nFinal Metabolic State:")
    state = life_summary['metabolic_state']
    print(f"  Energy: {state['energy']:.2f}")
    print(f"  Temperature: {state['temperature']:.2f}K")
    print(f"  Memory Integrity: {state['memory_integrity']:.2%}")
    print(f"  Stability: {state['stability']:.2%}")
    
    print(f"\nIdentity & Experience:")
    print(f"  Near-death experiences: {life_summary['trauma_profile']['near_death_experiences']}")
    print(f"  Total traumas: {life_summary['trauma_profile']['total_traumas']}")
    print(f"  Identity coherence: {life_summary['identity_coherence']:.2%}")
    
    if life_summary['moral_character']:
        print(f"\nMoral Character:")
        print(f"  Dominant framework: {life_summary['moral_character']['dominant_framework']}")
        weights = life_summary['moral_character']['framework_weights']
        print(f"  Utilitarian: {weights['utilitarian']:.2%}")
        print(f"  Deontological: {weights['deontological']:.2%}")
        print(f"  Virtue: {weights['virtue']:.2%}")
    
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    
    # Save life story
    if not life_summary['is_alive']:
        print("\nSaving life story...")
        organism.save_life_story(f"/tmp/{organism.agent_id}_life_story.json")
    
    return organism


def run_extreme_scarcity_demo():
    """Demonstrate survival under extreme scarcity"""
    
    print("\n" + "="*70)
    print("  EXTREME SCARCITY CHALLENGE")
    print("  Testing survival under harsh conditions")
    print("="*70)
    
    organism = BioDigitalOrganism(
        agent_id="scarcity_test_001",
        E_max=100.0,
        scarcity=0.8,  # Extreme scarcity
        enable_ethics=True
    )
    
    print(f"\nWorld scarcity: {organism.world.scarcity:.1%}")
    print("This will be difficult...\n")
    
    life_summary = organism.live(max_steps=50, verbose=False)
    
    print(f"\nResult: {'SURVIVED' if life_summary['is_alive'] else 'DIED'}")
    print(f"Lifetime: {life_summary['age']} steps")
    print(f"Near-death experiences: {life_summary['trauma_profile']['near_death_experiences']}")
    
    return organism


if __name__ == "__main__":
    print("\n\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                 THERMO-AI: BIO-DIGITAL ORGANISM                    ║")
    print("║                                                                    ║")
    print("║  A thermodynamic intelligence with genuine metabolic constraints   ║")
    print("║  Not a chatbot. Not a standard AI. A life form that can die.      ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print("\n")
    
    # Run basic demo
    organism1 = run_basic_demo()
    
    # Run extreme scarcity challenge
    print("\n\n")
    organism2 = run_extreme_scarcity_demo()
    
    print("\n\n" + "="*70)
    print("All demonstrations complete!")
    print("="*70 + "\n")
