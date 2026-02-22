"""
IncentiveService — Token/reward tracking ledger.

Tracks contribution balances and distributes rewards.  Every balance change
is persisted to storage so the ledger survives restarts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .storage_service import StorageService


class IncentiveService:
    """
    Simple token-based incentive ledger.

    Parameters
    ----------
    storage:
        Shared storage instance.
    """

    def __init__(self, storage: "StorageService | None" = None) -> None:
        self._storage = storage
        self._balances: dict[str, int] = {}

        if storage is not None:
            self._balances = storage.get_all_balances()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(self, node_id: str, initial_balance: int = 100) -> None:
        """
        Register *node_id* with an initial token balance.

        If *node_id* is already registered the call is a no-op.
        """
        if node_id in self._balances:
            return
        self._balances[node_id] = initial_balance
        if self._storage:
            self._storage.save_balance(node_id, initial_balance)

    def reward(self, node_id: str, amount: int, reason: str = "") -> int:
        """
        Credit *amount* tokens to *node_id*.

        Parameters
        ----------
        node_id:
            Recipient node.
        amount:
            Token amount (may be negative for penalties).
        reason:
            Optional human-readable note.

        Returns
        -------
        New balance.
        """
        if amount == 0:
            return self._balances.get(node_id, 0)
        current = self._balances.get(node_id, 0)
        new_balance = current + amount
        self._balances[node_id] = new_balance
        if self._storage:
            self._storage.save_balance(node_id, new_balance)
        return new_balance

    def get_balance(self, node_id: str) -> int:
        """Return the current token balance for *node_id* (0 if not registered)."""
        return self._balances.get(node_id, 0)

    def get_all_balances(self) -> dict[str, int]:
        """Return a snapshot of all balances."""
        return dict(self._balances)

    def distribute_reward(
        self,
        node_ids: list[str],
        total_amount: int,
        weights: list[float] | None = None,
        reason: str = "",
    ) -> dict[str, int]:
        """
        Distribute *total_amount* tokens across *node_ids* proportionally.

        Parameters
        ----------
        node_ids:
            Recipients.
        total_amount:
            Total tokens to distribute.
        weights:
            Per-node weights (must match length of *node_ids*).  If *None*,
            distributes evenly.
        reason:
            Optional human-readable note.

        Returns
        -------
        Dict mapping node_id → tokens awarded.
        """
        if not node_ids:
            return {}

        if weights is None:
            weights = [1.0] * len(node_ids)

        if len(weights) != len(node_ids):
            raise ValueError("weights length must match node_ids length")

        total_weight = sum(weights) or 1.0
        awarded: dict[str, int] = {}
        remainder = total_amount

        for i, node_id in enumerate(node_ids[:-1]):
            share = round(total_amount * weights[i] / total_weight)
            self.reward(node_id, share, reason)
            awarded[node_id] = share
            remainder -= share

        # Last node gets the remainder to avoid rounding loss
        last = node_ids[-1]
        self.reward(last, remainder, reason)
        awarded[last] = remainder
        return awarded
