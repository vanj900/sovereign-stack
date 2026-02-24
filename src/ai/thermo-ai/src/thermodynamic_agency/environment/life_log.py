"""
Life Log - Chronicle of Existence

Records the agent's complete life story: successes, failures, trauma, and death.
"""

import json
import time
from typing import Dict, Any, List, Optional


class LifeLog:
    """
    Chronicles an agent's entire existence from birth to death.
    
    This is the "soul trace" - the unique narrative that emerges
    from each agent's specific struggles against entropy.
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.birth_time = time.time()
        self.death_time = None
        
        # Event categories
        self.major_events = []
        self.metabolic_snapshots = []
        self.decisions = []
        self.traumas = []
        
        # Statistics
        self.total_energy_consumed = 0.0
        self.total_energy_harvested = 0.0
        self.near_death_count = 0
        self.ethical_dilemmas = 0
        
    def log_event(
        self,
        event_type: str,
        description: str,
        metabolic_state: Dict[str, Any],
        significance: float = 0.5
    ):
        """Log a significant event"""
        event = {
            'timestamp': time.time() - self.birth_time,
            'event_type': event_type,
            'description': description,
            'metabolic_state': metabolic_state,
            'significance': significance
        }
        
        self.major_events.append(event)
        
        # Track statistics
        if event_type == 'near_death':
            self.near_death_count += 1
        elif event_type == 'ethical_dilemma':
            self.ethical_dilemmas += 1
    
    def log_metabolic_snapshot(self, state: Dict[str, Any]):
        """Record metabolic state at this moment"""
        snapshot = {
            'timestamp': time.time() - self.birth_time,
            **state
        }
        self.metabolic_snapshots.append(snapshot)
    
    def log_decision(self, decision: Dict[str, Any]):
        """Record a decision made"""
        self.decisions.append({
            'timestamp': time.time() - self.birth_time,
            **decision
        })
    
    def log_death(self, cause: str, final_state: Dict[str, Any]):
        """Record the agent's death"""
        self.death_time = time.time()
        
        self.log_event(
            event_type='death',
            description=f'Agent died from {cause}',
            metabolic_state=final_state,
            significance=1.0
        )
    
    def get_life_summary(self) -> Dict[str, Any]:
        """Get summary of the agent's life"""
        lifetime = (self.death_time or time.time()) - self.birth_time
        
        return {
            'agent_id': self.agent_id,
            'birth_time': self.birth_time,
            'death_time': self.death_time,
            'lifetime_seconds': lifetime,
            'status': 'deceased' if self.death_time else 'alive',
            'major_events_count': len(self.major_events),
            'near_death_experiences': self.near_death_count,
            'ethical_dilemmas_faced': self.ethical_dilemmas,
            'decisions_made': len(self.decisions)
        }
    
    def save_to_json(self, filepath: str):
        """Save complete life log to JSON"""
        data = {
            'agent_id': self.agent_id,
            'birth_time': self.birth_time,
            'death_time': self.death_time,
            'life_summary': self.get_life_summary(),
            'major_events': self.major_events,
            'metabolic_snapshots': self.metabolic_snapshots,
            'decisions': self.decisions,
            'traumas': self.traumas
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def __repr__(self):
        lifetime = (self.death_time or time.time()) - self.birth_time
        status = "deceased" if self.death_time else "alive"
        return f"LifeLog({self.agent_id}: {status}, lifetime={lifetime:.1f}s, events={len(self.major_events)})"
