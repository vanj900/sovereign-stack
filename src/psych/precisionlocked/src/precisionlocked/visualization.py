"""
Visualization and Simulation Utilities

Tools for visualizing trauma dynamics, therapeutic intervention,
and free energy landscapes.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def plot_trauma_dynamics(
    results: Dict,
    save_path: Optional[str] = None
):
    """
    Visualize trauma dynamics over time.
    
    Args:
        results: Dictionary from TraumaSimulator.run_simulation()
        save_path: Optional path to save figure
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available for plotting")
        return
    
    fig, axes = plt.subplots(3, 1, figsize=(10, 8))
    
    # Plot prediction errors
    axes[0].plot(results['errors'], color='red', linewidth=2)
    axes[0].set_ylabel('Prediction Error', fontsize=12)
    axes[0].set_title('Trauma Dynamics: Chronic Error Suppression', fontsize=14)
    axes[0].grid(True, alpha=0.3)
    
    # Plot instantaneous allostatic load
    axes[1].plot(results['loads'], color='orange', linewidth=2)
    axes[1].set_ylabel('Allostatic Load (ATP)', fontsize=12)
    axes[1].grid(True, alpha=0.3)
    
    # Plot cumulative load
    axes[2].plot(results['cumulative_load'], color='darkred', linewidth=2)
    axes[2].set_ylabel('Cumulative Load', fontsize=12)
    axes[2].set_xlabel('Time', fontsize=12)
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_therapeutic_intervention(
    history: Dict,
    save_path: Optional[str] = None
):
    """
    Visualize therapeutic intervention (Bayesian Annealing).
    
    Args:
        history: Dictionary from TherapeuticIntervention.run_session()
        save_path: Optional path to save figure
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available for plotting")
        return
    
    fig, axes = plt.subplots(4, 1, figsize=(12, 10))
    
    # Extract beliefs (mu) over time
    mu_values = np.array(history['mu'])
    if mu_values.ndim > 1:
        mu_values = mu_values[:, 0]  # Take first dimension
    
    # Plot belief trajectory
    axes[0].plot(mu_values, color='blue', linewidth=2, label='Belief (μ)')
    axes[0].axhline(y=1.0, color='green', linestyle='--', label='Safety')
    axes[0].axhline(y=-1.0, color='red', linestyle='--', label='Danger')
    axes[0].set_ylabel('Belief State (μ)', fontsize=12)
    axes[0].set_title('Bayesian Annealing: Therapeutic Belief Updating', fontsize=14)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot precision dynamics
    axes[1].plot(history['pi_prior'], color='red', linewidth=2, label='Prior Π')
    axes[1].plot(history['pi_sensory'], color='green', linewidth=2, label='Sensory Π')
    axes[1].set_ylabel('Precision (Π)', fontsize=12)
    axes[1].set_yscale('log')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Plot free energy
    axes[2].plot(history['free_energy'], color='purple', linewidth=2)
    axes[2].set_ylabel('Free Energy (F)', fontsize=12)
    axes[2].grid(True, alpha=0.3)
    
    # Plot update magnitude
    axes[3].plot(history['update_magnitude'], color='orange', linewidth=2)
    axes[3].set_ylabel('Update Magnitude', fontsize=12)
    axes[3].set_xlabel('Time', fontsize=12)
    axes[3].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_precision_landscape(
    pi_prior_range: Tuple[float, float] = (0.1, 100),
    pi_sensory_range: Tuple[float, float] = (0.1, 100),
    n_points: int = 50,
    save_path: Optional[str] = None
):
    """
    Visualize the precision landscape (regime diagram).
    
    Shows regions of prior-driven vs sensory-driven regimes.
    
    Args:
        pi_prior_range: Range of prior precision values
        pi_sensory_range: Range of sensory precision values
        n_points: Number of grid points
        save_path: Optional path to save figure
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available for plotting")
        return
    
    # Create grid
    pi_prior = np.logspace(
        np.log10(pi_prior_range[0]),
        np.log10(pi_prior_range[1]),
        n_points
    )
    pi_sensory = np.logspace(
        np.log10(pi_sensory_range[0]),
        np.log10(pi_sensory_range[1]),
        n_points
    )
    
    PP, PS = np.meshgrid(pi_prior, pi_sensory)
    
    # Compute ratio (prior/sensory precision)
    ratio = PP / PS
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Contour plot
    levels = [0.1, 1.0, 10.0]
    cs = ax.contour(PP, PS, ratio, levels=levels, colors='black', linewidths=2)
    ax.clabel(cs, inline=True, fontsize=10)
    
    # Fill regions
    cf = ax.contourf(PP, PS, ratio, levels=[0, 1, 10, 100], 
                     colors=['lightgreen', 'yellow', 'red'], alpha=0.5)
    
    # Add colorbar
    cbar = plt.colorbar(cf, ax=ax)
    cbar.set_label('Prior/Sensory Ratio', fontsize=12)
    
    # Labels and annotations
    ax.set_xlabel('Prior Precision (Π_prior)', fontsize=12)
    ax.set_ylabel('Sensory Precision (Π_sensory)', fontsize=12)
    ax.set_title('Precision Landscape: Trauma vs Healthy Regimes', fontsize=14)
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    # Annotate regions
    ax.text(1, 50, 'Sensory-Driven\n(Healthy)', fontsize=12, ha='center')
    ax.text(50, 1, 'Prior-Driven\n(Trauma)', fontsize=12, ha='center')
    
    # Mark example points
    ax.plot(100, 0.1, 'ro', markersize=10, label='Trauma State')
    ax.plot(1, 10, 'go', markersize=10, label='Healthy State')
    
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def compare_scenarios(
    trauma_results: Dict,
    therapy_results: Dict,
    save_path: Optional[str] = None
):
    """
    Compare trauma dynamics with therapeutic intervention.
    
    Args:
        trauma_results: Results from trauma simulation
        therapy_results: Results from therapy simulation
        save_path: Optional path to save figure
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available for plotting")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Extract therapy beliefs
    therapy_mu = np.array(therapy_results['mu'])
    if therapy_mu.ndim > 1:
        therapy_mu = therapy_mu[:, 0]
    
    # Top left: Belief evolution
    axes[0, 0].axhline(y=-1.0, color='red', linestyle='--', 
                       linewidth=1, label='Trauma prior')
    axes[0, 0].axhline(y=1.0, color='green', linestyle='--', 
                       linewidth=1, label='Safety')
    axes[0, 0].plot(therapy_mu, color='blue', linewidth=2, 
                    label='Therapy: Belief update')
    axes[0, 0].set_ylabel('Belief State (μ)', fontsize=11)
    axes[0, 0].set_title('Belief Trajectory', fontsize=12)
    axes[0, 0].legend(fontsize=9)
    axes[0, 0].grid(True, alpha=0.3)
    
    # Top right: Prediction errors
    axes[0, 1].plot(trauma_results['errors'], color='red', 
                    linewidth=2, label='Trauma: Chronic errors')
    axes[0, 1].set_ylabel('Prediction Error', fontsize=11)
    axes[0, 1].set_title('Error Dynamics', fontsize=12)
    axes[0, 1].legend(fontsize=9)
    axes[0, 1].grid(True, alpha=0.3)
    
    # Bottom left: Allostatic load
    axes[1, 0].plot(trauma_results['cumulative_load'], color='darkred', 
                    linewidth=2, label='Trauma: Cumulative load')
    axes[1, 0].set_ylabel('Cumulative Allostatic Load', fontsize=11)
    axes[1, 0].set_xlabel('Time', fontsize=11)
    axes[1, 0].set_title('Metabolic Cost', fontsize=12)
    axes[1, 0].legend(fontsize=9)
    axes[1, 0].grid(True, alpha=0.3)
    
    # Bottom right: Free energy
    axes[1, 1].plot(therapy_results['free_energy'], color='purple', 
                    linewidth=2, label='Therapy: Free energy')
    axes[1, 1].set_ylabel('Free Energy (F)', fontsize=11)
    axes[1, 1].set_xlabel('Time', fontsize=11)
    axes[1, 1].set_title('Free Energy Minimization', fontsize=12)
    axes[1, 1].legend(fontsize=9)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle('Trauma vs Therapeutic Intervention', fontsize=14, y=1.0)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def print_summary(results: Dict, title: str = "Simulation Summary"):
    """
    Print a text summary of simulation results.
    
    Args:
        results: Results dictionary
        title: Title for the summary
    """
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}\n")
    
    if 'errors' in results:
        print(f"Prediction Errors:")
        print(f"  Mean: {np.mean(results['errors']):.3f}")
        print(f"  Max:  {np.max(results['errors']):.3f}")
        print(f"  Final: {results['errors'][-1]:.3f}\n")
    
    if 'cumulative_load' in results:
        print(f"Allostatic Load:")
        print(f"  Final cumulative: {results['cumulative_load'][-1]:.2f}")
        print(f"  Mean rate: {np.mean(results['loads']):.3f}\n")
    
    if 'mu' in results:
        mu_final = results['mu'][-1]
        mu_initial = results['mu'][0]
        print(f"Belief State:")
        print(f"  Initial: {mu_initial}")
        print(f"  Final:   {mu_final}")
        print(f"  Shift:   {np.linalg.norm(mu_final - mu_initial):.3f}\n")
    
    if 'free_energy' in results:
        print(f"Free Energy:")
        print(f"  Initial: {results['free_energy'][0]:.3f}")
        print(f"  Final:   {results['free_energy'][-1]:.3f}")
        print(f"  Reduction: {results['free_energy'][0] - results['free_energy'][-1]:.3f}\n")
    
    print(f"{'='*60}\n")
