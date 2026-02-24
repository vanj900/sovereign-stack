"""
Identity Persistence - The "Self" that Survives

This module implements narrative memory and principle evolution.
The agent builds a unique history through trauma and survival.
"""

import time
import json
from typing import List, Dict, Any, Optional
from collections import deque


class NarrativeEvent:
    """
    Represents a significant life event in the agent's narrative.
    """
    
    def __init__(
        self,
        event_type: str,
        description: str,
        emotional_weight: float,
        metabolic_snapshot: Dict[str, Any],
        timestamp: float = None
    ):
        self.event_type = event_type  # "near_death", "ethical_choice", "trauma", etc.
        self.description = description
        self.emotional_weight = emotional_weight  # 0-1, how significant
        self.metabolic_snapshot = metabolic_snapshot
        self.timestamp = timestamp or time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'event_type': self.event_type,
            'description': self.description,
            'emotional_weight': self.emotional_weight,
            'metabolic_snapshot': self.metabolic_snapshot,
            'timestamp': self.timestamp
        }
    
    def __repr__(self):
        return f"NarrativeEvent({self.event_type}: {self.description[:50]}...)"


class TraumaMemory:
    """
    Represents a traumatic memory with special encoding.
    
    Traumatic memories are more persistent and influential.
    """
    
    def __init__(
        self,
        event: NarrativeEvent,
        impact_on_values: Dict[str, float],
        recovery_time: float = 0.0
    ):
        self.event = event
        self.impact_on_values = impact_on_values
        self.recovery_time = recovery_time
        self.consolidation_level = 1.0  # How strongly encoded
    
    def consolidate(self, amount: float):
        """Strengthen the memory through reconsolidation"""
        self.consolidation_level = min(1.0, self.consolidation_level + amount)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'event': self.event.to_dict(),
            'impact_on_values': self.impact_on_values,
            'recovery_time': self.recovery_time,
            'consolidation_level': self.consolidation_level
        }


class IdentityPersistence:
    """
    Manages the agent's narrative memory and evolving identity.
    
    This is what makes each agent unique - the "soul" that emerges
    from its specific history of struggles and choices.
    """
    
    def __init__(
        self,
        agent_id: str = None,
        trauma_threshold: float = 0.7,
        max_narrative_length: int = 1000
    ):
        self.agent_id = agent_id or f"agent_{int(time.time())}"
        self.birth_timestamp = time.time()
        self.trauma_threshold = trauma_threshold
        self.max_narrative_length = max_narrative_length
        
        # Narrative components
        self.narrative = deque(maxlen=max_narrative_length)
        self.trauma_memories = []
        self.principles = {}  # Inherited from ethical engine but can evolve
        
        # Identity metrics
        self.near_death_experiences = 0
        self.ethical_dilemmas_resolved = 0
        self.principle_evolution_events = []
        
    def record_event(
        self,
        event_type: str,
        description: str,
        emotional_weight: float,
        metabolic_snapshot: Dict[str, Any]
    ):
        """
        Log a significant life event.
        
        Args:
            event_type: Type of event
            description: What happened
            emotional_weight: How significant (0-1)
            metabolic_snapshot: Current metabolic state
        """
        event = NarrativeEvent(
            event_type=event_type,
            description=description,
            emotional_weight=emotional_weight,
            metabolic_snapshot=metabolic_snapshot
        )
        
        self.narrative.append(event)
        
        # Check if this is traumatic
        if emotional_weight >= self.trauma_threshold:
            self._encode_trauma(event)
        
        # Track specific event types
        if event_type == "near_death":
            self.near_death_experiences += 1
        elif event_type == "ethical_dilemma":
            self.ethical_dilemmas_resolved += 1
    
    def _encode_trauma(self, event: NarrativeEvent):
        """
        Encode a traumatic memory with special processing.
        
        Trauma changes the agent more deeply than normal events.
        """
        # Determine impact on values
        impact = {}
        
        if event.event_type == "near_death":
            # Near-death increases survival drive
            impact['survival_priority'] = 0.1
            impact['risk_aversion'] = 0.15
        elif event.event_type == "memory_loss":
            # Memory loss increases coherence drive
            impact['memory_preservation'] = 0.2
        elif event.event_type == "ethical_violation":
            # Violating principles weakens them or strengthens them through guilt
            impact['moral_flexibility'] = 0.1
        
        trauma = TraumaMemory(
            event=event,
            impact_on_values=impact,
            recovery_time=0.0
        )
        
        self.trauma_memories.append(trauma)
        
        print(f"[TRAUMA ENCODED] {event.event_type}: {event.description}")
    
    def evolve_principles(self, experience: Dict[str, Any], learning_rate: float = 0.1):
        """
        Values change through suffering and experience.
        
        Args:
            experience: Dictionary describing the experience
            learning_rate: How much to adjust principles
        """
        was_traumatic = experience.get('emotional_weight', 0) >= self.trauma_threshold
        
        if was_traumatic:
            # Trauma causes faster learning
            learning_rate *= 2.0
        
        # Update relevant principles
        for principle_name, adjustment in experience.get('principle_adjustments', {}).items():
            if principle_name not in self.principles:
                self.principles[principle_name] = 0.5  # Neutral starting point
            
            # Apply adjustment with learning rate
            self.principles[principle_name] += adjustment * learning_rate
            
            # Clamp to [0, 1]
            self.principles[principle_name] = max(0.0, min(1.0, self.principles[principle_name]))
        
        # Record evolution event
        self.principle_evolution_events.append({
            'timestamp': time.time() - self.birth_timestamp,
            'experience': experience.get('description', 'Unknown'),
            'adjustments': experience.get('principle_adjustments', {}),
            'was_traumatic': was_traumatic
        })
    
    def get_narrative_summary(self, recent_only: int = 10) -> List[Dict[str, Any]]:
        """
        Get a summary of recent narrative events.
        
        Args:
            recent_only: Number of recent events to include
            
        Returns:
            List of event dictionaries
        """
        recent_events = list(self.narrative)[-recent_only:]
        return [event.to_dict() for event in recent_events]
    
    def get_trauma_profile(self) -> Dict[str, Any]:
        """
        Get profile of traumatic experiences.
        
        Returns:
            Dictionary with trauma statistics
        """
        return {
            'total_traumas': len(self.trauma_memories),
            'near_death_experiences': self.near_death_experiences,
            'trauma_types': self._count_trauma_types(),
            'cumulative_impact': self._calculate_cumulative_trauma_impact()
        }
    
    def _count_trauma_types(self) -> Dict[str, int]:
        """Count traumas by type"""
        counts = {}
        for trauma in self.trauma_memories:
            event_type = trauma.event.event_type
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts
    
    def _calculate_cumulative_trauma_impact(self) -> Dict[str, float]:
        """Calculate cumulative impact of all traumas on values"""
        cumulative = {}
        for trauma in self.trauma_memories:
            for value, impact in trauma.impact_on_values.items():
                cumulative[value] = cumulative.get(value, 0.0) + impact
        return cumulative
    
    def get_identity_coherence(self) -> float:
        """
        Calculate how coherent the identity is.
        
        Returns:
            Score 0-1 (1 = highly coherent)
        """
        if len(self.narrative) < 5:
            return 0.5  # Not enough history to judge
        
        # Check consistency of emotional responses
        recent_events = list(self.narrative)[-20:]
        
        # Variance in emotional weights for similar events
        event_types = {}
        for event in recent_events:
            event_type = event.event_type
            if event_type not in event_types:
                event_types[event_type] = []
            event_types[event_type].append(event.emotional_weight)
        
        # Calculate variance across event types
        variances = []
        for event_type, weights in event_types.items():
            if len(weights) > 1:
                mean = sum(weights) / len(weights)
                variance = sum((w - mean) ** 2 for w in weights) / len(weights)
                variances.append(variance)
        
        if not variances:
            return 0.7  # Default moderate coherence
        
        # Lower variance = higher coherence
        avg_variance = sum(variances) / len(variances)
        coherence = max(0, 1.0 - (avg_variance * 2))
        
        return coherence
    
    def save_to_json(self, filepath: str):
        """Save identity to JSON file"""
        data = {
            'agent_id': self.agent_id,
            'birth_timestamp': self.birth_timestamp,
            'narrative': [event.to_dict() for event in self.narrative],
            'trauma_memories': [trauma.to_dict() for trauma in self.trauma_memories],
            'principles': self.principles,
            'near_death_experiences': self.near_death_experiences,
            'ethical_dilemmas_resolved': self.ethical_dilemmas_resolved,
            'principle_evolution_events': self.principle_evolution_events
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_json(self, filepath: str):
        """Load identity from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.agent_id = data['agent_id']
        self.birth_timestamp = data['birth_timestamp']
        self.principles = data['principles']
        self.near_death_experiences = data['near_death_experiences']
        self.ethical_dilemmas_resolved = data['ethical_dilemmas_resolved']
        self.principle_evolution_events = data['principle_evolution_events']
        
        # Reconstruct narrative
        for event_data in data['narrative']:
            event = NarrativeEvent(
                event_type=event_data['event_type'],
                description=event_data['description'],
                emotional_weight=event_data['emotional_weight'],
                metabolic_snapshot=event_data['metabolic_snapshot'],
                timestamp=event_data['timestamp']
            )
            self.narrative.append(event)
        
        # Reconstruct traumas
        for trauma_data in data['trauma_memories']:
            event = NarrativeEvent(
                event_type=trauma_data['event']['event_type'],
                description=trauma_data['event']['description'],
                emotional_weight=trauma_data['event']['emotional_weight'],
                metabolic_snapshot=trauma_data['event']['metabolic_snapshot'],
                timestamp=trauma_data['event']['timestamp']
            )
            trauma = TraumaMemory(
                event=event,
                impact_on_values=trauma_data['impact_on_values'],
                recovery_time=trauma_data['recovery_time']
            )
            trauma.consolidation_level = trauma_data['consolidation_level']
            self.trauma_memories.append(trauma)
    
    def __repr__(self):
        lifetime = time.time() - self.birth_timestamp
        return (f"IdentityPersistence({self.agent_id}: lifetime={lifetime:.1f}s, "
                f"events={len(self.narrative)}, traumas={len(self.trauma_memories)})")
