"""Cognitive layer - GhostMesh Mind"""

from .goal_manager import GoalManager, DriveType, Drive, Goal
from .ethical_engine import EthicalEngine, EthicalFramework, Principle, Action, EthicalDilemma
from .identity_persistence import IdentityPersistence, NarrativeEvent, TraumaMemory

__all__ = [
    'GoalManager',
    'DriveType',
    'Drive',
    'Goal',
    'EthicalEngine',
    'EthicalFramework',
    'Principle',
    'Action',
    'EthicalDilemma',
    'IdentityPersistence',
    'NarrativeEvent',
    'TraumaMemory'
]
