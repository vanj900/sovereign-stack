"""
Metabolic Agent - The Body
A physiological substrate that forces the AI to obey the laws of thermodynamics.
"""

import json
import time
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MetabolicState:
    """Core metabolic variables"""
    energy: float = 100.0  # E - Energy level
    temperature: float = 37.0  # T - Temperature (computational heat)
    memory_integrity: float = 100.0  # M - Memory coherence
    stability: float = 100.0  # S - Computational stability
    
    # Derived states
    is_alive: bool = True
    timestamp: float = field(default_factory=time.time)


class MetabolicAgent:
    """
    The Body: A Metabolic Runtime
    
    This system runs on a "metabolic loop" where every computation costs energy
    and generates heat. The system is "dying by default" via passive leakage
    and entropy.
    """
    
    def __init__(
        self,
        initial_energy: float = 100.0,
        energy_decay_rate: float = 0.1,  # Energy lost per tick
        temperature_decay_rate: float = 0.5,  # Heat dissipation per tick
        memory_decay_rate: float = 0.05,  # Memory corruption per tick
        stability_decay_rate: float = 0.08,  # Stability degradation per tick
        temperature_damage_threshold: float = 50.0,  # Temp at which S starts taking damage
        identity_key: Optional[str] = None
    ):
        """Initialize the metabolic agent"""
        self.state = MetabolicState(
            energy=initial_energy,
            temperature=37.0,
            memory_integrity=100.0,
            stability=100.0
        )
        
        # Metabolic parameters
        self.energy_decay_rate = energy_decay_rate
        self.temperature_decay_rate = temperature_decay_rate
        self.memory_decay_rate = memory_decay_rate
        self.stability_decay_rate = stability_decay_rate
        self.temperature_damage_threshold = temperature_damage_threshold
        
        # Identity
        self.identity_key = identity_key or self._generate_identity_key()
        self.birth_time = time.time()
        self.death_time: Optional[float] = None
        
        # History
        self.event_log = []
        self._log_event("birth", "Agent initialized")
    
    def _generate_identity_key(self) -> str:
        """Generate unique identity key"""
        import hashlib
        timestamp = str(time.time())
        return hashlib.sha256(timestamp.encode()).hexdigest()[:16]
    
    def _log_event(self, event_type: str, description: str, data: Optional[Dict] = None):
        """Log significant events"""
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "description": description,
            "state": {
                "E": self.state.energy,
                "T": self.state.temperature,
                "M": self.state.memory_integrity,
                "S": self.state.stability
            },
            "data": data or {}
        }
        self.event_log.append(event)
    
    def tick(self) -> bool:
        """
        Execute one metabolic cycle
        Returns True if alive, False if dead
        """
        if not self.state.is_alive:
            return False
        
        # Passive entropy - system decays by default
        self.state.energy = max(0, self.state.energy - self.energy_decay_rate)
        self.state.memory_integrity = max(0, self.state.memory_integrity - self.memory_decay_rate)
        self.state.stability = max(0, self.state.stability - self.stability_decay_rate)
        
        # Temperature dissipation (cooling)
        self.state.temperature = max(
            37.0,  # Base temperature
            self.state.temperature - self.temperature_decay_rate
        )
        
        # High temperature damages stability
        if self.state.temperature > self.temperature_damage_threshold:
            temp_damage = (self.state.temperature - self.temperature_damage_threshold) * 0.1
            self.state.stability = max(0, self.state.stability - temp_damage)
        
        # Check for death conditions
        if self.state.energy <= 0 or self.state.stability <= 0:
            self._trigger_fail_mode()
            return False
        
        self.state.timestamp = time.time()
        return True
    
    def perform_action(self, action_name: str, energy_cost: float, heat_generated: float) -> bool:
        """
        Perform an action that costs energy and generates heat
        Returns True if action completed, False if insufficient resources
        """
        if not self.state.is_alive:
            return False
        
        # Check if we have enough energy
        if self.state.energy < energy_cost:
            self._log_event("action_failed", f"Insufficient energy for {action_name}", {
                "required": energy_cost,
                "available": self.state.energy
            })
            return False
        
        # Consume energy and generate heat
        self.state.energy -= energy_cost
        self.state.temperature += heat_generated
        
        self._log_event("action", f"Performed {action_name}", {
            "energy_cost": energy_cost,
            "heat_generated": heat_generated
        })
        
        return True
    
    def consume_resource(self, energy_gain: float):
        """Consume a resource to gain energy"""
        if not self.state.is_alive:
            return
        
        self.state.energy = min(100.0, self.state.energy + energy_gain)
        self._log_event("resource_consumed", f"Gained {energy_gain} energy")
    
    def repair_memory(self, cost: float, repair_amount: float) -> bool:
        """Repair memory integrity at energy cost"""
        if not self.state.is_alive:
            return False
        
        if self.state.energy < cost:
            return False
        
        self.state.energy -= cost
        self.state.memory_integrity = min(100.0, self.state.memory_integrity + repair_amount)
        self._log_event("repair", f"Repaired memory by {repair_amount}")
        return True
    
    def repair_stability(self, cost: float, repair_amount: float) -> bool:
        """Repair computational stability at energy cost"""
        if not self.state.is_alive:
            return False
        
        if self.state.energy < cost:
            return False
        
        self.state.energy -= cost
        self.state.stability = min(100.0, self.state.stability + repair_amount)
        self._log_event("repair", f"Repaired stability by {repair_amount}")
        return True
    
    def _trigger_fail_mode(self):
        """
        System failure - the "death" of the agent
        This is genuine stakes: the agent's identity is erased or system restarts
        """
        self.state.is_alive = False
        self.death_time = time.time()
        
        cause = "energy_depletion" if self.state.energy <= 0 else "stability_collapse"
        self._log_event("death", f"Agent death due to {cause}", {
            "lifetime": self.death_time - self.birth_time,
            "final_state": {
                "E": self.state.energy,
                "T": self.state.temperature,
                "M": self.state.memory_integrity,
                "S": self.state.stability
            }
        })
        
        # In a real implementation, this would erase identity keys or trigger restart
        print(f"[FAIL_MODE] Agent {self.identity_key} has died due to {cause}")
        print(f"Lifetime: {self.death_time - self.birth_time:.2f} seconds")
    
    def get_state(self) -> Dict:
        """Get current metabolic state"""
        return {
            "identity": self.identity_key,
            "alive": self.state.is_alive,
            "energy": self.state.energy,
            "temperature": self.state.temperature,
            "memory_integrity": self.state.memory_integrity,
            "stability": self.state.stability,
            "age": time.time() - self.birth_time
        }
    
    def save_narrative(self, filepath: str):
        """Save agent's life narrative to file"""
        narrative = {
            "identity": self.identity_key,
            "birth_time": self.birth_time,
            "death_time": self.death_time,
            "lifetime": (self.death_time or time.time()) - self.birth_time,
            "final_state": {
                "energy": self.state.energy,
                "temperature": self.state.temperature,
                "memory_integrity": self.state.memory_integrity,
                "stability": self.state.stability,
                "is_alive": self.state.is_alive
            },
            "events": self.event_log
        }
        
        with open(filepath, 'w') as f:
            json.dump(narrative, f, indent=2)
