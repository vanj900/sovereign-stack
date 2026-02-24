"""
Energy Trajectories Visualization

Plot energy (E), temperature (T), memory (M), and stability (S) over time.
Supports comparison of multiple agents and highlights critical events.
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
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10


def plot_energy_trajectory(
    state_history: List[Dict[str, Any]],
    agent_id: str = "organism",
    death_step: Optional[int] = None,
    near_death_steps: Optional[List[int]] = None,
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    Plot energy, temperature, memory, and stability trajectories for a single agent.
    
    Args:
        state_history: List of metabolic state snapshots
        agent_id: Agent identifier for title
        death_step: Step at which death occurred (if any)
        near_death_steps: List of steps with near-death experiences
        save_path: Path to save figure (None = don't save)
        show: Whether to display the plot
    """
    if not state_history:
        print("Warning: Empty state history, cannot plot")
        return
    
    # Extract time series
    steps = list(range(len(state_history)))
    energy = [s['energy'] for s in state_history]
    temperature = [s['temperature'] for s in state_history]
    memory = [s['memory_integrity'] for s in state_history]
    stability = [s['stability'] for s in state_history]
    
    # Create figure with 4 subplots
    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    
    # Plot Energy
    axes[0].plot(steps, energy, 'b-', linewidth=2, label='Energy (E)')
    axes[0].set_ylabel('Energy (J)', fontsize=12)
    axes[0].set_title(f'Agent: {agent_id} - State Variable Trajectories', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc='upper right')
    
    # Plot Temperature
    axes[1].plot(steps, temperature, 'r-', linewidth=2, label='Temperature (T)')
    # Add safe/critical temperature lines if available
    if state_history[0].get('T_safe'):
        axes[1].axhline(y=310.0, color='orange', linestyle='--', alpha=0.5, label='Safe Temp')
    if state_history[0].get('T_critical'):
        axes[1].axhline(y=350.0, color='red', linestyle='--', alpha=0.5, label='Critical Temp')
    axes[1].set_ylabel('Temperature (K)', fontsize=12)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(loc='upper right')
    
    # Plot Memory Integrity
    axes[2].plot(steps, memory, 'g-', linewidth=2, label='Memory (M)')
    axes[2].set_ylabel('Memory Integrity', fontsize=12)
    axes[2].set_ylim(-0.05, 1.05)
    axes[2].grid(True, alpha=0.3)
    axes[2].legend(loc='upper right')
    
    # Plot Stability
    axes[3].plot(steps, stability, 'm-', linewidth=2, label='Stability (S)')
    axes[3].set_ylabel('Stability', fontsize=12)
    axes[3].set_xlabel('Time Steps', fontsize=12)
    axes[3].set_ylim(-0.05, 1.05)
    axes[3].grid(True, alpha=0.3)
    axes[3].legend(loc='upper right')
    
    # Highlight death event
    if death_step is not None:
        for ax in axes:
            ax.axvline(x=death_step, color='black', linestyle='--', linewidth=2, alpha=0.7)
            ax.text(death_step, ax.get_ylim()[1] * 0.9, 'DEATH', 
                   rotation=90, va='top', ha='right', fontsize=10, fontweight='bold')
    
    # Highlight near-death experiences
    if near_death_steps:
        for step in near_death_steps:
            for ax in axes:
                ax.axvline(x=step, color='red', linestyle=':', linewidth=1, alpha=0.5)
    
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.png', '.svg'), format='svg', bbox_inches='tight')
        print(f"Saved trajectory plot to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_multi_agent_comparison(
    agent_histories: Dict[str, List[Dict[str, Any]]],
    variable: str = 'energy',
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    Plot a single variable for multiple agents on the same axes for comparison.
    
    Args:
        agent_histories: Dict mapping agent_id to state history
        variable: Which variable to plot ('energy', 'temperature', 'memory_integrity', 'stability')
        save_path: Path to save figure
        show: Whether to display the plot
    """
    if not agent_histories:
        print("Warning: No agent histories provided")
        return
    
    plt.figure(figsize=(14, 6))
    
    # Color palette
    colors = sns.color_palette("husl", len(agent_histories))
    
    # Plot each agent
    for idx, (agent_id, history) in enumerate(agent_histories.items()):
        if not history:
            continue
        
        steps = list(range(len(history)))
        values = [s[variable] for s in history]
        
        plt.plot(steps, values, linewidth=2, label=agent_id, 
                color=colors[idx], alpha=0.8)
    
    # Labels
    var_labels = {
        'energy': 'Energy (J)',
        'temperature': 'Temperature (K)',
        'memory_integrity': 'Memory Integrity',
        'stability': 'Stability'
    }
    
    plt.xlabel('Time Steps', fontsize=12)
    plt.ylabel(var_labels.get(variable, variable), fontsize=12)
    plt.title(f'Multi-Agent Comparison: {variable.replace("_", " ").title()}', 
             fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='best', ncol=2)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.png', '.svg'), format='svg', bbox_inches='tight')
        print(f"Saved comparison plot to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_state_variables_grid(
    agent_histories: Dict[str, List[Dict[str, Any]]],
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    Create a 2x2 grid comparing all four state variables across agents.
    
    Args:
        agent_histories: Dict mapping agent_id to state history
        save_path: Path to save figure
        show: Whether to display the plot
    """
    if not agent_histories:
        print("Warning: No agent histories provided")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('Multi-Agent State Variable Comparison', fontsize=16, fontweight='bold')
    
    variables = ['energy', 'temperature', 'memory_integrity', 'stability']
    var_labels = {
        'energy': 'Energy (J)',
        'temperature': 'Temperature (K)',
        'memory_integrity': 'Memory Integrity',
        'stability': 'Stability'
    }
    
    colors = sns.color_palette("husl", len(agent_histories))
    
    for idx, var in enumerate(variables):
        ax = axes[idx // 2, idx % 2]
        
        # Plot each agent
        for agent_idx, (agent_id, history) in enumerate(agent_histories.items()):
            if not history:
                continue
            
            steps = list(range(len(history)))
            values = [s[var] for s in history]
            
            ax.plot(steps, values, linewidth=1.5, label=agent_id,
                   color=colors[agent_idx], alpha=0.7)
        
        ax.set_xlabel('Time Steps', fontsize=11)
        ax.set_ylabel(var_labels[var], fontsize=11)
        ax.set_title(var_labels[var], fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        if idx == 0:  # Only show legend on first plot
            ax.legend(loc='best', fontsize=8, ncol=2)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.png', '.svg'), format='svg', bbox_inches='tight')
        print(f"Saved grid plot to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()
