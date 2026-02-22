"""
GovernanceService — Proposal & voting system with hash-chain anchoring.

Implements:
- Proposal creation
- Vote casting (APPROVE / REJECT / ABSTAIN)
- Quorum-aware vote tallying
- Append-only hash chain for tamper-evident audit trail
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .storage_service import StorageService

VALID_CHOICES = {"APPROVE", "REJECT", "ABSTAIN"}


class GovernanceService:
    """
    Lightweight proposal/voting engine with a simple append-only hash chain.

    Parameters
    ----------
    storage:
        Shared storage instance.
    quorum:
        Minimum fraction of registered voters required for a valid tally
        (default 0.5 → majority).
    """

    def __init__(
        self,
        storage: "StorageService | None" = None,
        quorum: float = 0.5,
    ) -> None:
        self._storage = storage
        self._quorum = quorum
        self._proposals: dict = {}
        self._votes: dict = {}  # proposal_id → {voter_did: choice}

        if storage is not None:
            self._load_from_storage()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load_from_storage(self) -> None:
        storage = self._storage
        assert storage is not None
        for row in storage.list_proposals():
            self._proposals[row["id"]] = row
            self._votes[row["id"]] = {}
        for row in storage.fetch_all(storage.votes.select()):
            pid = row["proposal_id"]
            if pid not in self._votes:
                self._votes[pid] = {}
            self._votes[pid][row["voter_did"]] = row["choice"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_proposal(self, proposer_did: str, description: str) -> str:
        """
        Create a new governance proposal.

        Returns the proposal id (``P-<n>``).
        """
        prop_id = f"P-{len(self._proposals) + 1}"
        proposal = {
            "id": prop_id,
            "proposer": proposer_did,
            "description": description,
            "status": "open",
        }
        self._proposals[prop_id] = proposal
        self._votes[prop_id] = {}
        if self._storage:
            self._storage.save_proposal(proposal)
        return prop_id

    def vote(self, prop_id: str, voter_did: str, choice: str) -> None:
        """
        Cast a vote on *prop_id*.

        Parameters
        ----------
        prop_id:
            Proposal identifier.
        voter_did:
            DID of the voter.
        choice:
            One of ``APPROVE``, ``REJECT``, or ``ABSTAIN``.
        """
        choice = choice.upper()
        if choice not in VALID_CHOICES:
            raise ValueError(f"Invalid choice '{choice}'. Must be one of {VALID_CHOICES}")
        if prop_id not in self._proposals:
            raise KeyError(f"Unknown proposal: {prop_id}")
        if self._proposals[prop_id]["status"] != "open":
            raise RuntimeError(f"Proposal {prop_id} is already closed")

        self._votes[prop_id][voter_did] = choice
        if self._storage:
            self._storage.save_vote(prop_id, voter_did, choice)

    def tally(self, prop_id: str, total_voters: int | None = None) -> str:
        """
        Tally votes, enforce quorum, update proposal status, and anchor to chain.

        Parameters
        ----------
        prop_id:
            Proposal to tally.
        total_voters:
            Total number of eligible voters (used for quorum check).  If
            *None*, uses the number of votes cast.

        Returns
        -------
        ``"PASSED"``, ``"FAILED"``, or ``"NO_QUORUM"``.
        """
        if prop_id not in self._proposals:
            raise KeyError(f"Unknown proposal: {prop_id}")

        votes = self._votes.get(prop_id, {})
        approve = sum(1 for v in votes.values() if v == "APPROVE")
        reject = sum(1 for v in votes.values() if v == "REJECT")
        total_cast = len(votes)

        eligible = total_voters if total_voters is not None else total_cast
        quorum_met = eligible == 0 or (total_cast / eligible) >= self._quorum

        if not quorum_met:
            result = "NO_QUORUM"
        elif approve > reject:
            result = "PASSED"
        else:
            result = "FAILED"

        self._proposals[prop_id]["status"] = result
        if self._storage:
            self._storage.save_proposal(self._proposals[prop_id])

        self._anchor(prop_id, result, approve, reject)
        return result

    def get_proposal(self, prop_id: str) -> dict | None:
        """Return the proposal dict or *None* if not found."""
        return self._proposals.get(prop_id)

    def list_proposals(self) -> list[dict]:
        """Return all proposals."""
        return list(self._proposals.values())

    def get_votes(self, prop_id: str) -> dict:
        """Return ``{voter_did: choice}`` for *prop_id*."""
        return dict(self._votes.get(prop_id, {}))

    def get_chain(self) -> list[dict]:
        """Return the full hash chain."""
        if self._storage:
            return self._storage.get_chain()
        return []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _anchor(self, prop_id: str, result: str, approve: int, reject: int) -> None:
        """Append a new block to the hash chain for this decision."""
        prev_hash = (
            self._storage.get_last_block_hash() if self._storage else "0" * 16
        )
        payload = json.dumps(
            {
                "prop_id": prop_id,
                "result": result,
                "approve": approve,
                "reject": reject,
                "ts": int(time.time()),
            },
            sort_keys=True,
        )
        block_hash = hashlib.sha256(
            (prev_hash + payload).encode()
        ).hexdigest()
        if self._storage:
            self._storage.append_block(prev_hash, payload, block_hash)
