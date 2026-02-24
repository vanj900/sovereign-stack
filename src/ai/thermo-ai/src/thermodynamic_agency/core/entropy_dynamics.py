"""
Entropy Dynamics - Passive Decay and Heat Generation

This module implements the thermodynamic processes that cause the agent
to "die by default" through entropy and passive energy leakage.
"""

import random
from typing import Dict, Any, Optional


class EntropySimulator:
    """
    Simulates environmental entropy and stochastic degradation events.
    
    The world is hostile by default, constantly attacking the agent's integrity.
    """
    
    def __init__(
        self,
        heat_wave_probability: float = 0.05,
        heat_wave_magnitude: float = 10.0,
        corruption_probability: float = 0.03,
        corruption_magnitude: float = 0.05,
        resource_depletion_rate: float = 0.1
    ):
        self.heat_wave_probability = heat_wave_probability
        self.heat_wave_magnitude = heat_wave_magnitude
        self.corruption_probability = corruption_probability
        self.corruption_magnitude = corruption_magnitude
        self.resource_depletion_rate = resource_depletion_rate
        
        self.events_log = []
    
    def apply_environmental_stress(self, metabolic_engine) -> Dict[str, Any]:
        """
        Apply random environmental stressors to the agent.
        
        Args:
            metabolic_engine: The agent's MetabolicEngine instance
            
        Returns:
            Dictionary describing what happened
        """
        events = {}
        
        # Heat wave (sudden temperature spike)
        if random.random() < self.heat_wave_probability:
            temp_increase = random.uniform(0, self.heat_wave_magnitude)
            metabolic_engine.T += temp_increase
            events['heat_wave'] = temp_increase
            self.events_log.append({
                'type': 'heat_wave',
                'magnitude': temp_increase,
                'age': metabolic_engine.age
            })
        
        # Random memory corruption
        if random.random() < self.corruption_probability:
            corruption = random.uniform(0, self.corruption_magnitude)
            metabolic_engine.M = max(0, metabolic_engine.M - corruption)
            events['memory_corruption'] = corruption
            self.events_log.append({
                'type': 'memory_corruption',
                'magnitude': corruption,
                'age': metabolic_engine.age
            })
        
        return events
    
    def get_entropy_pressure(self, age: float) -> float:
        """
        Calculate entropy pressure that increases with age.
        
        Older agents experience more entropy.
        
        Args:
            age: Current age of the agent
            
        Returns:
            Multiplier for entropy effects
        """
        # Entropy pressure increases logarithmically with age
        base_pressure = 1.0
        age_factor = 1.0 + (0.1 * (age ** 0.5))  # Square root growth
        return base_pressure * age_factor


class PassiveDecay:
    """
    Implements passive energy leakage and natural degradation.
    
    This is what makes the agent "dying by default" - without action,
    everything decays toward equilibrium (death).
    """
    
    @staticmethod
    def calculate_energy_leak(
        current_energy: float,
        leak_rate: float,
        dt: float
    ) -> float:
        """
        Calculate passive energy loss.
        
        Energy leaks out of the system continuously, requiring constant
        replenishment to survive.
        """
        return leak_rate * dt
    
    @staticmethod
    def calculate_memory_decay(
        current_memory: float,
        decay_rate: float,
        temperature: float,
        safe_temp: float,
        dt: float
    ) -> float:
        """
        Calculate memory degradation over time.
        
        Memory decays faster at higher temperatures (like real hardware).
        """
        base_decay = decay_rate * dt
        
        # Accelerated decay from overheating
        if temperature > safe_temp:
            thermal_factor = 1.0 + (temperature - safe_temp) / safe_temp
            return base_decay * thermal_factor
        
        return base_decay
    
    @staticmethod
    def calculate_stability_decay(
        current_stability: float,
        decay_rate: float,
        operations_count: int,
        dt: float
    ) -> float:
        """
        Calculate stability (entropy resistance) decay.
        
        More operations = more wear and tear on the system.
        """
        base_decay = decay_rate * dt
        
        # Operations add cumulative wear
        operation_factor = 1.0 + (operations_count * 0.0001)
        
        return base_decay * operation_factor


class HeatDynamics:
    """
    Implements thermodynamic heat generation and dissipation.
    """
    
    @staticmethod
    def heat_from_computation(
        energy_spent: float,
        heat_coefficient: float
    ) -> float:
        """
        Calculate heat generated from computation.
        
        All computation generates waste heat (Second Law of Thermodynamics).
        """
        return heat_coefficient * energy_spent
    
    @staticmethod
    def heat_dissipation(
        current_temp: float,
        ambient_temp: float,
        dissipation_rate: float,
        dt: float
    ) -> float:
        """
        Calculate heat dissipation via Newton's law of cooling.
        
        Temperature naturally moves toward ambient, but slowly.
        """
        temp_difference = current_temp - ambient_temp
        cooling = dissipation_rate * temp_difference * dt
        return cooling
    
    @staticmethod
    def thermal_damage_threshold(
        temperature: float,
        critical_temp: float,
        safe_temp: float
    ) -> float:
        """
        Calculate damage multiplier from overheating.
        
        Returns:
            Multiplier >= 1.0, higher means more damage
        """
        if temperature < safe_temp:
            return 1.0
        elif temperature >= critical_temp:
            return 10.0  # Catastrophic damage
        else:
            # Linear interpolation between safe and critical
            danger_range = critical_temp - safe_temp
            over_safe = temperature - safe_temp
            return 1.0 + (9.0 * (over_safe / danger_range))


class ThermodynamicLaws:
    """
    Enforces fundamental thermodynamic constraints.
    """
    
    @staticmethod
    def energy_conservation_check(
        initial_energy: float,
        final_energy: float,
        energy_spent: float,
        energy_gained: float,
        tolerance: float = 0.01
    ) -> bool:
        """
        Verify energy conservation.
        
        For debugging: ensure no energy is created or destroyed improperly.
        """
        expected_final = initial_energy - energy_spent + energy_gained
        difference = abs(final_energy - expected_final)
        return difference <= tolerance
    
    @staticmethod
    def entropy_must_increase(
        initial_entropy: float,
        final_entropy: float
    ) -> bool:
        """
        Verify Second Law: entropy never decreases on its own.
        
        (Repair operations can reduce entropy, but they cost energy)
        """
        return final_entropy >= initial_entropy or final_entropy == 0.0
    
    @staticmethod
    def calculate_minimum_energy_for_survival(
        metabolic_rate: float,
        time_horizon: float
    ) -> float:
        """
        Calculate minimum energy needed to survive for a given time.
        
        This helps the agent make survival predictions.
        """
        return metabolic_rate * time_horizon
