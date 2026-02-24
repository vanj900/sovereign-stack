"""
Visualization Module - Publication-Ready Plots

This module provides visualization tools for analyzing Bio-Digital Organism behavior,
including energy trajectories, bifurcation analysis, entropy dynamics, and survival analysis.
"""

from .energy_trajectories import (
    plot_energy_trajectory,
    plot_multi_agent_comparison,
    plot_state_variables_grid
)

from .entropy_export import (
    plot_entropy_dynamics,
    plot_heat_dissipation,
    plot_thermodynamic_efficiency
)

from .survival_analysis import (
    plot_survival_curves,
    plot_lifetime_vs_scarcity,
    plot_survival_heatmap
)

from .bifurcation_analysis import (
    plot_decision_tree,
    plot_parameter_bifurcation,
    plot_trajectory_divergence
)

__all__ = [
    # Energy trajectories
    'plot_energy_trajectory',
    'plot_multi_agent_comparison',
    'plot_state_variables_grid',
    
    # Entropy dynamics
    'plot_entropy_dynamics',
    'plot_heat_dissipation',
    'plot_thermodynamic_efficiency',
    
    # Survival analysis
    'plot_survival_curves',
    'plot_lifetime_vs_scarcity',
    'plot_survival_heatmap',
    
    # Bifurcation
    'plot_decision_tree',
    'plot_parameter_bifurcation',
    'plot_trajectory_divergence',
]
