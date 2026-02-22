"""
ReputationService — PageRank-style trust scoring with time-decay.

Nodes endorse each other; scores are computed iteratively so that
endorsements from high-reputation nodes carry more weight.
Time-decay reduces the influence of stale endorsements.
"""

from __future__ import annotations

import math
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .storage_service import StorageService


class ReputationService:
    """
    Trust-graph backed by a weighted, time-decayed PageRank algorithm.

    Parameters
    ----------
    storage:
        Shared storage instance.
    damping:
        PageRank damping factor (default 0.85).
    iterations:
        Number of power-iteration steps (default 20).
    decay_half_life_days:
        Half-life for endorsement weight decay in days.  An endorsement
        made *decay_half_life_days* ago counts at half weight.  Set to
        *None* to disable decay.
    """

    def __init__(
        self,
        storage: "StorageService | None" = None,
        damping: float = 0.85,
        iterations: int = 20,
        decay_half_life_days: float | None = 30.0,
    ) -> None:
        self._storage = storage
        self._damping = damping
        self._iterations = iterations
        self._decay_lambda = (
            math.log(2) / (decay_half_life_days * 86_400)
            if decay_half_life_days is not None
            else 0.0
        )
        self._nodes: set = set()
        # (source, target, weight, timestamp)
        self._edges: list[tuple[str, str, float, float]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_node(self, node_id: str) -> None:
        """Register *node_id* in the trust graph."""
        self._nodes.add(node_id)

    def add_endorsement(
        self,
        source: str,
        target: str,
        weight: float = 1.0,
        timestamp: float | None = None,
    ) -> None:
        """
        Record that *source* endorses *target*.

        Parameters
        ----------
        source, target:
            Node identifiers.
        weight:
            Base endorsement strength (default 1.0).
        timestamp:
            Unix timestamp of the endorsement (defaults to now).
        """
        ts = timestamp if timestamp is not None else time.time()
        self._nodes.update([source, target])
        self._edges.append((source, target, weight, ts))

    def compute_scores(self) -> dict[str, float]:
        """
        Run PageRank-style iteration and return ``{node_id: score}``.

        Scores sum to 1.0.  Results are persisted to storage if available.
        """
        nodes = list(self._nodes)
        n = len(nodes)
        if n == 0:
            return {}

        now = time.time()

        # Apply time decay to edge weights
        effective_edges: list[tuple[str, str, float]] = []
        for src, tgt, w, ts in self._edges:
            decay = math.exp(-self._decay_lambda * (now - ts)) if self._decay_lambda else 1.0
            effective_edges.append((src, tgt, w * decay))

        out_weight: dict = {nd: 0.0 for nd in nodes}
        in_edges: dict = {nd: [] for nd in nodes}
        for src, tgt, w in effective_edges:
            if src in out_weight:
                out_weight[src] += w
            if tgt in in_edges:
                in_edges[tgt].append((src, w))

        scores = {nd: 1.0 / n for nd in nodes}

        for _ in range(self._iterations):
            new_scores: dict = {}
            for nd in nodes:
                rank_sum = sum(
                    scores[src] * w / out_weight[src]
                    for src, w in in_edges[nd]
                    if out_weight.get(src, 0) > 0
                )
                new_scores[nd] = (1 - self._damping) / n + self._damping * rank_sum
            scores = new_scores

        total = sum(scores.values()) or 1.0
        scores = {nd: round(v / total, 6) for nd, v in scores.items()}

        if self._storage:
            for node_id, score in scores.items():
                self._storage.save_reputation_score(node_id, score)

        return scores

    def get_scores(self) -> dict[str, float]:
        """Return persisted scores without re-computing."""
        if self._storage:
            return self._storage.get_reputation_scores()
        return {}
