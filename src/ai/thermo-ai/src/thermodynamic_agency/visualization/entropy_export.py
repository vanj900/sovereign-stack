"""
Entropy Export Visualization

Plot entropy generation vs. export rates, heat dissipation dynamics,
and thermodynamic efficiency.
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


def plot_entropy_dynamics(
    state_history: List[Dict[str, Any]],
    agent_id: str = "organism",
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    Plot entropy generation and export dynamics over time.
    
    Args:
        state_history: List of metabolic state snapshots
        agent_id: Agent identifier
        save_path: Path to save figure
        show: Whether to display the plot
    """
    if len(state_history) < 2:
        print("Warning: Need at least 2 states to plot entropy dynamics")
        return
    
    steps = list(range(len(state_history)))
    stability = [s['stability'] for s in state_history]
    
    # Calculate entropy generation (decrease in stability)
    entropy_gen = [0]
    for i in range(1, len(stability)):
        gen = max(0, stability[i-1] - stability[i])
        entropy_gen.append(gen)
    
    # Calculate cumulative entropy
    cumulative_entropy = np.cumsum(entropy_gen)
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Plot instantaneous entropy generation
    axes[0].plot(steps, entropy_gen, 'r-', linewidth=2, label='Entropy Generation Rate')
    axes[0].fill_between(steps, 0, entropy_gen, alpha=0.3, color='red')
    axes[0].set_ylabel('Entropy Generation\n(ΔS per step)', fontsize=12)
    axes[0].set_title(f'Agent: {agent_id} - Entropy Dynamics', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc='upper right')
    
    # Plot cumulative entropy and stability
    ax2 = axes[1]
    ax2_twin = ax2.twinx()
    
    line1 = ax2.plot(steps, cumulative_entropy, 'r-', linewidth=2, 
                     label='Cumulative Entropy', alpha=0.8)
    line2 = ax2_twin.plot(steps, stability, 'b-', linewidth=2, 
                          label='Stability (S)', alpha=0.8)
    
    ax2.set_xlabel('Time Steps', fontsize=12)
    ax2.set_ylabel('Cumulative Entropy', fontsize=12, color='r')
    ax2_twin.set_ylabel('Stability', fontsize=12, color='b')
    ax2.tick_params(axis='y', labelcolor='r')
    ax2_twin.tick_params(axis='y', labelcolor='b')
    ax2.grid(True, alpha=0.3)
    
    # Combined legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc='upper right')
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.png', '.svg'), format='svg', bbox_inches='tight')
        print(f"Saved entropy dynamics plot to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_heat_dissipation(
    state_history: List[Dict[str, Any]],
    agent_id: str = "organism",
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    Plot heat generation and dissipation dynamics.
    
    Args:
        state_history: List of metabolic state snapshots
        agent_id: Agent identifier
        save_path: Path to save figure
        show: Whether to display the plot
    """
    if len(state_history) < 2:
        print("Warning: Need at least 2 states to plot heat dissipation")
        return
    
    steps = list(range(len(state_history)))
    temperature = [s['temperature'] for s in state_history]
    energy = [s['energy'] for s in state_history]
    
    # Estimate heat generation (temperature increases)
    heat_gen = [0]
    for i in range(1, len(temperature)):
        gen = max(0, temperature[i] - temperature[i-1])
        heat_gen.append(gen)
    
    # Estimate heat dissipation (temperature decreases)
    heat_diss = [0]
    for i in range(1, len(temperature)):
        diss = max(0, temperature[i-1] - temperature[i])
        heat_diss.append(diss)
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Plot temperature trajectory with safe/critical zones
    axes[0].plot(steps, temperature, 'r-', linewidth=2, label='Temperature')
    axes[0].axhline(y=293.15, color='blue', linestyle='--', alpha=0.3, label='Ambient (20°C)')
    axes[0].axhline(y=310.0, color='orange', linestyle='--', alpha=0.5, label='Safe (~37°C)')
    axes[0].axhline(y=350.0, color='red', linestyle='--', alpha=0.5, label='Critical (~77°C)')
    axes[0].fill_between(steps, 293.15, 310.0, alpha=0.1, color='green', label='Safe Zone')
    axes[0].fill_between(steps, 310.0, 350.0, alpha=0.1, color='orange', label='Warning Zone')
    axes[0].set_ylabel('Temperature (K)', fontsize=12)
    axes[0].set_title(f'Agent: {agent_id} - Heat Dissipation Dynamics', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc='best', fontsize=9)
    
    # Plot heat generation and dissipation rates
    axes[1].bar(steps, heat_gen, width=1.0, alpha=0.6, color='red', label='Heat Generation')
    axes[1].bar(steps, [-d for d in heat_diss], width=1.0, alpha=0.6, color='blue', label='Heat Dissipation')
    axes[1].axhline(y=0, color='black', linewidth=0.8)
    axes[1].set_xlabel('Time Steps', fontsize=12)
    axes[1].set_ylabel('Heat Rate (ΔT per step)', fontsize=12)
    axes[1].grid(True, alpha=0.3, axis='y')
    axes[1].legend(loc='upper right')
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.png', '.svg'), format='svg', bbox_inches='tight')
        print(f"Saved heat dissipation plot to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_thermodynamic_efficiency(
    state_history: List[Dict[str, Any]],
    agent_id: str = "organism",
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    Plot thermodynamic efficiency metrics over time.
    
    Args:
        state_history: List of metabolic state snapshots
        agent_id: Agent identifier
        save_path: Path to save figure
        show: Whether to display the plot
    """
    if len(state_history) < 2:
        print("Warning: Need at least 2 states to plot efficiency")
        return
    
    steps = list(range(len(state_history)))
    energy = [s['energy'] for s in state_history]
    temperature = [s['temperature'] for s in state_history]
    stability = [s['stability'] for s in state_history]
    memory = [s['memory_integrity'] for s in state_history]
    
    # Calculate energy expenditure rate
    energy_rate = [0]
    for i in range(1, len(energy)):
        rate = max(0, energy[i-1] - energy[i])
        energy_rate.append(rate)
    
    # Calculate useful work (maintaining stability and memory)
    useful_work = []
    for i in range(len(state_history)):
        work = stability[i] * memory[i]  # Proxy for useful state maintenance
        useful_work.append(work)
    
    # Calculate efficiency: useful work per energy spent
    efficiency = []
    cumulative_energy = 0
    for i in range(len(steps)):
        cumulative_energy += energy_rate[i]
        if cumulative_energy > 0.1:
            eff = useful_work[i] / cumulative_energy
            efficiency.append(eff)
        else:
            efficiency.append(0)
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Plot energy expenditure
    axes[0].plot(steps, energy_rate, 'b-', linewidth=2)
    axes[0].fill_between(steps, 0, energy_rate, alpha=0.3, color='blue')
    axes[0].set_ylabel('Energy Rate\n(ΔE per step)', fontsize=12)
    axes[0].set_title(f'Agent: {agent_id} - Thermodynamic Efficiency', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    # Plot useful work
    axes[1].plot(steps, useful_work, 'g-', linewidth=2)
    axes[1].fill_between(steps, 0, useful_work, alpha=0.3, color='green')
    axes[1].set_ylabel('Useful Work\n(S × M)', fontsize=12)
    axes[1].grid(True, alpha=0.3)
    
    # Plot efficiency
    axes[2].plot(steps, efficiency, 'purple', linewidth=2)
    axes[2].fill_between(steps, 0, efficiency, alpha=0.3, color='purple')
    axes[2].set_xlabel('Time Steps', fontsize=12)
    axes[2].set_ylabel('Efficiency\n(Work / Energy)', fontsize=12)
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.png', '.svg'), format='svg', bbox_inches='tight')
        print(f"Saved efficiency plot to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()
