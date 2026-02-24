"""
Tests for Active Inference (The Nervous System)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.inference.efe_calculator import EFECalculator, ActionSimulation


def test_efe_calculator_initialization():
    """Test EFE calculator initialization"""
    calc = EFECalculator(
        pragmatic_weight=1.0,
        epistemic_weight=0.3,
        cost_weight=1.0
    )
    
    assert calc.pragmatic_weight == 1.0
    assert calc.epistemic_weight == 0.3
    assert calc.cost_weight == 1.0


def test_action_simulation():
    """Test action simulation creation"""
    action = ActionSimulation(
        action_name="test_action",
        energy_cost=10.0,
        heat_generated=2.0,
        expected_energy_gain=20.0,
        expected_stability_change=0.0,
        expected_memory_change=0.0,
        uncertainty=0.5
    )
    
    assert action.action_name == "test_action"
    assert action.energy_cost == 10.0
    assert action.expected_energy_gain == 20.0


def test_efe_calculation():
    """Test Expected Free Energy calculation"""
    calc = EFECalculator()
    
    action = ActionSimulation(
        action_name="good_action",
        energy_cost=5.0,
        heat_generated=1.0,
        expected_energy_gain=30.0,
        expected_stability_change=0.0,
        expected_memory_change=0.0,
        uncertainty=0.2
    )
    
    current_state = {
        "energy": 50.0,
        "temperature": 37.0,
        "stability": 50.0
    }
    
    efe = calc.calculate_efe(action, current_state)
    
    # EFE should be calculated
    assert isinstance(efe, float)
    assert action.efe == efe
    assert action.pragmatic_value is not None
    assert action.epistemic_value is not None


def test_select_best_action():
    """Test that EFE selects the best action"""
    calc = EFECalculator()
    
    # Good action: net positive energy
    good_action = ActionSimulation(
        action_name="good",
        energy_cost=5.0,
        heat_generated=1.0,
        expected_energy_gain=30.0,
        expected_stability_change=0.0,
        expected_memory_change=0.0,
        uncertainty=0.2
    )
    
    # Bad action: net negative energy
    bad_action = ActionSimulation(
        action_name="bad",
        energy_cost=20.0,
        heat_generated=5.0,
        expected_energy_gain=5.0,
        expected_stability_change=-10.0,
        expected_memory_change=0.0,
        uncertainty=0.2
    )
    
    current_state = {
        "energy": 50.0,
        "temperature": 37.0,
        "stability": 50.0
    }
    
    best = calc.select_action([good_action, bad_action], current_state)
    
    # Should select the good action (lower EFE)
    assert best.action_name == "good"


def test_predictive_processing():
    """Test outcome simulation"""
    calc = EFECalculator()
    
    action = ActionSimulation(
        action_name="test",
        energy_cost=10.0,
        heat_generated=5.0,
        expected_energy_gain=20.0,
        expected_stability_change=0.0,
        expected_memory_change=0.0,
        uncertainty=0.2
    )
    
    current_state = {
        "energy": 50.0,
        "temperature": 37.0,
        "stability": 80.0,
        "memory_integrity": 90.0
    }
    
    predicted = calc.simulate_outcome(action, current_state)
    
    # Check predictions
    assert predicted["energy"] == 60.0  # 50 - 10 + 20
    assert predicted["temperature"] == 42.0  # 37 + 5
    assert predicted["will_survive"] == True


def test_should_not_execute_lethal_action():
    """Test that lethal actions are rejected"""
    calc = EFECalculator()
    
    lethal_action = ActionSimulation(
        action_name="lethal",
        energy_cost=100.0,
        heat_generated=0.0,
        expected_energy_gain=0.0,
        expected_stability_change=0.0,
        expected_memory_change=0.0,
        uncertainty=0.0
    )
    
    current_state = {
        "energy": 50.0,
        "temperature": 37.0,
        "stability": 50.0
    }
    
    should_execute, reasoning = calc.should_execute_action(lethal_action, current_state)
    
    assert should_execute == False
    assert "death" in reasoning.lower()


def test_action_comparison():
    """Test comparing multiple actions"""
    calc = EFECalculator()
    
    actions = [
        ActionSimulation("a1", 5.0, 1.0, 20.0, 0.0, 0.0, 0.2),
        ActionSimulation("a2", 10.0, 2.0, 15.0, 0.0, 0.0, 0.3),
        ActionSimulation("a3", 15.0, 3.0, 10.0, 0.0, 0.0, 0.4),
    ]
    
    current_state = {
        "energy": 50.0,
        "temperature": 37.0,
        "stability": 50.0
    }
    
    comparison = calc.compare_actions(actions, current_state)
    
    # Should return sorted list
    assert len(comparison) == 3
    assert all("efe" in result for result in comparison)
    assert all("will_survive" in result for result in comparison)


if __name__ == "__main__":
    print("Running active inference tests...")
    
    test_efe_calculator_initialization()
    print("✓ Initialization test passed")
    
    test_action_simulation()
    print("✓ Action simulation test passed")
    
    test_efe_calculation()
    print("✓ EFE calculation test passed")
    
    test_select_best_action()
    print("✓ Action selection test passed")
    
    test_predictive_processing()
    print("✓ Predictive processing test passed")
    
    test_should_not_execute_lethal_action()
    print("✓ Lethal action rejection test passed")
    
    test_action_comparison()
    print("✓ Action comparison test passed")
    
    print("\nAll active inference tests passed! ✓")
