"""
Tests for Goal Manager (The Mind)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.autonomy.goal_generation.goal_manager import GoalManager, DriveType


def test_goal_manager_initialization():
    """Test that goal manager initializes correctly"""
    manager = GoalManager()
    
    assert len(manager.drives) == 4
    assert manager.goal_counter == 0
    assert len(manager.active_goals) == 0


def test_drive_urgency_calculation():
    """Test that drive urgency increases when variable is low"""
    manager = GoalManager()
    
    # Get survival drive (coupled to energy)
    survival_drive = next(d for d in manager.drives if d.drive_type == DriveType.SURVIVAL)
    
    # High energy - low urgency
    metabolic_state = {"energy": 80.0}
    manager.update_drives(metabolic_state)
    assert survival_drive.urgency < 0.3
    
    # Low energy - high urgency
    metabolic_state = {"energy": 20.0}
    manager.update_drives(metabolic_state)
    assert survival_drive.urgency >= 0.5  # At threshold, urgency is 0.5


def test_goal_generation_based_on_urgency():
    """Test that goals are generated when drives are urgent"""
    manager = GoalManager()
    
    # Low energy triggers survival goal
    metabolic_state = {
        "energy": 25.0,
        "memory_integrity": 100.0,
        "stability": 100.0
    }
    env_state = {}
    
    goals = manager.generate_goals(metabolic_state, env_state)
    
    # Should generate survival goal
    assert len(goals) > 0
    survival_goals = [g for g in goals if g.drive_type == DriveType.SURVIVAL]
    assert len(survival_goals) > 0


def test_goal_priority_reflects_urgency():
    """Test that goal priority reflects drive urgency"""
    manager = GoalManager()
    
    # Critical energy
    metabolic_state = {
        "energy": 15.0,
        "memory_integrity": 50.0,
        "stability": 80.0
    }
    env_state = {}
    
    goals = manager.generate_goals(metabolic_state, env_state)
    
    # Survival goal should have highest priority
    highest = manager.get_highest_priority_goal()
    assert highest is not None
    assert highest.drive_type == DriveType.SURVIVAL


def test_memory_integrity_drive():
    """Test that low memory integrity triggers identity drive"""
    manager = GoalManager()
    
    metabolic_state = {
        "energy": 80.0,
        "memory_integrity": 40.0,  # Low memory
        "stability": 80.0
    }
    env_state = {}
    
    goals = manager.generate_goals(metabolic_state, env_state)
    
    # Should generate identity/memory goal
    identity_goals = [g for g in goals if g.drive_type == DriveType.COHERENT_IDENTITY]
    assert len(identity_goals) > 0


def test_goal_completion():
    """Test goal completion tracking"""
    manager = GoalManager()
    
    metabolic_state = {"energy": 25.0, "memory_integrity": 100.0, "stability": 100.0}
    goals = manager.generate_goals(metabolic_state, {})
    
    initial_active = len(manager.active_goals)
    initial_completed = len(manager.completed_goals)
    
    # Complete first goal
    if manager.active_goals:
        goal_id = manager.active_goals[0].goal_id
        manager.complete_goal(goal_id)
        
        assert len(manager.active_goals) == initial_active - 1
        assert len(manager.completed_goals) == initial_completed + 1


if __name__ == "__main__":
    print("Running goal manager tests...")
    
    test_goal_manager_initialization()
    print("✓ Initialization test passed")
    
    test_drive_urgency_calculation()
    print("✓ Drive urgency test passed")
    
    test_goal_generation_based_on_urgency()
    print("✓ Goal generation test passed")
    
    test_goal_priority_reflects_urgency()
    print("✓ Goal priority test passed")
    
    test_memory_integrity_drive()
    print("✓ Memory integrity drive test passed")
    
    test_goal_completion()
    print("✓ Goal completion test passed")
    
    print("\nAll goal manager tests passed! ✓")
