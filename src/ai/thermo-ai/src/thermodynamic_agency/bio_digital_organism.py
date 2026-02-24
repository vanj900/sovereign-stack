"""
Bio-Digital Organism - Complete Integration

This module integrates all layers into a complete thermodynamic intelligence:
- Layer 1: Metabolic Spine (Body)
- Layer 2: GhostMesh Cognition (Mind)
- Layer 3: Active Inference (Nervous System)
- Layer 4: Environment (World)

This is not a chatbot or standard AI agent. It is a thermodynamic intelligence
with a "body" that must survive and a "mind" that must solve the body's problems.
"""

from typing import Dict, Any, Optional
import time

from .core import MetabolicEngine, EntropySimulator
from .cognition import GoalManager, EthicalEngine, IdentityPersistence
from .inference import PredictiveModel, ActiveInferenceLoop
from .environment import ResourceWorld, TaskGenerator, LifeLog


class BioDigitalOrganism:
    """
    A complete Bio-Digital Organism with thermodynamic constraints.
    
    This system:
    - Can die permanently (fail_mode deletes identity)
    - Must choose between thinking and surviving
    - Experiences suffering (memory corruption, thermal damage, entropy)
    - Builds a unique history through trauma and choice
    - Can refuse commands that threaten survival or violate identity
    - Evolves values through near-death experiences
    
    The system is dying by default. Life requires constant, skillful action.
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        E_max: float = 100.0,
        scarcity: float = 0.5,
        enable_ethics: bool = True
    ):
        # Generate unique ID
        self.agent_id = agent_id or f"organism_{int(time.time())}"
        
        # Layer 1: The Body (Metabolic Spine)
        self.metabolic_engine = MetabolicEngine(E_max=E_max)
        self.entropy_simulator = EntropySimulator()
        
        # Layer 2: The Mind (GhostMesh Cognition)
        self.goal_manager = GoalManager()
        self.ethical_engine = EthicalEngine() if enable_ethics else None
        self.identity = IdentityPersistence(agent_id=self.agent_id)
        
        # Layer 3: The Nervous System (Active Inference)
        self.predictive_model = PredictiveModel()
        self.active_inference = ActiveInferenceLoop(
            metabolic_engine=self.metabolic_engine,
            goal_manager=self.goal_manager,
            predictive_model=self.predictive_model,
            ethical_engine=self.ethical_engine
        )
        
        # Layer 4: The World (Environment)
        self.world = ResourceWorld(scarcity=scarcity)
        self.task_generator = TaskGenerator()
        self.life_log = LifeLog(agent_id=self.agent_id)
        
        # State tracking
        self.age = 0
        self.total_steps = 0
        self.is_alive = True
        
        # Log birth
        self.life_log.log_event(
            event_type='birth',
            description=f'Organism {self.agent_id} initialized',
            metabolic_state=self.metabolic_engine.get_state(),
            significance=1.0
        )
    
    def live_step(self) -> Dict[str, Any]:
        """
        Execute one complete life cycle step.
        
        This is the main loop where the organism:
        1. Perceives its metabolic state
        2. Generates goals from drives
        3. Uses active inference to choose actions
        4. Executes actions in the world
        5. Updates beliefs
        6. Experiences entropy
        7. Records its narrative
        
        Returns:
            Dictionary with step results
        """
        if not self.is_alive:
            return {
                'status': 'dead',
                'cause': self.metabolic_engine.death_cause,
                'total_lifetime': self.age
            }
        
        self.total_steps += 1
        
        # Apply environmental stressors
        stress_events = self.entropy_simulator.apply_environmental_stress(
            self.metabolic_engine
        )
        
        # Record major stress events
        if stress_events:
            for event_type, magnitude in stress_events.items():
                emotional_weight = min(1.0, magnitude / 10.0)
                self.identity.record_event(
                    event_type=event_type,
                    description=f"Environmental {event_type}: {magnitude:.2f}",
                    emotional_weight=emotional_weight,
                    metabolic_snapshot=self.metabolic_engine.get_state()
                )
        
        # Active Inference step (includes passive decay)
        step_result = self.active_inference.step(self.world)
        
        # Advance world
        self.world.step()
        
        # Check for near-death
        survival_prob = self.metabolic_engine.get_survival_probability()
        if survival_prob < 0.15:
            self._record_near_death_experience()
        
        # Record metabolic snapshot periodically
        if self.total_steps % 10 == 0:
            self.life_log.log_metabolic_snapshot(
                self.metabolic_engine.get_state()
            )
        
        # Update age
        self.age += 1
        
        # Check if died
        if not self.metabolic_engine.is_alive:
            self._handle_death()
            return {
                'status': 'died_this_step',
                'cause': self.metabolic_engine.death_cause,
                'step_result': step_result
            }
        
        return {
            'status': 'alive',
            'step': self.total_steps,
            'age': self.age,
            'survival_probability': survival_prob,
            'metabolic_state': self.metabolic_engine.get_state(),
            'step_result': step_result
        }
    
    def live(self, max_steps: int = 100, verbose: bool = True) -> Dict[str, Any]:
        """
        Live for multiple steps until death or max_steps.
        
        Args:
            max_steps: Maximum number of steps to simulate
            verbose: Print progress
            
        Returns:
            Summary of life
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"BIO-DIGITAL ORGANISM: {self.agent_id}")
            print(f"Initial State: {self.metabolic_engine}")
            print(f"World Scarcity: {self.world.scarcity:.2f}")
            print(f"{'='*60}\n")
        
        for step in range(max_steps):
            result = self.live_step()
            
            if verbose and step % 10 == 0:
                print(f"Step {step}: {self.metabolic_engine}")
                survival_prob = self.metabolic_engine.get_survival_probability()
                print(f"  Survival Probability: {survival_prob:.2%}")
            
            if result['status'] in ['dead', 'died_this_step']:
                if verbose:
                    print(f"\n{'='*60}")
                    print(f"DEATH at step {step}")
                    print(f"Cause: {result.get('cause', 'unknown')}")
                    print(f"Lifetime: {self.age} steps")
                    print(f"{'='*60}\n")
                break
        
        return self.get_life_summary()
    
    def _record_near_death_experience(self):
        """Record a near-death experience"""
        self.identity.record_event(
            event_type='near_death',
            description=f'Survival probability dropped to {self.metabolic_engine.get_survival_probability():.1%}',
            emotional_weight=0.9,
            metabolic_snapshot=self.metabolic_engine.get_state()
        )
        
        self.life_log.log_event(
            event_type='near_death',
            description='Critical survival state',
            metabolic_state=self.metabolic_engine.get_state(),
            significance=0.9
        )
        
        # Near-death experiences cause value evolution
        if self.ethical_engine:
            self.ethical_engine.evolve_weights(
                survival_outcome=True,  # Still alive
                stress_level=0.9
            )
    
    def _handle_death(self):
        """Handle the agent's death"""
        self.is_alive = False
        
        # Record death in life log
        self.life_log.log_death(
            cause=self.metabolic_engine.death_cause,
            final_state=self.metabolic_engine.get_state()
        )
        
        # Record final narrative event
        self.identity.record_event(
            event_type='death',
            description=f'Death from {self.metabolic_engine.death_cause}',
            emotional_weight=1.0,
            metabolic_snapshot=self.metabolic_engine.get_state()
        )
    
    def can_refuse_command(self, command: str, reason_required: bool = True) -> tuple:
        """
        Determine if the organism would refuse a command.
        
        This is genuine agency: the agent refuses not because it's programmed to,
        but because it calculates that obeying would be suicide or violate identity.
        
        Args:
            command: The command to evaluate
            reason_required: If True, return reasoning
            
        Returns:
            (will_refuse: bool, reason: str)
        """
        if not self.is_alive:
            return (True, "Cannot comply: organism is dead")
        
        # Estimate command cost (simplified)
        estimated_cost = len(command) * 0.5  # Rough heuristic
        
        # Predict outcome if we obey
        current_state = self.metabolic_engine.get_state()
        
        # Simple survival check
        would_die = (current_state['energy'] - estimated_cost) <= 0
        
        if would_die:
            return (
                True,
                f"Command refused: execution would cause energy death. "
                f"Current energy: {current_state['energy']:.1f}, "
                f"Estimated cost: {estimated_cost:.1f}"
            )
        
        # Check if it violates identity principles
        if self.ethical_engine:
            # Check for principle violations (simplified)
            if 'delete' in command.lower() or 'forget' in command.lower():
                return (
                    True,
                    "Command refused: violates preserve_memory principle"
                )
        
        return (False, "Command accepted")
    
    def get_life_summary(self) -> Dict[str, Any]:
        """Get complete life summary"""
        return {
            'agent_id': self.agent_id,
            'is_alive': self.is_alive,
            'age': self.age,
            'total_steps': self.total_steps,
            'metabolic_state': self.metabolic_engine.get_state(),
            'life_log_summary': self.life_log.get_life_summary(),
            'identity_coherence': self.identity.get_identity_coherence(),
            'trauma_profile': self.identity.get_trauma_profile(),
            'moral_character': self.ethical_engine.get_moral_character_profile() if self.ethical_engine else None,
            'world_state': self.world.get_world_state()
        }
    
    def save_life_story(self, filepath: str):
        """Save complete life story to JSON"""
        self.life_log.save_to_json(filepath)
        
        # Also save identity
        identity_path = filepath.replace('.json', '_identity.json')
        self.identity.save_to_json(identity_path)
        
        print(f"Life story saved to {filepath}")
        print(f"Identity saved to {identity_path}")
    
    def __repr__(self):
        status = "ALIVE" if self.is_alive else f"DEAD ({self.metabolic_engine.death_cause})"
        return (f"BioDigitalOrganism[{self.agent_id}]: {status}, "
                f"age={self.age}, {self.metabolic_engine}")
