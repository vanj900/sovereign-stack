"""
Tests for Metabolic Agent (The Body)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.metabolic.agent import MetabolicAgent, MetabolicState


def test_metabolic_agent_initialization():
    """Test that agent initializes correctly"""
    agent = MetabolicAgent(initial_energy=100.0)
    
    assert agent.state.energy == 100.0
    assert agent.state.temperature == 37.0
    assert agent.state.memory_integrity == 100.0
    assert agent.state.stability == 100.0
    assert agent.state.is_alive == True
    assert agent.identity_key is not None


def test_metabolic_tick_entropy():
    """Test that metabolic tick causes entropy (passive decay)"""
    agent = MetabolicAgent(
        initial_energy=100.0,
        energy_decay_rate=1.0,
        memory_decay_rate=0.5,
        stability_decay_rate=0.8
    )
    
    initial_energy = agent.state.energy
    initial_memory = agent.state.memory_integrity
    initial_stability = agent.state.stability
    
    agent.tick()
    
    # All variables should decay
    assert agent.state.energy < initial_energy
    assert agent.state.memory_integrity < initial_memory
    assert agent.state.stability < initial_stability


def test_action_costs_energy():
    """Test that actions cost energy and generate heat"""
    agent = MetabolicAgent(initial_energy=100.0)
    
    initial_energy = agent.state.energy
    initial_temp = agent.state.temperature
    
    success = agent.perform_action("test_action", energy_cost=10.0, heat_generated=5.0)
    
    assert success == True
    assert agent.state.energy == initial_energy - 10.0
    assert agent.state.temperature == initial_temp + 5.0


def test_fail_mode_on_zero_energy():
    """Test that agent dies when energy reaches zero"""
    agent = MetabolicAgent(initial_energy=5.0, energy_decay_rate=10.0)
    
    assert agent.state.is_alive == True
    
    # Tick should cause death
    alive = agent.tick()
    
    assert alive == False
    assert agent.state.is_alive == False
    assert agent.death_time is not None


def test_fail_mode_on_zero_stability():
    """Test that agent dies when stability reaches zero"""
    agent = MetabolicAgent(initial_energy=100.0, stability_decay_rate=50.0)
    
    # Two ticks should kill stability
    agent.tick()
    agent.tick()
    
    assert agent.state.is_alive == False


def test_cannot_act_when_dead():
    """Test that dead agents cannot perform actions"""
    agent = MetabolicAgent(initial_energy=1.0, energy_decay_rate=10.0)
    
    # Kill the agent
    agent.tick()
    assert agent.state.is_alive == False
    
    # Try to perform action
    success = agent.perform_action("test", 5.0, 0.0)
    assert success == False


def test_repair_memory():
    """Test memory repair functionality"""
    agent = MetabolicAgent(initial_energy=100.0)
    
    # Damage memory
    agent.state.memory_integrity = 50.0
    
    # Repair
    success = agent.repair_memory(cost=10.0, repair_amount=20.0)
    
    assert success == True
    assert agent.state.memory_integrity == 70.0
    assert agent.state.energy == 90.0  # Cost was paid


def test_repair_stability():
    """Test stability repair functionality"""
    agent = MetabolicAgent(initial_energy=100.0)
    
    # Damage stability
    agent.state.stability = 40.0
    
    # Repair
    success = agent.repair_stability(cost=12.0, repair_amount=25.0)
    
    assert success == True
    assert agent.state.stability == 65.0
    assert agent.state.energy == 88.0


def test_consume_resource():
    """Test resource consumption"""
    agent = MetabolicAgent(initial_energy=50.0)
    
    agent.consume_resource(30.0)
    
    assert agent.state.energy == 80.0


def test_temperature_damages_stability():
    """Test that high temperature damages stability"""
    agent = MetabolicAgent(
        initial_energy=100.0,
        temperature_damage_threshold=50.0,
        stability_decay_rate=0.1
    )
    
    # Heat up the agent
    agent.state.temperature = 60.0  # Above threshold
    
    initial_stability = agent.state.stability
    
    agent.tick()
    
    # Stability should be lower due to heat damage (in addition to normal decay)
    expected_normal_decay = 0.1
    # Heat damage = (60 - 50) * 0.1 = 1.0
    # Total loss = 0.1 + 1.0 = 1.1
    assert agent.state.stability < initial_stability - expected_normal_decay


if __name__ == "__main__":
    print("Running metabolic agent tests...")
    
    test_metabolic_agent_initialization()
    print("✓ Initialization test passed")
    
    test_metabolic_tick_entropy()
    print("✓ Entropy test passed")
    
    test_action_costs_energy()
    print("✓ Action cost test passed")
    
    test_fail_mode_on_zero_energy()
    print("✓ Energy death test passed")
    
    test_fail_mode_on_zero_stability()
    print("✓ Stability death test passed")
    
    test_cannot_act_when_dead()
    print("✓ Death prevents action test passed")
    
    test_repair_memory()
    print("✓ Memory repair test passed")
    
    test_repair_stability()
    print("✓ Stability repair test passed")
    
    test_consume_resource()
    print("✓ Resource consumption test passed")
    
    test_temperature_damages_stability()
    print("✓ Temperature damage test passed")
    
    print("\nAll metabolic agent tests passed! ✓")
