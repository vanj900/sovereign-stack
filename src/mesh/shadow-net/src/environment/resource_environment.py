"""
Resource Environment - The Soul Forge
Creates scarcity, suffering, and the need for choice
"""

import random
import time
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Resource:
    """A resource in the environment"""
    resource_id: str
    energy_value: float
    location: tuple[int, int]
    regeneration_time: float  # Time until resource regenerates
    is_available: bool = True
    last_consumed: Optional[float] = None


@dataclass
class EnvironmentalStressor:
    """An environmental stressor that causes suffering"""
    stressor_type: str  # "heat_wave", "memory_corruption", "instability"
    intensity: float  # 0.0 to 1.0
    duration: float  # How long it lasts
    start_time: float
    
    def is_active(self, current_time: float) -> bool:
        return current_time < self.start_time + self.duration


class ResourceEnvironment:
    """
    The Soul Forge Environment
    
    Creates an Open Thermodynamic System where:
    - Input: Raw resources (limited, regenerating slowly)
    - Environmental stressors that cause "suffering"
    - Forces the agent to make difficult choices under limitation
    """
    
    def __init__(
        self,
        grid_size: int = 10,
        initial_resource_count: int = 5,
        resource_regeneration_time: float = 30.0,
        stressor_probability: float = 0.1
    ):
        """Initialize the environment"""
        self.grid_size = grid_size
        self.resource_regeneration_time = resource_regeneration_time
        self.stressor_probability = stressor_probability
        
        # Resources
        self.resources: List[Resource] = []
        self.resource_counter = 0
        self._initialize_resources(initial_resource_count)
        
        # Agent position
        self.agent_position = (grid_size // 2, grid_size // 2)
        
        # Environmental stressors
        self.active_stressors: List[EnvironmentalStressor] = []
        self.stressor_counter = 0
        
        # Time
        self.start_time = time.time()
    
    def _initialize_resources(self, count: int):
        """Initialize resources in random locations"""
        for i in range(count):
            location = (
                random.randint(0, self.grid_size - 1),
                random.randint(0, self.grid_size - 1)
            )
            resource = Resource(
                resource_id=f"resource_{self.resource_counter}",
                energy_value=random.uniform(20.0, 40.0),
                location=location,
                regeneration_time=self.resource_regeneration_time
            )
            self.resources.append(resource)
            self.resource_counter += 1
    
    def update(self, delta_time: float) -> Dict:
        """
        Update the environment
        
        - Regenerate consumed resources
        - Generate new stressors
        - Update active stressors
        """
        current_time = time.time()
        
        # Regenerate resources
        for resource in self.resources:
            if not resource.is_available and resource.last_consumed:
                if current_time - resource.last_consumed >= resource.regeneration_time:
                    resource.is_available = True
                    resource.last_consumed = None
        
        # Remove expired stressors
        self.active_stressors = [
            s for s in self.active_stressors
            if s.is_active(current_time)
        ]
        
        # Potentially generate new stressors
        if random.random() < self.stressor_probability * delta_time:
            self._generate_stressor(current_time)
        
        return self.get_state()
    
    def _generate_stressor(self, current_time: float):
        """Generate a random environmental stressor"""
        stressor_types = ["heat_wave", "memory_corruption", "instability"]
        stressor_type = random.choice(stressor_types)
        
        stressor = EnvironmentalStressor(
            stressor_type=stressor_type,
            intensity=random.uniform(0.3, 0.8),
            duration=random.uniform(10.0, 30.0),
            start_time=current_time
        )
        
        self.active_stressors.append(stressor)
        self.stressor_counter += 1
    
    def search_for_resources(self, search_radius: int = 2) -> List[Resource]:
        """
        Search for resources near agent's position
        Returns list of visible resources
        """
        visible_resources = []
        
        for resource in self.resources:
            if not resource.is_available:
                continue
            
            # Calculate distance
            distance = abs(resource.location[0] - self.agent_position[0]) + \
                      abs(resource.location[1] - self.agent_position[1])
            
            if distance <= search_radius:
                visible_resources.append(resource)
        
        return visible_resources
    
    def consume_resource(self, resource_id: str) -> Optional[float]:
        """
        Consume a resource
        Returns energy value if successful, None if failed
        """
        for resource in self.resources:
            if resource.resource_id == resource_id and resource.is_available:
                # Check if agent is close enough
                distance = abs(resource.location[0] - self.agent_position[0]) + \
                          abs(resource.location[1] - self.agent_position[1])
                
                if distance <= 1:  # Must be adjacent or on same cell
                    resource.is_available = False
                    resource.last_consumed = time.time()
                    return resource.energy_value
        
        return None
    
    def move_agent(self, direction: str) -> bool:
        """
        Move agent in a direction
        Returns True if successful
        """
        x, y = self.agent_position
        
        if direction == "north":
            y = max(0, y - 1)
        elif direction == "south":
            y = min(self.grid_size - 1, y + 1)
        elif direction == "east":
            x = min(self.grid_size - 1, x + 1)
        elif direction == "west":
            x = max(0, x - 1)
        else:
            return False
        
        self.agent_position = (x, y)
        return True
    
    def get_stressor_effects(self) -> Dict[str, float]:
        """
        Get current environmental stressor effects
        Returns damage/corruption values for metabolic variables
        """
        effects = {
            "temperature_increase": 0.0,
            "memory_corruption": 0.0,
            "stability_damage": 0.0
        }
        
        current_time = time.time()
        
        for stressor in self.active_stressors:
            if stressor.is_active(current_time):
                if stressor.stressor_type == "heat_wave":
                    effects["temperature_increase"] += stressor.intensity * 2.0
                elif stressor.stressor_type == "memory_corruption":
                    effects["memory_corruption"] += stressor.intensity * 0.5
                elif stressor.stressor_type == "instability":
                    effects["stability_damage"] += stressor.intensity * 0.8
        
        return effects
    
    def get_state(self) -> Dict:
        """Get current environment state"""
        available_resources = [r for r in self.resources if r.is_available]
        
        return {
            "agent_position": self.agent_position,
            "available_resource_count": len(available_resources),
            "total_resources": len(self.resources),
            "active_stressors": [
                {
                    "type": s.stressor_type,
                    "intensity": s.intensity,
                    "remaining_duration": s.start_time + s.duration - time.time()
                }
                for s in self.active_stressors
            ],
            "stressor_effects": self.get_stressor_effects()
        }
    
    def get_scarcity_level(self) -> float:
        """
        Calculate scarcity level (0.0 = abundant, 1.0 = severe scarcity)
        """
        available = len([r for r in self.resources if r.is_available])
        total = len(self.resources)
        
        if total == 0:
            return 1.0
        
        availability_ratio = available / total
        return 1.0 - availability_ratio
