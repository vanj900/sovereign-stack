"""
Survival Analysis Visualization

Kaplan-Meier survival curves, lifetime analysis, and survival probability heatmaps.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import os

# Set publication-quality defaults
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300


def plot_survival_curves(
    survival_data: Dict[str, List[int]],
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    Plot Kaplan-Meier style survival curves for different configurations.
    
    Args:
        survival_data: Dict mapping configuration name to list of lifetimes
        save_path: Path to save figure
        show: Whether to display the plot
    """
    if not survival_data:
        print("Warning: No survival data provided")
        return
    
    plt.figure(figsize=(12, 7))
    
    colors = sns.color_palette("husl", len(survival_data))
    
    for idx, (config_name, lifetimes) in enumerate(survival_data.items()):
        if not lifetimes:
            continue
        
        # Sort lifetimes
        lifetimes_sorted = sorted(lifetimes)
        max_time = max(lifetimes_sorted) if lifetimes_sorted else 0
        
        # Create survival function
        times = [0]
        survival_prob = [1.0]
        
        for i, t in enumerate(lifetimes_sorted):
            # Survival probability drops at each death
            times.append(t)
            survival_prob.append(1.0 - (i + 1) / len(lifetimes_sorted))
            
            # Flat line until next death
            if i < len(lifetimes_sorted) - 1:
                times.append(lifetimes_sorted[i + 1])
                survival_prob.append(1.0 - (i + 1) / len(lifetimes_sorted))
        
        plt.step(times, survival_prob, where='post', linewidth=2, 
                label=f'{config_name} (n={len(lifetimes)})', color=colors[idx])
        
        # Add median survival line
        median_lifetime = np.median(lifetimes)
        plt.axvline(x=median_lifetime, color=colors[idx], linestyle='--', 
                   alpha=0.3, linewidth=1)
    
    plt.xlabel('Time Steps', fontsize=12)
    plt.ylabel('Survival Probability', fontsize=12)
    plt.title('Survival Curves by Configuration', fontsize=14, fontweight='bold')
    plt.ylim(-0.05, 1.05)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='best', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.png', '.svg'), format='svg', bbox_inches='tight')
        print(f"Saved survival curves to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_lifetime_vs_scarcity(
    results: List[Tuple[float, int]],
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    Plot lifetime vs. scarcity as a scatter plot with trend line.
    
    Args:
        results: List of (scarcity, lifetime) tuples
        save_path: Path to save figure
        show: Whether to display the plot
    """
    if not results:
        print("Warning: No results provided")
        return
    
    scarcities = [r[0] for r in results]
    lifetimes = [r[1] for r in results]
    
    plt.figure(figsize=(10, 7))
    
    # Scatter plot
    plt.scatter(scarcities, lifetimes, alpha=0.6, s=50, c=lifetimes, 
               cmap='viridis', edgecolors='black', linewidth=0.5)
    
    # Add colorbar
    cbar = plt.colorbar()
    cbar.set_label('Lifetime (steps)', fontsize=11)
    
    # Fit and plot trend line
    if len(scarcities) > 1:
        z = np.polyfit(scarcities, lifetimes, 2)  # Quadratic fit
        p = np.poly1d(z)
        x_trend = np.linspace(min(scarcities), max(scarcities), 100)
        y_trend = p(x_trend)
        plt.plot(x_trend, y_trend, 'r--', linewidth=2, alpha=0.8, label='Trend (polynomial)')
    
    plt.xlabel('Scarcity', fontsize=12)
    plt.ylabel('Lifetime (steps)', fontsize=12)
    plt.title('Lifetime vs. Resource Scarcity', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='best')
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.png', '.svg'), format='svg', bbox_inches='tight')
        print(f"Saved lifetime vs scarcity plot to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_survival_heatmap(
    parameter_grid: Dict[str, Any],
    survival_matrix: np.ndarray,
    param1_name: str,
    param2_name: str,
    param1_values: List[float],
    param2_values: List[float],
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    Plot heatmap of survival probability by parameter combinations.
    
    Args:
        parameter_grid: Dictionary describing the parameter space
        survival_matrix: 2D array of survival probabilities or average lifetimes
        param1_name: Name of first parameter (x-axis)
        param2_name: Name of second parameter (y-axis)
        param1_values: Values for first parameter
        param2_values: Values for second parameter
        save_path: Path to save figure
        show: Whether to display the plot
    """
    plt.figure(figsize=(12, 8))
    
    # Create heatmap
    sns.heatmap(survival_matrix, 
                xticklabels=[f'{v:.2f}' for v in param1_values],
                yticklabels=[f'{v:.2f}' for v in param2_values],
                annot=True, fmt='.1f', cmap='RdYlGn', 
                cbar_kws={'label': 'Average Lifetime (steps)'},
                linewidths=0.5, linecolor='gray')
    
    plt.xlabel(param1_name, fontsize=12)
    plt.ylabel(param2_name, fontsize=12)
    plt.title(f'Survival Heatmap: {param1_name} vs {param2_name}', 
             fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.png', '.svg'), format='svg', bbox_inches='tight')
        print(f"Saved survival heatmap to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_death_causes_distribution(
    death_causes: List[str],
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    Plot distribution of death causes as a pie chart and bar chart.
    
    Args:
        death_causes: List of death causes
        save_path: Path to save figure
        show: Whether to display the plot
    """
    if not death_causes:
        print("Warning: No death causes provided")
        return
    
    # Count occurrences
    from collections import Counter
    cause_counts = Counter(death_causes)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Pie chart
    labels = list(cause_counts.keys())
    sizes = list(cause_counts.values())
    colors = sns.color_palette("Set3", len(labels))
    
    axes[0].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 11})
    axes[0].set_title('Death Causes Distribution', fontsize=13, fontweight='bold')
    
    # Bar chart
    axes[1].bar(labels, sizes, color=colors, edgecolor='black', linewidth=1.5)
    axes[1].set_xlabel('Death Cause', fontsize=12)
    axes[1].set_ylabel('Count', fontsize=12)
    axes[1].set_title('Death Causes Frequency', fontsize=13, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # Rotate labels if needed
    if len(labels) > 3:
        axes[1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.png', '.svg'), format='svg', bbox_inches='tight')
        print(f"Saved death causes plot to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()
