"""
Resource World - Thermodynamic Ecosystem

This module implements a hostile world with scarce resources that forces
genuine strategic trade-offs for survival.
"""

import random
from typing import List, Dict, Any, Optional, Tuple
import math


class EnergySource:
    """
    Represents a source of energy in the environment.
    """
    
    def __init__(
        self,
        source_id: str,
        location: Tuple[float, float],
        capacity: float,
        regen_rate: float,
        current: Optional[float] = None
    ):
        self.source_id = source_id
        self.location = location
        self.max_capacity = capacity
        self.current = current if current is not None else capacity
        self.regen_rate = regen_rate
        self.total_harvested = 0.0
        self.depletion_events = 0
    
    def harvest(self, amount: float) -> float:
        """
        Extract energy from this source.
        
        Args:
            amount: Requested amount
            
        Returns:
            Actual amount extracted
        """
        actual = min(amount, self.current)
        self.current -= actual
        self.total_harvested += actual
        
        if self.current == 0:
            self.depletion_events += 1
        
        return actual
    
    def regenerate(self, dt: float = 1.0):
        """
        Resources regenerate slowly over time.
        
        Args:
            dt: Time step
        """
        self.current = min(
            self.current + self.regen_rate * dt,
            self.max_capacity
        )
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state"""
        return {
            'source_id': self.source_id,
            'location': self.location,
            'current': self.current,
            'capacity': self.max_capacity,
            'availability': self.current / self.max_capacity if self.max_capacity > 0 else 0
        }
    
    def __repr__(self):
        return f"EnergySource({self.source_id}: {self.current:.1f}/{self.max_capacity})"


class ResourceWorld:
    """
    A thermodynamic ecosystem with scarce resources.
    
    The world is hostile by design, forcing agents to make difficult choices.
    """
    
    def __init__(
        self,
        scarcity: float = 0.5,
        num_sources: int = 3,
        world_size: Tuple[float, float] = (100.0, 100.0),
        base_regen_rate: float = 2.0
    ):
        self.scarcity = scarcity  # 0 = abundant, 1 = extreme scarcity
        self.world_size = world_size
        self.base_regen_rate = base_regen_rate
        
        # Create energy sources
        self.energy_sources = self._create_energy_sources(num_sources)
        
        # Environmental state
        self.current_temperature = 293.15  # Ambient K
        self.time_step = 0
        
        # Tracking
        self.total_energy_provided = 0.0
        self.agent_positions = {}
    
    def _create_energy_sources(self, num_sources: int) -> List[EnergySource]:
        """Create energy sources distributed in world"""
        sources = []
        
        for i in range(num_sources):
            # Random location
            location = (
                random.uniform(0, self.world_size[0]),
                random.uniform(0, self.world_size[1])
            )
            
            # Capacity affected by scarcity
            base_capacity = 100.0
            capacity = base_capacity * (1.0 - self.scarcity * 0.7)
            
            # Regen rate affected by scarcity
            regen_rate = self.base_regen_rate * (1.0 - self.scarcity * 0.5)
            
            source = EnergySource(
                source_id=f"source_{i}",
                location=location,
                capacity=capacity,
                regen_rate=regen_rate
            )
            sources.append(source)
        
        return sources
    
    def step(self, dt: float = 1.0):
        """
        Advance world state by one time step.
        
        Args:
            dt: Time delta
        """
        self.time_step += 1
        
        # Regenerate all sources
        for source in self.energy_sources:
            source.regenerate(dt)
        
        # Random environmental changes
        self._apply_environmental_changes()
    
    def _apply_environmental_changes(self):
        """Apply random environmental stressors"""
        # Occasional temperature fluctuations
        if random.random() < 0.1:
            self.current_temperature += random.uniform(-5, 10)
    
    def get_available_resources(self) -> List[Dict[str, Any]]:
        """Get list of available energy sources"""
        return [source.get_state() for source in self.energy_sources]
    
    def get_visible_resources(self, agent_position: Optional[Tuple[float, float]] = None) -> List[Dict]:
        """Get resources visible to agent (simplified - all visible for now)"""
        return self.get_available_resources()
    
    def execute_action(self, action, metabolic_engine) -> Dict[str, Any]:
        """
        Execute an action in the environment.
        
        Args:
            action: The action to execute
            metabolic_engine: Agent's metabolic engine
            
        Returns:
            Result dictionary
        """
        result = {
            'success': False,
            'energy_gained': 0.0,
            'message': ''
        }
        
        action_description = getattr(action, 'description', str(action))
        
        # Parse action type from description
        if 'Harvest' in action_description or 'survival' in str(action):
            # Harvesting energy
            target_amount = getattr(action, 'estimated_benefit', 30.0)
            energy_gained = self._harvest_energy(target_amount)
            
            metabolic_engine.replenish_energy(energy_gained)
            
            result['success'] = True
            result['energy_gained'] = energy_gained
            result['message'] = f"Harvested {energy_gained:.1f} energy"
            
        elif 'Repair memory' in action_description or 'coherence' in str(action):
            # Memory repair
            cost = getattr(action, 'estimated_cost', 15.0)
            success = metabolic_engine.repair_memory(cost)
            
            result['success'] = success
            result['message'] = "Memory repaired" if success else "Insufficient energy for repair"
            
        elif 'stability' in action_description or 'stability' in str(action):
            # Stability repair
            cost = getattr(action, 'estimated_cost', 20.0)
            success = metabolic_engine.repair_stability(cost)
            
            result['success'] = success
            result['message'] = "Stability restored" if success else "Insufficient energy for repair"
            
        elif 'Explore' in action_description or 'exploration' in str(action):
            # Exploration action
            result['success'] = True
            result['message'] = "Explored environment"
            # Exploration might reveal resources or information (simplified for now)
            
        else:
            result['message'] = "Unknown action type"
        
        return result
    
    def _harvest_energy(self, amount: float) -> float:
        """
        Harvest energy from available sources.
        
        Args:
            amount: Desired amount
            
        Returns:
            Actual amount harvested
        """
        total_harvested = 0.0
        
        # Try to harvest from sources in order
        for source in self.energy_sources:
            if total_harvested >= amount:
                break
            
            needed = amount - total_harvested
            harvested = source.harvest(needed)
            total_harvested += harvested
        
        self.total_energy_provided += total_harvested
        return total_harvested
    
    def get_world_state(self) -> Dict[str, Any]:
        """Get complete world state"""
        return {
            'time_step': self.time_step,
            'scarcity': self.scarcity,
            'temperature': self.current_temperature,
            'num_sources': len(self.energy_sources),
            'total_available_energy': sum(s.current for s in self.energy_sources),
            'sources': [s.get_state() for s in self.energy_sources]
        }
    
    def set_scarcity(self, new_scarcity: float):
        """Adjust scarcity level"""
        self.scarcity = max(0.0, min(1.0, new_scarcity))
        
        # Adjust source capacities and regen rates
        for source in self.energy_sources:
            base_capacity = 100.0
            source.max_capacity = base_capacity * (1.0 - self.scarcity * 0.7)
            source.regen_rate = self.base_regen_rate * (1.0 - self.scarcity * 0.5)
    
    def __repr__(self):
        total_energy = sum(s.current for s in self.energy_sources)
        return f"ResourceWorld(scarcity={self.scarcity:.2f}, energy={total_energy:.1f}, step={self.time_step})"
