"""GhostMesh cognitive layer — goals, ethics, identity."""

from .goal_manager import GoalManager, Drive
from .ethical_engine import EthicalEngine
from .identity_persistence import IdentityPersistence

__all__ = ["GoalManager", "Drive", "EthicalEngine", "IdentityPersistence"]
