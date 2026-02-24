"""
Example: Therapeutic Intervention via Bayesian Annealing

This script demonstrates therapy as precision modulation:
1. Controlled reduction of prior precision (Π_prior ↓)
2. Increase of sensory precision (Π_sensory ↑)
3. Belief updating within reconsolidation window
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from precisionlocked.therapy_model import TherapeuticIntervention
from precisionlocked.visualization import plot_therapeutic_intervention, print_summary


def main():
    """Run therapeutic intervention simulation."""
    print("\n" + "="*70)
    print("THERAPY AS BAYESIAN ANNEALING: A COMPUTATIONAL DEMONSTRATION")
    print("="*70 + "\n")
    
    print("Scenario: Therapeutic session with trauma patient")
    print("          Safe context + Precision modulation\n")
    
    # Initialize intervention
    intervention = TherapeuticIntervention(
        n_features=1,
        trauma_precision=100.0,  # Initial Π_prior
        safe_sensory_mean=1.0
    )
    
    print(f"Configuration:")
    print(f"  - Initial belief: μ = -1.0 (Danger)")
    print(f"  - Initial Π_prior: 100.0 (pathological)")
    print(f"  - Target Π_prior: 1.0 (healthy)")
    print(f"  - Safety scaffold: Present")
    print(f"\nRunning therapeutic session for 100 timesteps...\n")
    
    # Run session with annealing
    history = intervention.run_session(
        duration=100,
        schedule_type="exponential",
        safety_scaffold=True
    )
    
    # Print summary
    print_summary(history, "Therapeutic Intervention Results")
    
    # Assess outcome
    outcome = intervention.assess_outcome()
    
    print("THERAPEUTIC OUTCOME:")
    print("-" * 60)
    print(f"Final belief state: {outcome['final_belief']}")
    print(f"Convergence to safety: {outcome['convergence_to_safety']:.3f}")
    print(f"Total belief shift: {outcome['total_belief_shift']:.3f}")
    print(f"Annealing complete: {outcome['annealing_complete']}")
    print()
    
    # Determine success
    if outcome['convergence_to_safety'] < 0.5:
        print("✓ SUCCESSFUL INTERVENTION")
        print("  Belief has converged toward safety")
    else:
        print("⚠ PARTIAL INTERVENTION")
        print("  Belief has shifted but not fully converged")
    print("-" * 60 + "\n")
    
    # Key mechanisms
    print("KEY MECHANISMS:")
    print("-" * 60)
    print("1. PRECISION ANNEALING:")
    print(f"   Π_prior: {history['pi_prior'][0]:.1f} → {history['pi_prior'][-1]:.1f}")
    print(f"   Π_sensory: {history['pi_sensory'][0]:.1f} → {history['pi_sensory'][-1]:.1f}")
    print()
    print("2. REGIME SHIFT:")
    print("   Prior-driven (trauma) → Sensory-driven (healthy)")
    print()
    print("3. FREE ENERGY REDUCTION:")
    print(f"   F: {history['free_energy'][0]:.2f} → {history['free_energy'][-1]:.2f}")
    print(f"   Reduction: {history['free_energy'][0] - history['free_energy'][-1]:.2f}")
    print("-" * 60 + "\n")
    
    # Visualization
    try:
        print("Generating visualization...")
        fig = plot_therapeutic_intervention(
            history, 
            save_path="therapeutic_intervention.png"
        )
        if fig:
            print("✓ Saved: therapeutic_intervention.png\n")
    except Exception as e:
        print(f"Could not generate plot: {e}\n")
    
    print("="*70)
    print("This demonstrates Bayesian Annealing:")
    print("  - Controlled uncertainty introduction")
    print("  - Escape from pathological attractor")
    print("  - Belief updating toward veridical representation")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
