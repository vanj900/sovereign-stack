"""
Example: Trauma Dynamics Simulation

This script demonstrates the computational anatomy of trauma:
1. Pathological attractor basin (high-precision prior)
2. Chronic prediction errors (safe environment vs danger belief)
3. Allostatic load accumulation (metabolic cost)
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from precisionlocked.trauma_model import TraumaSimulator
from precisionlocked.visualization import plot_trauma_dynamics, print_summary


def main():
    """Run trauma dynamics simulation."""
    print("\n" + "="*70)
    print("TRAUMA AS PATHOLOGICAL PRECISION: A COMPUTATIONAL DEMONSTRATION")
    print("="*70 + "\n")
    
    print("Scenario: Individual with trauma-encoded 'Danger' prior")
    print("          living in objectively safe environment\n")
    
    # Initialize simulator
    simulator = TraumaSimulator(
        n_features=1,
        trauma_precision=100.0,  # Π_prior → ∞
        safe_environment_mean=1.0  # Positive = safe
    )
    
    print(f"Configuration:")
    print(f"  - Trauma prior: μ = -1.0 (Danger)")
    print(f"  - Prior precision: Π = {simulator.trauma_precision}")
    print(f"  - Environment: y = {simulator.safe_environment[0]} (Safe)")
    print(f"\nRunning simulation for 100 timesteps...\n")
    
    # Run simulation
    results = simulator.run_simulation(n_timesteps=100)
    
    # Print summary
    print_summary(results, "Trauma Dynamics Results")
    
    # Key observations
    print("KEY OBSERVATIONS:")
    print("-" * 60)
    print("1. PERSISTENT ERRORS: Despite safe environment, prediction")
    print("   errors remain high due to mismatch with trauma prior")
    print(f"   (Mean error: {np.mean(results['errors']):.3f})")
    print()
    print("2. METABOLIC EXHAUSTION: Chronic suppression of these errors")
    print("   creates sustained allostatic load")
    print(f"   (Cumulative load: {results['cumulative_load'][-1]:.2f} ATP)")
    print()
    print("3. FROZEN BELIEF: Internal model (μ) does not update")
    print("   System is trapped in attractor basin")
    print(f"   (All timesteps: trapped = {results['trapped'][0]})")
    print("-" * 60 + "\n")
    
    # Visualization
    try:
        print("Generating visualization...")
        fig = plot_trauma_dynamics(results, save_path="trauma_dynamics.png")
        if fig:
            print("✓ Saved: trauma_dynamics.png\n")
    except Exception as e:
        print(f"Could not generate plot: {e}\n")
    
    print("="*70)
    print("This demonstrates the Energetic Paradox:")
    print("  - Low uncertainty (rigid belief) → High metabolic cost")
    print("  - Mechanism: Continuous active suppression of prediction errors")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
