"""
Goal Manager - Physiologically-Grounded Drives

This module implements autonomous goal generation based on metabolic state.
Drives are not arbitrary rewards, but genuine survival imperatives.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
import random


class DriveType(Enum):
    """Types of drives that motivate the agent"""
    SURVIVAL = "survival"  # Coupled to Energy
    COHERENCE = "coherence"  # Coupled to Memory
    STABILITY = "stability"  # Coupled to Entropy resistance
    EXPLORATION = "exploration"  # Coupled to Uncertainty


class Drive:
    """
    Represents a motivational drive with physiological grounding.
    """
    
    def __init__(
        self,
        drive_type: DriveType,
        urgency: float = 0.0,
        threshold_critical: float = 0.8,
        threshold_high: float = 0.6,
        threshold_medium: float = 0.4
    ):
        self.drive_type = drive_type
        self.urgency = urgency  # 0-1, how urgent this drive is
        self.threshold_critical = threshold_critical
        self.threshold_high = threshold_high
        self.threshold_medium = threshold_medium
        self.history = []
    
    def update_urgency(self, new_urgency: float):
        """Update urgency and record in history"""
        self.urgency = max(0.0, min(1.0, new_urgency))
        self.history.append(self.urgency)
    
    def get_priority_level(self) -> str:
        """Get priority level based on urgency"""
        if self.urgency >= self.threshold_critical:
            return "critical"
        elif self.urgency >= self.threshold_high:
            return "high"
        elif self.urgency >= self.threshold_medium:
            return "medium"
        else:
            return "low"
    
    def __repr__(self):
        return f"Drive({self.drive_type.value}: {self.urgency:.2f} [{self.get_priority_level()}])"


class Goal:
    """
    Represents a specific goal generated from drives.
    """
    
    def __init__(
        self,
        goal_id: str,
        description: str,
        drive_type: DriveType,
        priority: float,
        estimated_cost: float,
        estimated_benefit: float
    ):
        self.goal_id = goal_id
        self.description = description
        self.drive_type = drive_type
        self.priority = priority
        self.estimated_cost = estimated_cost
        self.estimated_benefit = estimated_benefit
        self.status = "pending"  # pending, active, completed, abandoned
        self.outcome = None
    
    def get_expected_value(self) -> float:
        """Calculate expected value: benefit - cost"""
        return self.estimated_benefit - self.estimated_cost
    
    def __repr__(self):
        return (f"Goal({self.goal_id}: {self.description}, "
                f"priority={self.priority:.2f}, value={self.get_expected_value():.2f})")


class GoalManager:
    """
    Manages autonomous goal generation based on physiological state.
    
    Unlike traditional AI with fixed reward functions, this system
    generates goals dynamically based on what the body needs to survive.
    """
    
    def __init__(self):
        # Initialize drives
        self.drives = {
            DriveType.SURVIVAL: Drive(DriveType.SURVIVAL),
            DriveType.COHERENCE: Drive(DriveType.COHERENCE),
            DriveType.STABILITY: Drive(DriveType.STABILITY),
            DriveType.EXPLORATION: Drive(DriveType.EXPLORATION)
        }
        
        self.active_goals = []
        self.completed_goals = []
        self.abandoned_goals = []
        self.goal_counter = 0
    
    def update_drives_from_metabolic_state(self, metabolic_engine):
        """
        Update drive urgencies based on metabolic state.
        
        This is where the Mind-Body coupling happens.
        
        Args:
            metabolic_engine: The MetabolicEngine instance
        """
        # Survival drive: inverse of energy ratio
        energy_ratio = metabolic_engine.E / metabolic_engine.E_max
        survival_urgency = 1.0 - energy_ratio
        self.drives[DriveType.SURVIVAL].update_urgency(survival_urgency)
        
        # Coherence drive: inverse of memory integrity
        coherence_urgency = 1.0 - metabolic_engine.M
        self.drives[DriveType.COHERENCE].update_urgency(coherence_urgency)
        
        # Stability drive: inverse of stability
        stability_urgency = 1.0 - metabolic_engine.S
        self.drives[DriveType.STABILITY].update_urgency(stability_urgency)
        
        # Exploration drive: decreases with danger, increases when safe
        survival_prob = metabolic_engine.get_survival_probability()
        if survival_prob > 0.6:
            # Safe enough to explore
            exploration_urgency = 0.3 * (survival_prob - 0.6) / 0.4
        else:
            # Too dangerous to explore
            exploration_urgency = 0.0
        self.drives[DriveType.EXPLORATION].update_urgency(exploration_urgency)
    
    def generate_goals(self, metabolic_engine, environment=None) -> List[Goal]:
        """
        Generate goals based on current drives and state.
        
        Args:
            metabolic_engine: Current metabolic state
            environment: Optional environment context
            
        Returns:
            List of newly generated goals
        """
        new_goals = []
        
        # Survival goals (energy-related)
        if self.drives[DriveType.SURVIVAL].get_priority_level() in ["critical", "high"]:
            goal = self._generate_survival_goal(metabolic_engine)
            if goal:
                new_goals.append(goal)
        
        # Coherence goals (memory repair)
        if self.drives[DriveType.COHERENCE].get_priority_level() in ["critical", "high"]:
            goal = self._generate_coherence_goal(metabolic_engine)
            if goal:
                new_goals.append(goal)
        
        # Stability goals (entropy reduction)
        if self.drives[DriveType.STABILITY].get_priority_level() in ["critical", "high"]:
            goal = self._generate_stability_goal(metabolic_engine)
            if goal:
                new_goals.append(goal)
        
        # Exploration goals (when safe)
        if self.drives[DriveType.EXPLORATION].get_priority_level() in ["medium", "high"]:
            goal = self._generate_exploration_goal(metabolic_engine)
            if goal:
                new_goals.append(goal)
        
        # Add to active goals
        self.active_goals.extend(new_goals)
        
        return new_goals
    
    def _generate_survival_goal(self, metabolic_engine) -> Optional[Goal]:
        """Generate a goal to increase energy"""
        self.goal_counter += 1
        
        urgency = self.drives[DriveType.SURVIVAL].urgency
        
        # Estimate how much energy we need
        energy_deficit = metabolic_engine.E_max - metabolic_engine.E
        target_energy = min(50.0, energy_deficit)  # Harvest up to 50 units
        
        return Goal(
            goal_id=f"survival_{self.goal_counter}",
            description=f"Harvest {target_energy:.1f} energy units",
            drive_type=DriveType.SURVIVAL,
            priority=urgency,
            estimated_cost=5.0,  # Movement and harvesting cost
            estimated_benefit=target_energy
        )
    
    def _generate_coherence_goal(self, metabolic_engine) -> Optional[Goal]:
        """Generate a goal to repair memory"""
        self.goal_counter += 1
        
        urgency = self.drives[DriveType.COHERENCE].urgency
        
        # Memory repair is expensive but necessary
        repair_cost = 15.0
        
        # Benefit is proportional to how much memory we've lost
        memory_loss = 1.0 - metabolic_engine.M
        benefit = memory_loss * 50.0  # High value because identity is at stake
        
        return Goal(
            goal_id=f"coherence_{self.goal_counter}",
            description=f"Repair memory corruption ({memory_loss*100:.1f}% lost)",
            drive_type=DriveType.COHERENCE,
            priority=urgency,
            estimated_cost=repair_cost,
            estimated_benefit=benefit
        )
    
    def _generate_stability_goal(self, metabolic_engine) -> Optional[Goal]:
        """Generate a goal to repair stability"""
        self.goal_counter += 1
        
        urgency = self.drives[DriveType.STABILITY].urgency
        
        repair_cost = 20.0
        
        stability_loss = 1.0 - metabolic_engine.S
        benefit = stability_loss * 60.0  # Very high value, stability is life
        
        return Goal(
            goal_id=f"stability_{self.goal_counter}",
            description=f"Restore system stability ({stability_loss*100:.1f}% lost)",
            drive_type=DriveType.STABILITY,
            priority=urgency,
            estimated_cost=repair_cost,
            estimated_benefit=benefit
        )
    
    def _generate_exploration_goal(self, metabolic_engine) -> Optional[Goal]:
        """Generate a goal to explore and gather information"""
        self.goal_counter += 1
        
        urgency = self.drives[DriveType.EXPLORATION].urgency
        
        return Goal(
            goal_id=f"exploration_{self.goal_counter}",
            description="Explore environment for new resources",
            drive_type=DriveType.EXPLORATION,
            priority=urgency,
            estimated_cost=10.0,
            estimated_benefit=30.0  # Uncertain but potentially valuable
        )
    
    def prioritize_goals(self) -> List[Goal]:
        """
        Sort active goals by priority and expected value.
        
        Returns:
            Sorted list of goals
        """
        # Sort by priority first, then by expected value
        return sorted(
            self.active_goals,
            key=lambda g: (g.priority, g.get_expected_value()),
            reverse=True
        )
    
    def complete_goal(self, goal: Goal, outcome: Any):
        """Mark a goal as completed"""
        goal.status = "completed"
        goal.outcome = outcome
        if goal in self.active_goals:
            self.active_goals.remove(goal)
        self.completed_goals.append(goal)
    
    def abandon_goal(self, goal: Goal, reason: str):
        """Mark a goal as abandoned"""
        goal.status = "abandoned"
        goal.outcome = {"reason": reason}
        if goal in self.active_goals:
            self.active_goals.remove(goal)
        self.abandoned_goals.append(goal)
    
    def get_most_urgent_drive(self) -> Drive:
        """Get the drive with highest urgency"""
        return max(self.drives.values(), key=lambda d: d.urgency)
    
    def get_drives_summary(self) -> Dict[str, Any]:
        """Get summary of all drives"""
        return {
            drive_type.value: {
                'urgency': drive.urgency,
                'priority_level': drive.get_priority_level()
            }
            for drive_type, drive in self.drives.items()
        }
    
    def __repr__(self):
        summary = "GoalManager:\n"
        summary += "  Drives:\n"
        for drive_type, drive in self.drives.items():
            summary += f"    {drive}\n"
        summary += f"  Active Goals: {len(self.active_goals)}\n"
        summary += f"  Completed: {len(self.completed_goals)}, Abandoned: {len(self.abandoned_goals)}\n"
        return summary
