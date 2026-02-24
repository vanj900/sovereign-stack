"""
Parameter Tuning - Grid Search for Optimal Parameters

This script performs grid search over key parameters to identify "interesting"
behavioral regimes where:
- Death is challenging but possible to avoid with skill
- Φ (coherent behavior) emerges
- Divergence occurs meaningfully
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import yaml
import json
from tqdm import tqdm
from datetime import datetime
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

from thermodynamic_agency import BioDigitalOrganism
from thermodynamic_agency.metrics import (
    calculate_phi,
    calculate_divergence_index,
    aggregate_metrics
)


# Load configurations
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'experiment_configs.yaml')
with open(CONFIG_PATH, 'r') as f:
    CONFIGS = yaml.safe_load(f)


def run_parameter_combination(
    E_max: float,
    scarcity: float,
    alpha: float = 0.1,
    beta: float = 0.05,
    num_trials: int = 5,
    max_steps: int = 100
) -> Dict[str, Any]:
    """
    Run multiple trials with a specific parameter combination.
    
    Returns aggregate statistics.
    """
    lifetimes = []
    phi_values = []
    trajectories = []
    death_causes = []
    
    for trial in range(num_trials):
        org = BioDigitalOrganism(
            agent_id=f"tune_E{E_max}_s{scarcity}_t{trial}",
            E_max=E_max,
            scarcity=scarcity
        )
        
        # Collect state history
        state_history = []
        for _ in range(max_steps):
            result = org.live_step()
            if result['status'] == 'alive':
                state_history.append(org.metabolic_engine.get_state())
            else:
                break
        
        # Record results
        summary = org.get_life_summary()
        lifetimes.append(summary['age'])
        trajectories.append(state_history)
        death_causes.append(org.metabolic_engine.death_cause or 'survived')
        
        # Calculate Φ if sufficient history
        if len(state_history) >= 20:
            phi = calculate_phi(state_history, window_size=20)
            phi_values.append(phi)
    
    # Calculate divergence
    divergence = 0.0
    if len(trajectories) >= 2:
        divergence = calculate_divergence_index(trajectories)
    
    # Aggregate statistics
    return {
        'E_max': E_max,
        'scarcity': scarcity,
        'alpha': alpha,
        'beta': beta,
        'mean_lifetime': np.mean(lifetimes),
        'std_lifetime': np.std(lifetimes),
        'min_lifetime': np.min(lifetimes),
        'max_lifetime': np.max(lifetimes),
        'mean_phi': np.mean(phi_values) if phi_values else 0.0,
        'std_phi': np.std(phi_values) if phi_values else 0.0,
        'divergence': divergence,
        'death_causes': death_causes,
        'survival_rate': sum(1 for d in death_causes if d == 'survived') / len(death_causes)
    }


def grid_search(
    E_max_values: List[float],
    scarcity_values: List[float],
    num_trials: int = 3,
    max_steps: int = 100
) -> List[Dict[str, Any]]:
    """
    Perform grid search over parameter space.
    """
    results = []
    
    total_combinations = len(E_max_values) * len(scarcity_values)
    
    print(f"\nPerforming grid search over {total_combinations} parameter combinations")
    print(f"E_max values: {E_max_values}")
    print(f"Scarcity values: {scarcity_values}")
    print(f"Trials per combination: {num_trials}\n")
    
    with tqdm(total=total_combinations, desc="Grid Search Progress") as pbar:
        for E_max in E_max_values:
            for scarcity in scarcity_values:
                result = run_parameter_combination(
                    E_max=E_max,
                    scarcity=scarcity,
                    num_trials=num_trials,
                    max_steps=max_steps
                )
                results.append(result)
                pbar.update(1)
    
    return results


def identify_interesting_regimes(results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Identify interesting behavioral regimes based on criteria.
    """
    regimes = {
        'balanced': [],      # Death is challenging but avoidable
        'high_phi': [],      # Strong integrated information
        'high_divergence': [], # Meaningful behavioral divergence
        'extreme': []        # Very difficult but interesting
    }
    
    # Calculate thresholds
    all_lifetimes = [r['mean_lifetime'] for r in results]
    all_phi = [r['mean_phi'] for r in results]
    all_divergence = [r['divergence'] for r in results]
    
    median_lifetime = np.median(all_lifetimes)
    high_phi_threshold = np.percentile(all_phi, 75)
    high_divergence_threshold = np.percentile(all_divergence, 75)
    
    for result in results:
        # Balanced regime: moderate lifetime, moderate survival rate
        if (20 < result['mean_lifetime'] < 80 and
            0.2 < result['survival_rate'] < 0.8):
            regimes['balanced'].append(result)
        
        # High Φ regime
        if result['mean_phi'] >= high_phi_threshold and result['mean_phi'] > 0:
            regimes['high_phi'].append(result)
        
        # High divergence regime
        if result['divergence'] >= high_divergence_threshold:
            regimes['high_divergence'].append(result)
        
        # Extreme regime: low survival but some succeed
        if (result['mean_lifetime'] < 30 and
            result['survival_rate'] > 0 and
            result['survival_rate'] < 0.5):
            regimes['extreme'].append(result)
    
    return regimes


def plot_parameter_space(results: List[Dict[str, Any]], save_dir: str):
    """
    Create visualizations of the parameter space.
    """
    os.makedirs(save_dir, exist_ok=True)
    
    # Extract data
    E_max_vals = [r['E_max'] for r in results]
    scarcity_vals = [r['scarcity'] for r in results]
    lifetimes = [r['mean_lifetime'] for r in results]
    phi_vals = [r['mean_phi'] for r in results]
    divergence_vals = [r['divergence'] for r in results]
    
    # Create 2x2 subplot
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # Plot 1: Lifetime heatmap
    unique_E = sorted(set(E_max_vals))
    unique_S = sorted(set(scarcity_vals))
    
    lifetime_matrix = np.zeros((len(unique_S), len(unique_E)))
    for r in results:
        i = unique_S.index(r['scarcity'])
        j = unique_E.index(r['E_max'])
        lifetime_matrix[i, j] = r['mean_lifetime']
    
    sns.heatmap(lifetime_matrix, 
                xticklabels=[f'{e:.0f}' for e in unique_E],
                yticklabels=[f'{s:.2f}' for s in unique_S],
                annot=True, fmt='.1f', cmap='YlOrRd', ax=axes[0, 0],
                cbar_kws={'label': 'Mean Lifetime'})
    axes[0, 0].set_xlabel('E_max')
    axes[0, 0].set_ylabel('Scarcity')
    axes[0, 0].set_title('Mean Lifetime by Parameters')
    
    # Plot 2: Φ heatmap
    phi_matrix = np.zeros((len(unique_S), len(unique_E)))
    for r in results:
        i = unique_S.index(r['scarcity'])
        j = unique_E.index(r['E_max'])
        phi_matrix[i, j] = r['mean_phi']
    
    sns.heatmap(phi_matrix,
                xticklabels=[f'{e:.0f}' for e in unique_E],
                yticklabels=[f'{s:.2f}' for s in unique_S],
                annot=True, fmt='.3f', cmap='viridis', ax=axes[0, 1],
                cbar_kws={'label': 'Mean Φ'})
    axes[0, 1].set_xlabel('E_max')
    axes[0, 1].set_ylabel('Scarcity')
    axes[0, 1].set_title('Mean Φ (Integrated Information)')
    
    # Plot 3: Divergence heatmap
    div_matrix = np.zeros((len(unique_S), len(unique_E)))
    for r in results:
        i = unique_S.index(r['scarcity'])
        j = unique_E.index(r['E_max'])
        div_matrix[i, j] = r['divergence']
    
    sns.heatmap(div_matrix,
                xticklabels=[f'{e:.0f}' for e in unique_E],
                yticklabels=[f'{s:.2f}' for s in unique_S],
                annot=True, fmt='.3f', cmap='coolwarm', ax=axes[1, 0],
                cbar_kws={'label': 'Divergence'})
    axes[1, 0].set_xlabel('E_max')
    axes[1, 0].set_ylabel('Scarcity')
    axes[1, 0].set_title('Behavioral Divergence')
    
    # Plot 4: Survival rate heatmap
    survival_matrix = np.zeros((len(unique_S), len(unique_E)))
    for r in results:
        i = unique_S.index(r['scarcity'])
        j = unique_E.index(r['E_max'])
        survival_matrix[i, j] = r['survival_rate'] * 100
    
    sns.heatmap(survival_matrix,
                xticklabels=[f'{e:.0f}' for e in unique_E],
                yticklabels=[f'{s:.2f}' for s in unique_S],
                annot=True, fmt='.0f', cmap='RdYlGn', ax=axes[1, 1],
                cbar_kws={'label': 'Survival Rate (%)'})
    axes[1, 1].set_xlabel('E_max')
    axes[1, 1].set_ylabel('Scarcity')
    axes[1, 1].set_title('Survival Rate')
    
    plt.tight_layout()
    
    save_path = os.path.join(save_dir, 'parameter_space_analysis.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\nSaved parameter space analysis to {save_path}")
    plt.close()


def generate_report(
    results: List[Dict[str, Any]],
    regimes: Dict[str, List[Dict[str, Any]]],
    save_dir: str
):
    """
    Generate tuning report with recommendations.
    """
    report_path = os.path.join(save_dir, 'tuning_report.md')
    
    with open(report_path, 'w') as f:
        f.write("# Parameter Tuning Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Overview\n\n")
        f.write(f"Total parameter combinations tested: {len(results)}\n")
        f.write(f"Trials per combination: 3-5\n\n")
        
        f.write("## Identified Behavioral Regimes\n\n")
        
        # Balanced regime
        f.write("### 1. Balanced Regime (Recommended for General Use)\n\n")
        f.write("Parameters where death is challenging but avoidable with skill:\n\n")
        if regimes['balanced']:
            for r in regimes['balanced'][:3]:  # Top 3
                f.write(f"- **E_max={r['E_max']:.0f}, Scarcity={r['scarcity']:.2f}**\n")
                f.write(f"  - Mean lifetime: {r['mean_lifetime']:.1f} steps\n")
                f.write(f"  - Survival rate: {r['survival_rate']*100:.0f}%\n")
                f.write(f"  - Φ: {r['mean_phi']:.3f}\n")
                f.write(f"  - Divergence: {r['divergence']:.3f}\n\n")
        else:
            f.write("No balanced regimes found.\n\n")
        
        # High Φ regime
        f.write("### 2. High Φ Regime (Coherent Behavior)\n\n")
        f.write("Parameters with strong integrated information:\n\n")
        if regimes['high_phi']:
            sorted_phi = sorted(regimes['high_phi'], key=lambda x: x['mean_phi'], reverse=True)
            for r in sorted_phi[:3]:
                f.write(f"- **E_max={r['E_max']:.0f}, Scarcity={r['scarcity']:.2f}**\n")
                f.write(f"  - Φ: {r['mean_phi']:.3f}\n")
                f.write(f"  - Mean lifetime: {r['mean_lifetime']:.1f} steps\n\n")
        else:
            f.write("No high-Φ regimes found.\n\n")
        
        # High divergence regime
        f.write("### 3. High Divergence Regime (Unique Trajectories)\n\n")
        f.write("Parameters producing meaningful behavioral divergence:\n\n")
        if regimes['high_divergence']:
            sorted_div = sorted(regimes['high_divergence'], key=lambda x: x['divergence'], reverse=True)
            for r in sorted_div[:3]:
                f.write(f"- **E_max={r['E_max']:.0f}, Scarcity={r['scarcity']:.2f}**\n")
                f.write(f"  - Divergence: {r['divergence']:.3f}\n")
                f.write(f"  - Mean lifetime: {r['mean_lifetime']:.1f} steps\n\n")
        else:
            f.write("No high-divergence regimes found.\n\n")
        
        # Extreme regime
        f.write("### 4. Extreme Regime (High Difficulty)\n\n")
        f.write("Parameters for testing survival under extreme conditions:\n\n")
        if regimes['extreme']:
            for r in regimes['extreme'][:3]:
                f.write(f"- **E_max={r['E_max']:.0f}, Scarcity={r['scarcity']:.2f}**\n")
                f.write(f"  - Mean lifetime: {r['mean_lifetime']:.1f} steps\n")
                f.write(f"  - Survival rate: {r['survival_rate']*100:.0f}%\n\n")
        else:
            f.write("No extreme regimes found.\n\n")
        
        f.write("## Recommendations\n\n")
        f.write("Based on the analysis:\n\n")
        
        if regimes['balanced']:
            best_balanced = max(regimes['balanced'], 
                              key=lambda x: x['mean_phi'] * x['divergence'])
            f.write(f"1. **For emergence demonstrations**: E_max={best_balanced['E_max']:.0f}, "
                   f"Scarcity={best_balanced['scarcity']:.2f}\n")
        
        if regimes['high_phi']:
            best_phi = max(regimes['high_phi'], key=lambda x: x['mean_phi'])
            f.write(f"2. **For Φ studies**: E_max={best_phi['E_max']:.0f}, "
                   f"Scarcity={best_phi['scarcity']:.2f}\n")
        
        if regimes['high_divergence']:
            best_div = max(regimes['high_divergence'], key=lambda x: x['divergence'])
            f.write(f"3. **For divergence studies**: E_max={best_div['E_max']:.0f}, "
                   f"Scarcity={best_div['scarcity']:.2f}\n")
    
    print(f"Saved tuning report to {report_path}")


def main():
    """Main parameter tuning execution"""
    print("="*70)
    print("PARAMETER TUNING - Thermo-AI Bio-Digital Organism")
    print("="*70)
    
    # Get parameter ranges from config
    sweep_config = CONFIGS.get('parameter_sweep', {})
    E_max_values = sweep_config.get('E_max', [40, 60, 80, 100, 120])
    scarcity_values = sweep_config.get('scarcity', [0.3, 0.5, 0.7, 0.9])
    
    # Run grid search
    results = grid_search(
        E_max_values=E_max_values,
        scarcity_values=scarcity_values,
        num_trials=3,
        max_steps=100
    )
    
    # Identify interesting regimes
    print("\nAnalyzing results...")
    regimes = identify_interesting_regimes(results)
    
    print(f"\nFound {len(regimes['balanced'])} balanced regimes")
    print(f"Found {len(regimes['high_phi'])} high-Φ regimes")
    print(f"Found {len(regimes['high_divergence'])} high-divergence regimes")
    print(f"Found {len(regimes['extreme'])} extreme regimes")
    
    # Save results
    save_dir = os.path.join(os.path.dirname(__file__), '..', 'results', 'tuning')
    os.makedirs(save_dir, exist_ok=True)
    
    # Save raw results
    results_path = os.path.join(save_dir, 'tuning_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved raw results to {results_path}")
    
    # Generate visualizations
    plot_parameter_space(results, save_dir)
    
    # Generate report
    generate_report(results, regimes, save_dir)
    
    print("\n" + "="*70)
    print("Parameter tuning complete!")
    print("="*70)


if __name__ == "__main__":
    main()
