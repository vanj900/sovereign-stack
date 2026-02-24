"""
Bifurcation Analysis Visualization

Plot decision trees, parameter space bifurcations, and trajectory divergence.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict, Any, Optional
import os

# Set publication-quality defaults
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300


def plot_trajectory_divergence(
    agent_histories: Dict[str, List[Dict[str, Any]]],
    variable: str = 'energy',
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    Plot trajectory divergence for agents with identical initial conditions.
    
    Args:
        agent_histories: Dict mapping agent_id to state history
        variable: Which variable to track
        save_path: Path to save figure
        show: Whether to display the plot
    """
    if not agent_histories or len(agent_histories) < 2:
        print("Warning: Need at least 2 agents to plot divergence")
        return
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    colors = sns.color_palette("husl", len(agent_histories))
    
    # Plot 1: Individual trajectories
    for idx, (agent_id, history) in enumerate(agent_histories.items()):
        if not history:
            continue
        
        steps = list(range(len(history)))
        values = [s[variable] for s in history]
        
        axes[0].plot(steps, values, linewidth=2, label=agent_id,
                    color=colors[idx], alpha=0.7)
    
    axes[0].set_xlabel('Time Steps', fontsize=12)
    axes[0].set_ylabel(variable.replace('_', ' ').title(), fontsize=12)
    axes[0].set_title('Trajectory Divergence from Identical Initial Conditions', 
                     fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc='best', ncol=3, fontsize=9)
    
    # Plot 2: Divergence metric over time
    # Calculate pairwise divergence at each time step
    min_length = min(len(hist) for hist in agent_histories.values())
    
    divergences = []
    for t in range(min_length):
        values_at_t = []
        for history in agent_histories.values():
            values_at_t.append(history[t][variable])
        
        # Standard deviation as divergence metric
        divergence = np.std(values_at_t)
        divergences.append(divergence)
    
    steps = list(range(min_length))
    axes[1].plot(steps, divergences, 'r-', linewidth=2, label='Divergence (std dev)')
    axes[1].fill_between(steps, 0, divergences, alpha=0.3, color='red')
    axes[1].set_xlabel('Time Steps', fontsize=12)
    axes[1].set_ylabel('Divergence Metric (σ)', fontsize=12)
    axes[1].set_title('Divergence Growth Over Time', fontsize=13, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(loc='upper left')
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.png', '.svg'), format='svg', bbox_inches='tight')
        print(f"Saved divergence plot to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_parameter_bifurcation(
    parameter_name: str,
    parameter_values: List[float],
    outcomes: Dict[str, List[Any]],
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    Plot bifurcation diagram showing how outcomes change with parameter.
    
    Args:
        parameter_name: Name of the parameter being varied
        parameter_values: Values of the parameter
        outcomes: Dict mapping outcome type to list of values at each parameter
        save_path: Path to save figure
        show: Whether to display the plot
    """
    if not outcomes:
        print("Warning: No outcomes provided")
        return
    
    plt.figure(figsize=(12, 8))
    
    colors = sns.color_palette("Set2", len(outcomes))
    
    for idx, (outcome_name, values) in enumerate(outcomes.items()):
        plt.scatter(parameter_values, values, alpha=0.6, s=30, 
                   label=outcome_name, color=colors[idx])
    
    plt.xlabel(parameter_name, fontsize=12)
    plt.ylabel('Outcome Value', fontsize=12)
    plt.title(f'Bifurcation Analysis: {parameter_name}', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='best', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.png', '.svg'), format='svg', bbox_inches='tight')
        print(f"Saved bifurcation plot to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_decision_tree(
    decisions: List[Dict[str, Any]],
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    Plot decision tree visualization for ethical dilemmas.
    
    Args:
        decisions: List of decision records with choices and outcomes
        save_path: Path to save figure
        show: Whether to display the plot
    """
    if not decisions:
        print("Warning: No decisions provided")
        return
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Extract decision types and outcomes
    decision_types = [d.get('type', 'unknown') for d in decisions]
    choices = [d.get('choice', 'unknown') for d in decisions]
    
    # Count decision patterns
    from collections import Counter
    type_counts = Counter(decision_types)
    choice_counts = Counter(choices)
    
    # Create two subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot decision types
    if type_counts:
        types = list(type_counts.keys())
        counts = list(type_counts.values())
        colors1 = sns.color_palette("Set3", len(types))
        
        axes[0].barh(types, counts, color=colors1, edgecolor='black', linewidth=1.5)
        axes[0].set_xlabel('Count', fontsize=12)
        axes[0].set_ylabel('Decision Type', fontsize=12)
        axes[0].set_title('Decision Types Distribution', fontsize=13, fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='x')
    
    # Plot choice outcomes
    if choice_counts:
        choices_list = list(choice_counts.keys())
        counts_list = list(choice_counts.values())
        colors2 = sns.color_palette("Set2", len(choices_list))
        
        axes[1].pie(counts_list, labels=choices_list, colors=colors2, 
                   autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})
        axes[1].set_title('Choice Distribution', fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.png', '.svg'), format='svg', bbox_inches='tight')
        print(f"Saved decision tree plot to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_phase_space(
    state_histories: List[List[Dict[str, Any]]],
    var1: str = 'energy',
    var2: str = 'temperature',
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    Plot phase space trajectories (2D projection of state space).
    
    Args:
        state_histories: List of state histories for multiple agents
        var1: First state variable
        var2: Second state variable
        save_path: Path to save figure
        show: Whether to display the plot
    """
    if not state_histories:
        print("Warning: No state histories provided")
        return
    
    plt.figure(figsize=(10, 10))
    
    colors = sns.color_palette("husl", len(state_histories))
    
    for idx, history in enumerate(state_histories):
        if not history:
            continue
        
        var1_values = [s[var1] for s in history]
        var2_values = [s[var2] for s in history]
        
        # Plot trajectory
        plt.plot(var1_values, var2_values, linewidth=1.5, 
                color=colors[idx], alpha=0.6, label=f'Agent {idx+1}')
        
        # Mark start and end
        plt.scatter(var1_values[0], var2_values[0], 
                   color=colors[idx], s=100, marker='o', 
                   edgecolors='black', linewidth=2, zorder=5)
        plt.scatter(var1_values[-1], var2_values[-1], 
                   color=colors[idx], s=100, marker='X', 
                   edgecolors='black', linewidth=2, zorder=5)
    
    plt.xlabel(var1.replace('_', ' ').title(), fontsize=12)
    plt.ylabel(var2.replace('_', ' ').title(), fontsize=12)
    plt.title(f'Phase Space: {var1} vs {var2}', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='best', fontsize=9)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.png', '.svg'), format='svg', bbox_inches='tight')
        print(f"Saved phase space plot to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()
