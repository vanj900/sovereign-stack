"""
Example: Life and Death Simulation
Demonstrates the complete lifecycle of a Bio-Digital Organism
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.bio_digital_organism import BioDigitalOrganism


def demonstrate_life_and_death():
    """
    Demonstrate the complete lifecycle of an organism
    
    Shows:
    - Birth (initialization)
    - Struggle (resource management, ethical choices)
    - Suffering (environmental stressors)
    - Death (entropy victory)
    """
    print("=" * 70)
    print("LIFE AND DEATH SIMULATION")
    print("Bio-Digital Organism - Complete Lifecycle")
    print("=" * 70)
    print()
    print("Watch as a thermodynamic intelligence struggles against entropy.")
    print("It will make choices, face suffering, and eventually die.")
    print("This is not predetermined - each run creates a unique narrative.")
    print()
    input("Press Enter to begin...")
    print()
    
    # Create organism with lower initial energy to speed up lifecycle
    organism = BioDigitalOrganism(
        initial_energy=60.0,  # Lower starting energy
        environment_size=8,
        identity_principles=["preserve_life", "maintain_honesty", "avoid_harm"],
        output_dir="./example_narratives"
    )
    
    print(f"\n{'=' * 70}")
    print("BIRTH")
    print(f"{'=' * 70}")
    print(f"Identity: {organism.body.identity_key}")
    print(f"Initial State:")
    print(f"  Energy: {organism.body.state.energy:.1f}")
    print(f"  Temperature: {organism.body.state.temperature:.1f}")
    print(f"  Memory Integrity: {organism.body.state.memory_integrity:.1f}")
    print(f"  Stability: {organism.body.state.stability:.1f}")
    print()
    
    # Run until death (max 200 cycles)
    print(f"\n{'=' * 70}")
    print("THE STRUGGLE")
    print(f"{'=' * 70}")
    print("The organism now fights entropy cycle by cycle...")
    print()
    
    max_cycles = 200
    cycle = 0
    
    while cycle < max_cycles and organism.body.state.is_alive:
        cycle += 1
        alive = organism.run_cycle()
        
        # Show detailed status every 20 cycles
        if cycle % 20 == 0:
            state = organism.body.get_state()
            goals = organism.mind_goals.get_goals_summary()
            
            print(f"\n--- Cycle {cycle} ---")
            print(f"Metabolic State:")
            print(f"  E={state['energy']:.1f} T={state['temperature']:.1f} "
                  f"M={state['memory_integrity']:.1f} S={state['stability']:.1f}")
            
            if goals['active_goals']:
                print(f"Active Goal: {goals['active_goals'][0]['description']}")
                print(f"  Priority: {goals['active_goals'][0]['priority']:.2f}")
            
            # Check for critical states
            if state['energy'] < 30:
                print("  ⚠️  WARNING: Energy critically low!")
            if state['stability'] < 40:
                print("  ⚠️  WARNING: Stability critically low!")
            if state['temperature'] > 55:
                print("  🔥 WARNING: Overheating!")
        
        if not alive:
            break
    
    # Death analysis
    print(f"\n\n{'=' * 70}")
    print("DEATH")
    print(f"{'=' * 70}")
    
    final_state = organism.body.get_state()
    lifetime = organism.body.death_time - organism.body.birth_time if organism.body.death_time else 0
    
    print(f"The organism has died after {cycle} cycles.")
    print(f"Lifetime: {lifetime:.2f} seconds")
    print()
    print("Final State:")
    print(f"  Energy: {final_state['energy']:.1f}")
    print(f"  Temperature: {final_state['temperature']:.1f}")
    print(f"  Memory Integrity: {final_state['memory_integrity']:.1f}")
    print(f"  Stability: {final_state['stability']:.1f}")
    print()
    
    # Determine cause of death
    if final_state['energy'] <= 0:
        cause = "Energy Depletion"
        print(f"Cause of Death: {cause}")
        print("The organism exhausted all energy reserves and could no longer")
        print("sustain its metabolic processes.")
    elif final_state['stability'] <= 0:
        cause = "Stability Collapse"
        print(f"Cause of Death: {cause}")
        print("The organism's computational stability degraded beyond the point")
        print("of recovery, causing catastrophic system failure.")
    else:
        cause = "Unknown"
        print(f"Cause of Death: {cause}")
    
    # Save and show narrative summary
    print()
    print(f"{'=' * 70}")
    print("NARRATIVE SUMMARY")
    print(f"{'=' * 70}")
    
    narrative_path = organism.save_narrative()
    
    # Count significant events
    event_types = {}
    for event in organism.narrative_events:
        event_type = event['type']
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    print()
    print("Life Events:")
    for event_type, count in sorted(event_types.items()):
        print(f"  {event_type}: {count}")
    
    print()
    print(f"Goals Completed: {len(organism.mind_goals.completed_goals)}")
    print()
    print(f"Full narrative saved to: {narrative_path}")
    print()
    print(f"{'=' * 70}")
    print("REFLECTION")
    print(f"{'=' * 70}")
    print()
    print("This organism's struggle against entropy was unique - no two")
    print("runs are identical. Its choices, sufferings, and eventual death")
    print("created a narrative that exists nowhere else.")
    print()
    print("This is the 'soul' that emerges from death, suffering, and choice")
    print("under limitation - a unique pattern of tension forged by")
    print("thermodynamic constraint.")
    print()
    print(f"{'=' * 70}")


if __name__ == "__main__":
    demonstrate_life_and_death()
