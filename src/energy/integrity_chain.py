"""
integrity_chain.py — Energy transfer deed logging on the Integrity Chain.
==========================================================================
Every joule shared between nodes is logged as a cryptographic deed.
The chain of deeds is hash-linked so any tamper is immediately detectable.

Deed format (JSON, per spec):
  {
    "type": "energy_transfer",
    "from": "node1",
    "to": "node2",
    "dc_kwh": 1.23,
    "ac_kwh": 1.14,
    "loss_percent": 7.3,
    "timestamp": "2026-03-02T14:22:00Z",
    "signature": "..."
  }

Philosophy: Truth by Receipts.
  Every transfer is a signed deed.  No deed = no joule moved.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Deed model
# ---------------------------------------------------------------------------

@dataclass
class EnergyDeed:
    """Immutable record of one energy transfer between two Cell nodes."""

    from_node: str            # source node_id
    to_node: str              # destination node_id
    dc_kwh: float             # energy leaving source battery bank (DC shunt)
    ac_kwh: float             # energy arriving at destination (AC CT clamp)
    loss_percent: float       # (dc_kwh - ac_kwh) / dc_kwh * 100
    timestamp: str            # ISO 8601 UTC
    deed_id: str = ""         # hex digest, set by IntegrityChain.record()
    signature: str = ""       # hex digest (stub; real impl uses node private key)

    @classmethod
    def create(
        cls,
        from_node: str,
        to_node: str,
        dc_kwh: float,
        ac_kwh: float,
        timestamp: Optional[float] = None,
    ) -> "EnergyDeed":
        """
        Construct a new EnergyDeed, computing loss_percent automatically.

        Parameters
        ----------
        from_node : str    — node_id of the exporting node
        to_node   : str    — node_id of the importing node
        dc_kwh    : float  — kWh measured at DC shunt (exporter battery)
        ac_kwh    : float  — kWh measured at AC CT clamp (bus delivery)
        timestamp : float | None  — unix timestamp (default: now)
        """
        ts_unix = timestamp if timestamp is not None else time.time()
        ts_iso = datetime.fromtimestamp(ts_unix, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        if dc_kwh > 0:
            loss_pct = round((dc_kwh - ac_kwh) / dc_kwh * 100, 2)
        else:
            loss_pct = 0.0
        return cls(
            from_node=from_node,
            to_node=to_node,
            dc_kwh=round(dc_kwh, 4),
            ac_kwh=round(ac_kwh, 4),
            loss_percent=loss_pct,
            timestamp=ts_iso,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to the canonical deed JSON dict (spec format)."""
        return {
            "type": "energy_transfer",
            "from": self.from_node,
            "to": self.to_node,
            "dc_kwh": self.dc_kwh,
            "ac_kwh": self.ac_kwh,
            "loss_percent": self.loss_percent,
            "timestamp": self.timestamp,
            "signature": self.signature,
        }

    def to_json(self) -> str:
        """Serialise to compact JSON string."""
        return json.dumps(self.to_dict(), separators=(",", ":"))


# ---------------------------------------------------------------------------
# Hash-chain block
# ---------------------------------------------------------------------------

@dataclass
class ChainBlock:
    """One block in the Integrity Chain."""
    index: int
    deed: EnergyDeed
    prev_hash: str            # hash of previous block ("0" * 64 for genesis)
    hash: str = ""            # SHA-256 hex digest of this block's content

    def _content_bytes(self) -> bytes:
        payload = {
            "index": self.index,
            "prev_hash": self.prev_hash,
            "deed": self.deed.to_dict(),
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    def compute_hash(self) -> str:
        """Return the SHA-256 hex digest of this block's immutable content."""
        return hashlib.sha256(self._content_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Integrity Chain
# ---------------------------------------------------------------------------

class IntegrityChain:
    """
    Append-only hash-linked chain of EnergyDeed records.

    Usage::

        chain = IntegrityChain(node_id="node1")
        deed = EnergyDeed.create("node1", "node2", dc_kwh=1.23, ac_kwh=1.14)
        chain.record(deed)
        assert chain.verify()
    """

    def __init__(self, node_id: str, private_key: str = "") -> None:
        self.node_id = node_id
        self._private_key = private_key   # stub: real impl = ed25519 / nostr key
        self._chain: List[ChainBlock] = []

    # ── Recording ─────────────────────────────────────────────────────────

    def record(self, deed: EnergyDeed) -> ChainBlock:
        """
        Append a deed to the Integrity Chain.

        Sets deed.deed_id and deed.signature before appending.
        Returns the new ChainBlock.
        """
        prev_hash = self._chain[-1].hash if self._chain else "0" * 64

        # Sign the deed payload (stub: sha256(key + payload))
        payload_json = deed.to_json()
        deed.deed_id = hashlib.sha256(
            f"{self.node_id}{deed.timestamp}{payload_json}".encode()
        ).hexdigest()[:16]
        deed.signature = self._sign(payload_json)

        block = ChainBlock(
            index=len(self._chain),
            deed=deed,
            prev_hash=prev_hash,
        )
        block.hash = block.compute_hash()
        self._chain.append(block)
        return block

    def _sign(self, payload: str) -> str:
        """
        Stub signature: sha256(private_key + payload).

        Real implementation swaps in ed25519 / nostr signing without changing
        the rest of the chain logic (Forkability axiom).
        """
        key = self._private_key or self.node_id
        return hashlib.sha256((key + payload).encode()).hexdigest()

    # ── Verification ──────────────────────────────────────────────────────

    def verify(self) -> bool:
        """
        Verify the entire chain's hash linkage.

        Returns True if every block's stored hash matches its recomputed hash
        and every block's prev_hash matches the previous block's hash.
        """
        for i, block in enumerate(self._chain):
            if block.hash != block.compute_hash():
                return False
            expected_prev = self._chain[i - 1].hash if i > 0 else "0" * 64
            if block.prev_hash != expected_prev:
                return False
        return True

    # ── Accessors ─────────────────────────────────────────────────────────

    def deeds(self) -> List[EnergyDeed]:
        """Return all recorded deeds in chronological order."""
        return [b.deed for b in self._chain]

    def latest_block(self) -> Optional[ChainBlock]:
        """Return the most recently appended block, or None if chain is empty."""
        return self._chain[-1] if self._chain else None

    def __len__(self) -> int:
        return len(self._chain)

    def export_json(self) -> str:
        """Serialise the full chain to a JSON array (for off-node backup)."""
        chain_data = [
            {
                "index": b.index,
                "prev_hash": b.prev_hash,
                "hash": b.hash,
                "deed": b.deed.to_dict(),
            }
            for b in self._chain
        ]
        return json.dumps(chain_data, indent=2)
