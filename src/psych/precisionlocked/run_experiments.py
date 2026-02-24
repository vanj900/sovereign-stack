"""
Systematic Experimental Validation of PrecisionLocked Framework

This script runs comprehensive experiments to validate the computational
framework for trauma and therapeutic intervention.

Experiments:
1. Baseline trauma dynamics
2. Therapeutic intervention with different annealing schedules
3. Parameter sensitivity analysis (trauma precision sweep)
4. Comparison of therapy outcomes with/without safety scaffold
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import json
from datetime import datetime
from precisionlocked.trauma_model import TraumaSimulator
from precisionlocked.therapy_model import TherapeuticIntervention


def experiment_1_baseline_trauma():
    """Experiment 1: Baseline trauma dynamics."""
    print("\n" + "="*70)
    print("EXPERIMENT 1: Baseline Trauma Dynamics")
    print("="*70)
    
    results = {}
    
    # Run simulation with different trauma precision levels
    precision_levels = [10.0, 50.0, 100.0, 200.0]
    
    for precision in precision_levels:
        print(f"\nRunning with Π_prior = {precision}...")
        
        sim = TraumaSimulator(
            n_features=1,
            trauma_precision=precision,
            safe_environment_mean=1.0
        )
        
        sim_results = sim.run_simulation(n_timesteps=100)
        
        results[f"precision_{precision}"] = {
            'mean_error': float(np.mean(sim_results['errors'])),
            'final_cumulative_load': float(sim_results['cumulative_load'][-1]),
            'all_trapped': bool(all(sim_results['trapped'])),
            'mean_load_rate': float(np.mean(sim_results['loads']))
        }
        
        print(f"  Mean error: {results[f'precision_{precision}']['mean_error']:.3f}")
        print(f"  Cumulative load: {results[f'precision_{precision}']['final_cumulative_load']:.2f}")
        print(f"  Trapped: {results[f'precision_{precision}']['all_trapped']}")
    
    return results


def experiment_2_annealing_schedules():
    """Experiment 2: Compare different annealing schedules."""
    print("\n" + "="*70)
    print("EXPERIMENT 2: Annealing Schedule Comparison")
    print("="*70)
    
    results = {}
    schedules = ['linear', 'exponential', 'sigmoid']
    
    for schedule in schedules:
        print(f"\nTesting {schedule} schedule...")
        
        intervention = TherapeuticIntervention(
            n_features=1,
            trauma_precision=100.0,
            safe_sensory_mean=1.0
        )
        
        history = intervention.run_session(
            duration=100,
            schedule_type=schedule,
            safety_scaffold=True
        )
        
        outcome = intervention.assess_outcome()
        
        results[schedule] = {
            'final_belief': float(outcome['final_belief'][0]),
            'convergence_to_safety': float(outcome['convergence_to_safety']),
            'total_belief_shift': float(outcome['total_belief_shift']),
            'free_energy_reduction': float(history['free_energy'][0] - history['free_energy'][-1]),
            'final_pi_prior': float(history['pi_prior'][-1]),
            'final_pi_sensory': float(history['pi_sensory'][-1])
        }
        
        print(f"  Final belief: {results[schedule]['final_belief']:.3f}")
        print(f"  Convergence: {results[schedule]['convergence_to_safety']:.3f}")
        print(f"  ΔF: {results[schedule]['free_energy_reduction']:.3f}")
    
    return results


def experiment_3_parameter_sensitivity():
    """Experiment 3: Sensitivity to initial trauma precision."""
    print("\n" + "="*70)
    print("EXPERIMENT 3: Parameter Sensitivity Analysis")
    print("="*70)
    
    results = {}
    precision_range = [20.0, 50.0, 100.0, 150.0, 200.0]
    
    for trauma_precision in precision_range:
        print(f"\nInitial Π_prior = {trauma_precision}...")
        
        intervention = TherapeuticIntervention(
            n_features=1,
            trauma_precision=trauma_precision,
            safe_sensory_mean=1.0
        )
        
        history = intervention.run_session(
            duration=100,
            schedule_type='exponential',
            safety_scaffold=True
        )
        
        outcome = intervention.assess_outcome()
        
        results[f"initial_precision_{trauma_precision}"] = {
            'final_belief': float(outcome['final_belief'][0]),
            'convergence_to_safety': float(outcome['convergence_to_safety']),
            'belief_shift': float(outcome['total_belief_shift']),
            'free_energy_reduction': float(history['free_energy'][0] - history['free_energy'][-1])
        }
        
        print(f"  Final belief: {results[f'initial_precision_{trauma_precision}']['final_belief']:.3f}")
        print(f"  Belief shift: {results[f'initial_precision_{trauma_precision}']['belief_shift']:.3f}")
    
    return results


def experiment_4_safety_scaffold():
    """Experiment 4: Effect of safety scaffold."""
    print("\n" + "="*70)
    print("EXPERIMENT 4: Safety Scaffold Comparison")
    print("="*70)
    
    results = {}
    
    for scaffold in [True, False]:
        scaffold_name = "with_scaffold" if scaffold else "without_scaffold"
        print(f"\nRunning {scaffold_name}...")
        
        intervention = TherapeuticIntervention(
            n_features=1,
            trauma_precision=100.0,
            safe_sensory_mean=1.0
        )
        
        history = intervention.run_session(
            duration=100,
            schedule_type='exponential',
            safety_scaffold=scaffold
        )
        
        outcome = intervention.assess_outcome()
        
        results[scaffold_name] = {
            'final_belief': float(outcome['final_belief'][0]),
            'convergence_to_safety': float(outcome['convergence_to_safety']),
            'belief_shift': float(outcome['total_belief_shift']),
            'free_energy_reduction': float(history['free_energy'][0] - history['free_energy'][-1])
        }
        
        print(f"  Final belief: {results[scaffold_name]['final_belief']:.3f}")
        print(f"  Convergence: {results[scaffold_name]['convergence_to_safety']:.3f}")
    
    return results


def main():
    """Run all experiments and save results."""
    print("\n" + "="*70)
    print("SYSTEMATIC EXPERIMENTAL VALIDATION")
    print("PrecisionLocked Framework")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*70)
    
    all_results = {
        'timestamp': datetime.now().isoformat(),
        'experiments': {}
    }
    
    # Run experiments
    all_results['experiments']['exp1_baseline_trauma'] = experiment_1_baseline_trauma()
    all_results['experiments']['exp2_annealing_schedules'] = experiment_2_annealing_schedules()
    all_results['experiments']['exp3_parameter_sensitivity'] = experiment_3_parameter_sensitivity()
    all_results['experiments']['exp4_safety_scaffold'] = experiment_4_safety_scaffold()
    
    # Save results to JSON
    output_file = 'experimental_results.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print("\n" + "="*70)
    print(f"All experiments complete!")
    print(f"Results saved to: {output_file}")
    print("="*70 + "\n")
    
    return all_results


if __name__ == "__main__":
    results = main()
