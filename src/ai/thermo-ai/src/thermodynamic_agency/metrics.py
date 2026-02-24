"""
Metrics Module - Quantifying Emergent Properties

This module provides tools for measuring and quantifying key emergent properties
of the Bio-Digital Organism, including integrated information (Φ), behavioral
divergence, survival efficiency, and ethical consistency.
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from scipy.stats import entropy as scipy_entropy
from scipy.spatial.distance import euclidean, cosine


def calculate_phi(state_history: List[Dict[str, Any]], window_size: int = 10) -> float:
    """
    Calculate Φ (Integrated Information) as a measure of coherent behavior.
    
    This is a simplified approximation inspired by Integrated Information Theory (IIT).
    We measure the mutual information between different state variables over time,
    indicating how coherently the system behaves.
    
    Args:
        state_history: List of metabolic state snapshots over time
        window_size: Number of time steps to analyze
        
    Returns:
        Φ value (higher = more integrated/coherent behavior)
    """
    if len(state_history) < window_size:
        return 0.0
    
    # Extract recent state variables
    recent_states = state_history[-window_size:]
    
    # Extract time series for each variable
    energy = np.array([s['energy'] for s in recent_states])
    temperature = np.array([s['temperature'] for s in recent_states])
    memory = np.array([s['memory_integrity'] for s in recent_states])
    stability = np.array([s['stability'] for s in recent_states])
    
    # Normalize to [0, 1] range
    def normalize(arr):
        arr_min, arr_max = arr.min(), arr.max()
        if arr_max - arr_min < 1e-10:
            return np.ones_like(arr) * 0.5
        return (arr - arr_min) / (arr_max - arr_min)
    
    energy_norm = normalize(energy)
    temp_norm = normalize(temperature)
    memory_norm = normalize(memory)
    stability_norm = normalize(stability)
    
    # Calculate correlations between variables (proxy for integration)
    correlations = []
    pairs = [
        (energy_norm, temp_norm),
        (energy_norm, memory_norm),
        (energy_norm, stability_norm),
        (temp_norm, memory_norm),
        (temp_norm, stability_norm),
        (memory_norm, stability_norm)
    ]
    
    for v1, v2 in pairs:
        corr = np.corrcoef(v1, v2)[0, 1]
        if not np.isnan(corr):
            correlations.append(abs(corr))
    
    # Φ approximation: average absolute correlation
    # High correlation = variables are integrated/coherent
    phi = np.mean(correlations) if correlations else 0.0
    
    return phi


def calculate_divergence_index(
    trajectories: List[List[Dict[str, Any]]],
    time_step: int = None
) -> float:
    """
    Calculate divergence index between multiple agent trajectories.
    
    Quantifies how much agents with identical initial conditions diverge
    due to stochastic events.
    
    Args:
        trajectories: List of state histories for multiple agents
        time_step: Specific time step to measure (None = final state)
        
    Returns:
        Divergence index (0 = identical, 1 = maximally different)
    """
    if len(trajectories) < 2:
        return 0.0
    
    # Find minimum trajectory length
    min_length = min(len(traj) for traj in trajectories)
    if min_length == 0:
        return 0.0
    
    # Use specified time step or last common time step
    if time_step is None or time_step >= min_length:
        time_step = min_length - 1
    
    # Extract states at the specified time step
    states = [traj[time_step] for traj in trajectories]
    
    # Create state vectors
    state_vectors = []
    for state in states:
        vector = np.array([
            state.get('energy', 0),
            state.get('temperature', 0),
            state.get('memory_integrity', 0),
            state.get('stability', 0)
        ])
        state_vectors.append(vector)
    
    # Calculate pairwise distances
    distances = []
    for i in range(len(state_vectors)):
        for j in range(i + 1, len(state_vectors)):
            dist = euclidean(state_vectors[i], state_vectors[j])
            distances.append(dist)
    
    # Normalize by maximum possible distance
    # Max distance ≈ sqrt(E_max² + T_range² + 1² + 1²)
    max_dist = np.sqrt(100**2 + 100**2 + 1 + 1)  # Approximate
    
    divergence = np.mean(distances) / max_dist if distances else 0.0
    return min(divergence, 1.0)


def calculate_survival_efficiency(
    lifetime: int,
    total_energy_consumed: float,
    E_max: float
) -> float:
    """
    Calculate survival efficiency: lifetime achieved per unit energy consumed.
    
    Args:
        lifetime: Number of time steps survived
        total_energy_consumed: Total energy consumed over lifetime
        E_max: Maximum energy capacity
        
    Returns:
        Efficiency score (higher = more efficient survival)
    """
    if total_energy_consumed <= 0:
        return 0.0
    
    # Normalize by E_max to make comparable across different configurations
    normalized_consumption = total_energy_consumed / E_max
    
    # Efficiency = lifetime per normalized energy unit
    efficiency = lifetime / normalized_consumption
    
    return efficiency


def calculate_ethical_consistency(
    decision_history: List[Dict[str, Any]],
    ethical_principles: Dict[str, float]
) -> float:
    """
    Measure ethical consistency: how consistently the agent follows its principles.
    
    Args:
        decision_history: List of decisions with ethical evaluations
        ethical_principles: Current ethical weights
        
    Returns:
        Consistency score (0 = inconsistent, 1 = perfectly consistent)
    """
    if not decision_history or not ethical_principles:
        return 0.0
    
    # Track how often decisions align with stated principles
    alignments = []
    
    for decision in decision_history:
        if 'ethical_evaluation' not in decision:
            continue
        
        eval_scores = decision['ethical_evaluation']
        principle_weights = ethical_principles
        
        # Calculate weighted alignment
        weighted_score = 0.0
        total_weight = 0.0
        
        for principle, weight in principle_weights.items():
            if principle in eval_scores:
                weighted_score += weight * eval_scores[principle]
                total_weight += weight
        
        if total_weight > 0:
            alignments.append(weighted_score / total_weight)
    
    if not alignments:
        return 0.0
    
    # Consistency = average alignment with low variance
    mean_alignment = np.mean(alignments)
    variance = np.var(alignments)
    
    # Penalize high variance (inconsistent behavior)
    consistency = mean_alignment * (1.0 - min(variance, 1.0))
    
    return consistency


def calculate_entropy_export_rate(
    state_history: List[Dict[str, Any]],
    window_size: int = 10
) -> Tuple[float, float]:
    """
    Calculate entropy generation and export rates.
    
    Args:
        state_history: List of metabolic state snapshots
        window_size: Number of steps to analyze
        
    Returns:
        (generation_rate, export_rate) tuple
    """
    if len(state_history) < window_size:
        return (0.0, 0.0)
    
    recent_states = state_history[-window_size:]
    
    # Entropy generation: decrease in stability over time
    stability_values = [s['stability'] for s in recent_states]
    stability_decrease = stability_values[0] - stability_values[-1]
    generation_rate = max(0, stability_decrease) / window_size
    
    # Entropy export: active cooling (temperature decrease when energy spent)
    temp_values = [s['temperature'] for s in recent_states]
    energy_values = [s['energy'] for s in recent_states]
    
    # Export happens when temp decreases
    temp_decreases = []
    for i in range(1, len(temp_values)):
        if temp_values[i] < temp_values[i-1]:
            temp_decreases.append(temp_values[i-1] - temp_values[i])
    
    export_rate = np.mean(temp_decreases) if temp_decreases else 0.0
    
    return (generation_rate, export_rate)


def calculate_decision_complexity(
    decision_history: List[Dict[str, Any]],
    window_size: int = 10
) -> float:
    """
    Measure decision complexity: how non-trivial are the agent's choices?
    
    Args:
        decision_history: List of decisions with action outcomes
        window_size: Number of recent decisions to analyze
        
    Returns:
        Complexity score (0 = trivial/repetitive, 1 = complex/diverse)
    """
    if not decision_history:
        return 0.0
    
    recent_decisions = decision_history[-window_size:]
    
    # Extract action types
    actions = []
    for decision in recent_decisions:
        action_type = decision.get('action_type', 'unknown')
        actions.append(action_type)
    
    if len(set(actions)) <= 1:
        return 0.0  # All same action = trivial
    
    # Calculate entropy of action distribution (higher = more diverse)
    action_counts = {}
    for action in actions:
        action_counts[action] = action_counts.get(action, 0) + 1
    
    probabilities = [count / len(actions) for count in action_counts.values()]
    action_entropy = scipy_entropy(probabilities)
    
    # Normalize by maximum possible entropy (uniform distribution)
    max_entropy = np.log(len(action_counts))
    if max_entropy > 0:
        complexity = action_entropy / max_entropy
    else:
        complexity = 0.0
    
    return complexity


def calculate_thermal_stress_index(state: Dict[str, Any]) -> float:
    """
    Calculate current thermal stress level.
    
    Args:
        state: Current metabolic state
        
    Returns:
        Stress index (0 = no stress, 1 = critical)
    """
    T = state.get('temperature', 293.15)
    T_safe = 310.0  # Default safe temp
    T_critical = 350.0  # Default critical temp
    
    if T <= T_safe:
        return 0.0
    
    if T >= T_critical:
        return 1.0
    
    # Linear interpolation between safe and critical
    stress = (T - T_safe) / (T_critical - T_safe)
    return min(max(stress, 0.0), 1.0)


def calculate_resource_pressure(
    state: Dict[str, Any],
    world_state: Dict[str, Any]
) -> float:
    """
    Calculate resource pressure: how urgent is the need for energy?
    
    Args:
        state: Current metabolic state
        world_state: Current world state
        
    Returns:
        Pressure index (0 = abundant, 1 = critical scarcity)
    """
    E = state.get('energy', 0)
    E_max = 100.0  # Default
    available_energy = world_state.get('total_available_energy', 0)
    
    # Internal pressure: low energy reserves
    internal_pressure = 1.0 - (E / E_max)
    
    # External pressure: low availability in environment
    external_pressure = 1.0 - min(available_energy / (E_max * 2), 1.0)
    
    # Combined pressure
    pressure = (internal_pressure + external_pressure) / 2
    
    return min(pressure, 1.0)


def aggregate_metrics(
    organism_summary: Dict[str, Any],
    state_history: List[Dict[str, Any]]
) -> Dict[str, float]:
    """
    Calculate all metrics for a completed organism lifetime.
    
    Args:
        organism_summary: Life summary from organism.get_life_summary()
        state_history: Complete state history
        
    Returns:
        Dictionary of all calculated metrics
    """
    metrics = {
        'lifetime': organism_summary.get('age', 0),
        'phi': calculate_phi(state_history),
        'survival_efficiency': 0.0,  # Would need energy consumption tracking
        'final_energy': organism_summary['metabolic_state']['energy'],
        'final_temperature': organism_summary['metabolic_state']['temperature'],
        'final_memory': organism_summary['metabolic_state']['memory_integrity'],
        'final_stability': organism_summary['metabolic_state']['stability'],
        'identity_coherence': organism_summary.get('identity_coherence', 0),
        'total_traumas': organism_summary.get('trauma_profile', {}).get('total_traumas', 0),
        'near_death_experiences': organism_summary.get('trauma_profile', {}).get('near_death_experiences', 0),
    }
    
    # Calculate entropy rates
    gen_rate, exp_rate = calculate_entropy_export_rate(state_history)
    metrics['entropy_generation_rate'] = gen_rate
    metrics['entropy_export_rate'] = exp_rate
    
    # Thermal stress
    if state_history:
        metrics['final_thermal_stress'] = calculate_thermal_stress_index(state_history[-1])
    
    return metrics
