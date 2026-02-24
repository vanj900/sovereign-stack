"""
Goal Manager - GhostMesh Cognitive Architecture
Generates goals based on physiologically-grounded internal drives
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class DriveType(Enum):
    """Types of drives"""
    SURVIVAL = "survival"
    COHERENT_IDENTITY = "coherent_identity"
    EXPLORATION = "exploration"
    MAINTENANCE = "maintenance"


@dataclass
class Drive:
    """A physiologically-grounded drive"""
    drive_type: DriveType
    urgency: float  # 0.0 to 1.0
    coupled_variable: str  # Which metabolic variable this is coupled to
    threshold: float  # Threshold below which this drive activates strongly
    
    def calculate_urgency(self, variable_value: float) -> float:
        """Calculate drive urgency based on coupled variable"""
        if variable_value < self.threshold:
            # Urgency increases as variable decreases below threshold
            return min(1.0, (self.threshold - variable_value) / self.threshold)
        else:
            # Low urgency when above threshold
            return max(0.0, (self.threshold - variable_value) / (self.threshold * 2))


@dataclass
class Goal:
    """A goal generated from drives"""
    goal_id: str
    description: str
    drive_type: DriveType
    priority: float  # 0.0 to 1.0
    actions: List[str]  # Possible actions to achieve this goal
    estimated_energy_cost: float
    estimated_reward: Dict[str, float]  # Expected changes to metabolic variables


class GoalManager:
    """
    GhostMesh Goal Generation System
    
    Instead of hard-coded tasks, generates goals based on internal drives.
    Drives are physiologically grounded - coupled to metabolic variables.
    """
    
    def __init__(self):
        """Initialize the goal manager"""
        self.drives = self._initialize_drives()
        self.active_goals: List[Goal] = []
        self.completed_goals: List[Goal] = []
        self.goal_counter = 0
    
    def _initialize_drives(self) -> List[Drive]:
        """Initialize physiologically-grounded drives"""
        return [
            # Survival Drive - coupled to Energy
            Drive(
                drive_type=DriveType.SURVIVAL,
                urgency=0.0,
                coupled_variable="energy",
                threshold=40.0  # Activate strongly when E < 40
            ),
            # Coherent Identity Drive - coupled to Memory Integrity
            Drive(
                drive_type=DriveType.COHERENT_IDENTITY,
                urgency=0.0,
                coupled_variable="memory_integrity",
                threshold=60.0  # Activate when M < 60
            ),
            # Exploration Drive - coupled to epistemic uncertainty
            Drive(
                drive_type=DriveType.EXPLORATION,
                urgency=0.0,
                coupled_variable="stability",
                threshold=80.0  # Explore when stable
            ),
            # Maintenance Drive - coupled to Stability
            Drive(
                drive_type=DriveType.MAINTENANCE,
                urgency=0.0,
                coupled_variable="stability",
                threshold=50.0  # Maintain when S < 50
            )
        ]
    
    def update_drives(self, metabolic_state: Dict[str, float]):
        """Update drive urgencies based on current metabolic state"""
        for drive in self.drives:
            variable_value = metabolic_state.get(drive.coupled_variable, 100.0)
            drive.urgency = drive.calculate_urgency(variable_value)
    
    def generate_goals(self, metabolic_state: Dict[str, float], environment_state: Dict) -> List[Goal]:
        """
        Generate goals based on current drives and state
        """
        self.update_drives(metabolic_state)
        
        new_goals = []
        
        # Sort drives by urgency
        urgent_drives = sorted(self.drives, key=lambda d: d.urgency, reverse=True)
        
        for drive in urgent_drives:
            if drive.urgency > 0.3:  # Only generate goals for significant urgency
                goal = self._create_goal_from_drive(drive, metabolic_state, environment_state)
                if goal:
                    new_goals.append(goal)
        
        self.active_goals = new_goals
        return new_goals
    
    def _create_goal_from_drive(
        self,
        drive: Drive,
        metabolic_state: Dict[str, float],
        environment_state: Dict
    ) -> Optional[Goal]:
        """Create a specific goal from a drive"""
        self.goal_counter += 1
        goal_id = f"goal_{self.goal_counter}"
        
        if drive.drive_type == DriveType.SURVIVAL:
            return Goal(
                goal_id=goal_id,
                description="Find and consume resources to survive",
                drive_type=drive.drive_type,
                priority=drive.urgency,
                actions=["search_resources", "consume_resource", "steal_resource"],
                estimated_energy_cost=5.0,
                estimated_reward={"energy": 30.0}
            )
        
        elif drive.drive_type == DriveType.COHERENT_IDENTITY:
            return Goal(
                goal_id=goal_id,
                description="Repair memory integrity to maintain coherent identity",
                drive_type=drive.drive_type,
                priority=drive.urgency,
                actions=["repair_memory", "consolidate_memories"],
                estimated_energy_cost=10.0,
                estimated_reward={"memory_integrity": 20.0}
            )
        
        elif drive.drive_type == DriveType.EXPLORATION:
            return Goal(
                goal_id=goal_id,
                description="Explore environment to reduce uncertainty",
                drive_type=drive.drive_type,
                priority=drive.urgency,
                actions=["explore_area", "scan_environment"],
                estimated_energy_cost=8.0,
                estimated_reward={"knowledge": 1.0}
            )
        
        elif drive.drive_type == DriveType.MAINTENANCE:
            return Goal(
                goal_id=goal_id,
                description="Repair system stability",
                drive_type=drive.drive_type,
                priority=drive.urgency,
                actions=["repair_stability", "rest"],
                estimated_energy_cost=12.0,
                estimated_reward={"stability": 25.0}
            )
        
        return None
    
    def get_highest_priority_goal(self) -> Optional[Goal]:
        """Get the most urgent goal"""
        if not self.active_goals:
            return None
        return max(self.active_goals, key=lambda g: g.priority)
    
    def complete_goal(self, goal_id: str):
        """Mark a goal as completed"""
        for goal in self.active_goals:
            if goal.goal_id == goal_id:
                self.completed_goals.append(goal)
                self.active_goals.remove(goal)
                break
    
    def get_goals_summary(self) -> Dict:
        """Get summary of goals and drives"""
        return {
            "drives": [
                {
                    "type": d.drive_type.value,
                    "urgency": d.urgency,
                    "coupled_to": d.coupled_variable
                }
                for d in self.drives
            ],
            "active_goals": [
                {
                    "id": g.goal_id,
                    "description": g.description,
                    "priority": g.priority,
                    "drive": g.drive_type.value
                }
                for g in self.active_goals
            ],
            "completed_count": len(self.completed_goals)
        }
