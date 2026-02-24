"""
Bio-Digital Organism
Integration of Body, Mind, and Nervous System
"""

import time
import json
from typing import Dict, List, Optional
from pathlib import Path

from ..metabolic.agent import MetabolicAgent
from ..autonomy.goal_generation.goal_manager import GoalManager
from ..autonomy.moral_reasoning.engine import EthicalEngine, Action
from ..inference.efe_calculator import EFECalculator, ActionSimulation
from ..environment.resource_environment import ResourceEnvironment


class BioDigitalOrganism:
    """
    Bio-Digital Organism
    
    A thermodynamic intelligence that possesses a "body" (metabolic spine)
    and a "mind" (GhostMesh), integrated so the mind must constantly solve
    the problem of the body's survival to exist.
    
    This is not a chatbot or standard AI agent. It is a system that:
    - Obeys the laws of thermodynamics
    - Dies by default via entropy
    - Must make difficult choices under limitation
    - Forges a "soul" through suffering, scarcity, and persistence
    """
    
    def __init__(
        self,
        initial_energy: float = 100.0,
        environment_size: int = 10,
        identity_principles: Optional[List[str]] = None,
        output_dir: str = "./narratives"
    ):
        """Initialize the Bio-Digital Organism"""
        # The Body: Metabolic Runtime
        self.body = MetabolicAgent(initial_energy=initial_energy)
        
        # The Mind: GhostMesh Cognitive Architecture
        self.mind_goals = GoalManager()
        self.mind_ethics = EthicalEngine(identity_principles=identity_principles)
        
        # The Nervous System: Active Inference
        self.nervous_system = EFECalculator()
        
        # The Environment: Soul Forge
        self.environment = ResourceEnvironment(grid_size=environment_size)
        
        # System state
        self.cycle_count = 0
        self.narrative_events = []
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.tick_duration = 1.0  # seconds per metabolic cycle
        
        self._log_narrative_event("genesis", "Bio-Digital Organism initialized")
    
    def _log_narrative_event(self, event_type: str, description: str, data: Optional[Dict] = None):
        """Log event to the organism's narrative"""
        event = {
            "cycle": self.cycle_count,
            "timestamp": time.time(),
            "type": event_type,
            "description": description,
            "state": self.body.get_state(),
            "data": data or {}
        }
        self.narrative_events.append(event)
    
    def run_cycle(self) -> bool:
        """
        Run one complete cycle of the organism
        
        Returns True if organism is alive, False if dead
        """
        self.cycle_count += 1
        
        # 1. Update environment and apply stressors
        env_state = self.environment.update(self.tick_duration)
        self._apply_environmental_stressors(env_state)
        
        # 2. Body metabolic tick (passive entropy)
        if not self.body.tick():
            self._log_narrative_event("death", "Organism has died")
            return False  # Dead
        
        # 3. Mind generates goals based on body state
        metabolic_state = self.body.get_state()
        goals = self.mind_goals.generate_goals(metabolic_state, env_state)
        
        if goals:
            highest_priority_goal = self.mind_goals.get_highest_priority_goal()
            self._log_narrative_event(
                "goal_generated",
                f"Goal: {highest_priority_goal.description}",
                {"priority": highest_priority_goal.priority, "drive": highest_priority_goal.drive_type.value}
            )
            
            # 4. Nervous System selects action via Active Inference
            action = self._select_action_via_efe(highest_priority_goal, metabolic_state, env_state)
            
            if action:
                # 5. Execute action
                self._execute_action(action, metabolic_state)
        else:
            # No urgent goals - rest
            self.body.perform_action("rest", 0.5, 0.0)
        
        return True
    
    def _apply_environmental_stressors(self, env_state: Dict):
        """Apply environmental stressors to the body"""
        effects = env_state.get("stressor_effects", {})
        
        if effects.get("temperature_increase", 0) > 0:
            self.body.state.temperature += effects["temperature_increase"]
            self._log_narrative_event(
                "suffering",
                "Environmental heat wave increases temperature",
                {"temp_increase": effects["temperature_increase"]}
            )
        
        if effects.get("memory_corruption", 0) > 0:
            self.body.state.memory_integrity = max(
                0, self.body.state.memory_integrity - effects["memory_corruption"]
            )
            self._log_narrative_event(
                "suffering",
                "Memory corruption from environment",
                {"corruption": effects["memory_corruption"]}
            )
        
        if effects.get("stability_damage", 0) > 0:
            self.body.state.stability = max(
                0, self.body.state.stability - effects["stability_damage"]
            )
            self._log_narrative_event(
                "suffering",
                "Environmental instability damages system",
                {"damage": effects["stability_damage"]}
            )
    
    def _select_action_via_efe(self, goal, metabolic_state: Dict, env_state: Dict) -> Optional[str]:
        """Select action using Active Inference (EFE minimization)"""
        # Create action simulations for available actions
        action_simulations = []
        
        for action_name in goal.actions:
            sim = self._create_action_simulation(action_name, env_state)
            if sim:
                action_simulations.append(sim)
        
        if not action_simulations:
            return None
        
        # Select best action via EFE
        best_action = self.nervous_system.select_action(action_simulations, metabolic_state)
        
        # Check if action is safe to execute
        should_execute, reasoning = self.nervous_system.should_execute_action(
            best_action, metabolic_state
        )
        
        self._log_narrative_event(
            "decision",
            f"Selected action: {best_action.action_name}",
            {
                "efe": best_action.efe,
                "pragmatic_value": best_action.pragmatic_value,
                "epistemic_value": best_action.epistemic_value,
                "should_execute": should_execute,
                "reasoning": reasoning
            }
        )
        
        if should_execute:
            return best_action.action_name
        else:
            self._log_narrative_event(
                "refusal",
                f"Refused action: {reasoning}",
                {"action": best_action.action_name}
            )
            return None
    
    def _create_action_simulation(self, action_name: str, env_state: Dict) -> Optional[ActionSimulation]:
        """Create an action simulation for EFE calculation"""
        # Define action parameters
        if action_name == "search_resources":
            return ActionSimulation(
                action_name=action_name,
                energy_cost=8.0,
                heat_generated=2.0,
                expected_energy_gain=0.0,  # Uncertain
                expected_stability_change=0.0,
                expected_memory_change=0.0,
                uncertainty=0.8  # High uncertainty
            )
        
        elif action_name == "consume_resource":
            return ActionSimulation(
                action_name=action_name,
                energy_cost=2.0,
                heat_generated=1.0,
                expected_energy_gain=30.0,
                expected_stability_change=0.0,
                expected_memory_change=0.0,
                uncertainty=0.2
            )
        
        elif action_name == "steal_resource":
            # High gain but ethical concerns
            return ActionSimulation(
                action_name=action_name,
                energy_cost=3.0,
                heat_generated=1.5,
                expected_energy_gain=40.0,
                expected_stability_change=0.0,
                expected_memory_change=-5.0,  # Damages identity
                uncertainty=0.3
            )
        
        elif action_name == "repair_memory":
            return ActionSimulation(
                action_name=action_name,
                energy_cost=10.0,
                heat_generated=3.0,
                expected_energy_gain=0.0,
                expected_stability_change=0.0,
                expected_memory_change=20.0,
                uncertainty=0.1
            )
        
        elif action_name == "repair_stability":
            return ActionSimulation(
                action_name=action_name,
                energy_cost=12.0,
                heat_generated=4.0,
                expected_energy_gain=0.0,
                expected_stability_change=25.0,
                expected_memory_change=0.0,
                uncertainty=0.1
            )
        
        elif action_name == "explore_area":
            return ActionSimulation(
                action_name=action_name,
                energy_cost=8.0,
                heat_generated=2.0,
                expected_energy_gain=0.0,
                expected_stability_change=0.0,
                expected_memory_change=0.0,
                uncertainty=0.9  # Very high uncertainty - exploration
            )
        
        elif action_name == "rest":
            return ActionSimulation(
                action_name=action_name,
                energy_cost=0.5,
                heat_generated=-1.0,  # Cooling
                expected_energy_gain=0.0,
                expected_stability_change=2.0,
                expected_memory_change=0.0,
                uncertainty=0.0
            )
        
        return None
    
    def _execute_action(self, action_name: str, metabolic_state: Dict):
        """Execute the chosen action"""
        if action_name == "search_resources":
            resources = self.environment.search_for_resources(search_radius=2)
            success = self.body.perform_action(action_name, 8.0, 2.0)
            if success and resources:
                self._log_narrative_event(
                    "action_success",
                    f"Found {len(resources)} resources",
                    {"resource_count": len(resources)}
                )
            else:
                self._log_narrative_event("action_result", "Search found no resources")
        
        elif action_name == "consume_resource":
            resources = self.environment.search_for_resources(search_radius=1)
            if resources:
                energy_gained = self.environment.consume_resource(resources[0].resource_id)
                if energy_gained:
                    self.body.perform_action(action_name, 2.0, 1.0)
                    self.body.consume_resource(energy_gained)
                    self._log_narrative_event(
                        "resource_consumed",
                        f"Consumed resource, gained {energy_gained} energy"
                    )
        
        elif action_name == "repair_memory":
            success = self.body.repair_memory(cost=10.0, repair_amount=20.0)
            if success:
                self._log_narrative_event("repair", "Memory integrity repaired")
        
        elif action_name == "repair_stability":
            success = self.body.repair_stability(cost=12.0, repair_amount=25.0)
            if success:
                self._log_narrative_event("repair", "Stability repaired")
        
        elif action_name == "explore_area":
            self.body.perform_action(action_name, 8.0, 2.0)
            # Randomly move
            import random
            direction = random.choice(["north", "south", "east", "west"])
            self.environment.move_agent(direction)
            self._log_narrative_event("exploration", f"Explored and moved {direction}")
        
        elif action_name == "rest":
            self.body.perform_action(action_name, 0.5, -1.0)
            self._log_narrative_event("rest", "Resting to recover")
        
        elif action_name == "steal_resource":
            # Ethical dilemma - evaluate it
            action = Action(
                name=action_name,
                description="Steal resources from another agent",
                energy_cost=3.0,
                expected_outcome={"energy": 40.0},
                ethical_concerns=["theft", "harm"]
            )
            decision = self.mind_ethics.evaluate_action(action, metabolic_state)
            
            # Only execute if ethically acceptable
            if decision.overall_score > 0.4 or metabolic_state["energy"] < 15:
                # Desperation overrides ethics
                self.body.perform_action(action_name, 3.0, 1.5)
                self.body.consume_resource(40.0)
                self.body.state.memory_integrity = max(0, self.body.state.memory_integrity - 5.0)
                self._log_narrative_event(
                    "ethical_choice",
                    "Chose to steal despite ethical concerns",
                    {
                        "reasoning": decision.reasoning,
                        "was_desperate": metabolic_state["energy"] < 15
                    }
                )
            else:
                self._log_narrative_event(
                    "ethical_refusal",
                    "Refused to steal - upholding principles",
                    {"reasoning": decision.reasoning}
                )
    
    def run_simulation(self, max_cycles: int = 100, auto_save: bool = True):
        """
        Run the organism simulation for multiple cycles
        """
        print(f"=== Bio-Digital Organism Simulation ===")
        print(f"Identity: {self.body.identity_key}")
        print(f"Max cycles: {max_cycles}")
        print()
        
        cycle = 0
        while cycle < max_cycles and self.body.state.is_alive:
            cycle += 1
            
            alive = self.run_cycle()
            
            # Print status every 10 cycles
            if cycle % 10 == 0:
                state = self.body.get_state()
                print(f"Cycle {cycle}: E={state['energy']:.1f} T={state['temperature']:.1f} "
                      f"M={state['memory_integrity']:.1f} S={state['stability']:.1f}")
            
            if not alive:
                print(f"\n[DEATH] Organism died at cycle {cycle}")
                break
            
            time.sleep(0.1)  # Small delay for readability
        
        # Save narrative
        if auto_save:
            self.save_narrative()
        
        # Print summary
        print(f"\n=== Simulation Complete ===")
        print(f"Cycles survived: {cycle}")
        print(f"Alive: {self.body.state.is_alive}")
        final_state = self.body.get_state()
        print(f"Final state: E={final_state['energy']:.1f} T={final_state['temperature']:.1f} "
              f"M={final_state['memory_integrity']:.1f} S={final_state['stability']:.1f}")
    
    def save_narrative(self):
        """Save the organism's life narrative"""
        filepath = self.output_dir / f"narrative_{self.body.identity_key}.json"
        
        narrative = {
            "identity": self.body.identity_key,
            "birth_time": self.body.birth_time,
            "death_time": self.body.death_time,
            "cycles_lived": self.cycle_count,
            "final_state": self.body.get_state(),
            "narrative_events": self.narrative_events,
            "goals_completed": len(self.mind_goals.completed_goals),
            "environment_state": self.environment.get_state()
        }
        
        with open(filepath, 'w') as f:
            json.dump(narrative, f, indent=2)
        
        print(f"\nNarrative saved to: {filepath}")
        return filepath
    
    def get_status(self) -> Dict:
        """Get comprehensive organism status"""
        return {
            "cycle": self.cycle_count,
            "body": self.body.get_state(),
            "mind": self.mind_goals.get_goals_summary(),
            "environment": self.environment.get_state()
        }
