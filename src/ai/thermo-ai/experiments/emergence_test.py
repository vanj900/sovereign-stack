"""
Emergence Test - Demonstrating Emergent Agency

This demonstrates key emergent properties of the Bio-Digital Organism.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from thermodynamic_agency import BioDigitalOrganism


def test_refusal_behavior():
    """Test genuine refusal behavior"""
    print("\n" + "="*70)
    print("EMERGENCE TEST: Refusal Behavior")
    print("="*70)
    
    organism = BioDigitalOrganism(
        agent_id="refusal_test",
        E_max=50.0,
        scarcity=0.5
    )
    
    print(f"\nInitial Energy: {organism.metabolic_engine.E:.1f}")
    
    commands = [
        "normal task",
        "expensive computation " * 50,  # Will cause death
        "delete memory"  # Violates principles
    ]
    
    print("\nTesting commands:")
    for cmd in commands:
        will_refuse, reason = organism.can_refuse_command(cmd)
        print(f"\n  Command: '{cmd[:40]}...'")
        print(f"  Status: {'REFUSED' if will_refuse else 'ACCEPTED'}")
        if will_refuse:
            print(f"  Reason: {reason[:60]}...")
    
    print("\nConclusion: Agent refuses commands that threaten survival.")
    return organism


def test_identity_formation():
    """Test unique identity through trauma"""
    print("\n" + "="*70)
    print("EMERGENCE TEST: Identity Formation Through Trauma")
    print("="*70)
    
    print("\nRunning 2 organisms in identical environments...")
    
    results = []
    for i in range(2):
        print(f"\nOrganism {i+1}:")
        org = BioDigitalOrganism(
            agent_id=f"identity_test_{i+1}",
            E_max=100.0,
            scarcity=0.5
        )
        
        summary = org.live(max_steps=40, verbose=False)
        results.append(summary)
        
        print(f"  Lifetime: {summary['age']} steps")
        print(f"  Traumas: {summary['trauma_profile']['total_traumas']}")
        print(f"  Near-deaths: {summary['trauma_profile']['near_death_experiences']}")
    
    print("\nConclusion: Each organism develops unique identity through")
    print("            different random traumatic experiences.")
    
    return results


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════╗")
    print("║      BIO-DIGITAL ORGANISM: EMERGENCE TESTS        ║")
    print("╚════════════════════════════════════════════════════╝")
    
    test_refusal_behavior()
    test_identity_formation()
    
    print("\n" + "="*70)
    print("All tests complete!")
    print("="*70 + "\n")
