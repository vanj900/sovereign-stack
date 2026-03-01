"""
ghostbrain.py — GhostBrain: demand forecasting + grid-former election.
=======================================================================
Implements:
  - 12-hour rolling demand forecast (exponential weighted average)
  - SoC floor enforcement: default 25 % or predicted <20 % in 6 h
  - Rate-limiter: export ramp ≤ ±300 W/min
  - Primary grid-former election: highest (SoC + uptime_bonus + receipt_bonus)
    among nodes that have spoken on Shadow-Net within the last 3 minutes.
  - Shadow-Net silence detection: >3 min → all nodes go standalone.

Philosophy: Flow Over Containment.
  GhostBrain proposes; the coupler firmware enforces.
  GhostBrain never issues hard hardware commands — it emits advisory signals
  that the coupler's safety layer can override.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants (spec-derived)
# ---------------------------------------------------------------------------

DEFAULT_SOC_FLOOR: float = 25.0          # % — never export below this
SOC_FLOOR_FORECAST_THRESHOLD: float = 20.0  # % — if 6-h forecast < 20 %, lock out
FORECAST_HORIZON_H: float = 12.0         # hours for full demand forecast window
ELECTION_INTERVAL_S: float = 15 * 60     # 15 minutes
SHADOW_NET_TIMEOUT_S: float = 3 * 60     # 3 minutes silence → standalone
MAX_RAMP_RATE_W_PER_MIN: float = 300.0   # ±300 W/min export ramp
EWA_ALPHA: float = 0.2                   # exponential weighted average smoothing


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class NodeState:
    """Live snapshot of one Cell node as seen by GhostBrain."""
    node_id: str
    soc: float                  # battery state-of-charge [0–100 %]
    last_seen: float            # unix timestamp of last Shadow-Net packet
    uptime_s: float = 0.0       # inverter uptime in seconds
    receipt_count: int = 0      # number of signed energy-transfer deeds issued
    is_grid_forming: bool = False

    def is_reachable(self, now: Optional[float] = None) -> bool:
        """True if node has been heard within SHADOW_NET_TIMEOUT_S."""
        t = now if now is not None else time.time()
        return (t - self.last_seen) < SHADOW_NET_TIMEOUT_S


@dataclass
class DemandSample:
    """Single power-demand observation."""
    timestamp: float   # unix timestamp
    power_w: float     # net demand in watts (positive = consumption)


@dataclass
class ForecastResult:
    """Output of GhostBrain.forecast()."""
    horizon_h: float
    predicted_demand_w: float       # average demand over horizon
    predicted_soc_at_6h: float      # estimated SoC in 6 hours
    export_locked: bool             # True when SoC floor would be breached
    reason: str                     # human-readable explanation


# ---------------------------------------------------------------------------
# GhostBrain core
# ---------------------------------------------------------------------------

class GhostBrain:
    """
    Demand forecasting and grid-former election brain for one Cell node.

    Usage::

        brain = GhostBrain(node_id="node1", battery_capacity_wh=7000)
        brain.record_demand(1500.0)   # call every minute with load reading
        forecast = brain.forecast()
        winner = brain.elect_grid_former(peers)
    """

    def __init__(
        self,
        node_id: str,
        battery_capacity_wh: float = 7000.0,
        soc_floor: float = DEFAULT_SOC_FLOOR,
    ) -> None:
        self.node_id = node_id
        self.battery_capacity_wh = battery_capacity_wh
        self.soc_floor = soc_floor

        self._samples: List[DemandSample] = []
        self._ewa_demand: Optional[float] = None     # exponential weighted average W
        self._last_export_setpoint_w: float = 0.0   # previous export command
        self._peer_states: Dict[str, NodeState] = {}
        self._last_election_ts: float = 0.0
        self._elected_grid_former: Optional[str] = None

    # ── Demand recording ──────────────────────────────────────────────────

    def record_demand(self, power_w: float, timestamp: Optional[float] = None) -> None:
        """
        Record a new demand sample (watts).

        Updates the internal exponential weighted average used for forecasting.
        Old samples beyond 12 h are pruned to bound memory usage.
        """
        ts = timestamp if timestamp is not None else time.time()
        sample = DemandSample(timestamp=ts, power_w=power_w)
        self._samples.append(sample)

        # Update EWA
        if self._ewa_demand is None:
            self._ewa_demand = power_w
        else:
            self._ewa_demand = EWA_ALPHA * power_w + (1 - EWA_ALPHA) * self._ewa_demand

        # Prune samples older than FORECAST_HORIZON_H
        cutoff = ts - FORECAST_HORIZON_H * 3600
        self._samples = [s for s in self._samples if s.timestamp >= cutoff]

    # ── Forecasting ───────────────────────────────────────────────────────

    def forecast(
        self,
        current_soc: float,
        current_timestamp: Optional[float] = None,
    ) -> ForecastResult:
        """
        Produce a demand forecast and decide whether export is permitted.

        Parameters
        ----------
        current_soc : float  — current battery SoC [0–100 %]
        current_timestamp : float | None  — unix timestamp (default: now)

        Returns
        -------
        ForecastResult
        """
        now = current_timestamp if current_timestamp is not None else time.time()

        # Average demand over the last available window
        if self._ewa_demand is not None:
            avg_demand_w = self._ewa_demand
        elif self._samples:
            avg_demand_w = sum(s.power_w for s in self._samples) / len(self._samples)
        else:
            avg_demand_w = 0.0

        # Estimate SoC in 6 hours given current demand and no solar/export change
        # Energy drawn in 6 h  = avg_demand_w * 6  Wh
        energy_drawn_6h = avg_demand_w * 6.0
        soc_delta_6h = (energy_drawn_6h / self.battery_capacity_wh) * 100.0
        predicted_soc_6h = max(0.0, current_soc - soc_delta_6h)

        # Export lock-out rules
        if current_soc <= self.soc_floor:
            locked = True
            reason = (
                f"SoC {current_soc:.1f}% at or below floor {self.soc_floor:.1f}%"
            )
        elif predicted_soc_6h < SOC_FLOOR_FORECAST_THRESHOLD:
            locked = True
            reason = (
                f"6-h SoC forecast {predicted_soc_6h:.1f}% < "
                f"threshold {SOC_FLOOR_FORECAST_THRESHOLD:.1f}%"
            )
        else:
            locked = False
            reason = (
                f"SoC {current_soc:.1f}% above floor; "
                f"6-h forecast {predicted_soc_6h:.1f}% safe"
            )

        return ForecastResult(
            horizon_h=FORECAST_HORIZON_H,
            predicted_demand_w=avg_demand_w,
            predicted_soc_at_6h=predicted_soc_6h,
            export_locked=locked,
            reason=reason,
        )

    # ── Ramp-rate limiter ─────────────────────────────────────────────────

    def clamp_export_setpoint(
        self,
        requested_w: float,
        elapsed_s: float = 60.0,
    ) -> float:
        """
        Apply ±300 W/min ramp-rate limit to an export setpoint change.

        Parameters
        ----------
        requested_w : float  — new desired export setpoint (W)
        elapsed_s   : float  — seconds since last setpoint update (default 60 s)

        Returns
        -------
        float  — clamped export setpoint (W)
        """
        max_delta = MAX_RAMP_RATE_W_PER_MIN * (elapsed_s / 60.0)
        delta = requested_w - self._last_export_setpoint_w
        clamped_delta = max(-max_delta, min(max_delta, delta))
        new_setpoint = self._last_export_setpoint_w + clamped_delta
        self._last_export_setpoint_w = new_setpoint
        return new_setpoint

    # ── Peer management ───────────────────────────────────────────────────

    def update_peer(self, state: NodeState) -> None:
        """Register or update a peer node state from a Shadow-Net packet."""
        self._peer_states[state.node_id] = state

    def reachable_peers(
        self, now: Optional[float] = None
    ) -> List[NodeState]:
        """Return peers heard within SHADOW_NET_TIMEOUT_S, including self placeholder."""
        t = now if now is not None else time.time()
        return [s for s in self._peer_states.values() if s.is_reachable(t)]

    def shadow_net_silent(self, now: Optional[float] = None) -> bool:
        """
        Return True when ALL known peers have been silent for ≥ SHADOW_NET_TIMEOUT_S.

        If no peers are known (fresh boot), returns False.
        """
        if not self._peer_states:
            return False
        t = now if now is not None else time.time()
        return all(
            (t - s.last_seen) >= SHADOW_NET_TIMEOUT_S
            for s in self._peer_states.values()
        )

    # ── Grid-former election ──────────────────────────────────────────────

    def election_score(self, state: NodeState) -> float:
        """
        Compute election score for a node.

        Score = soc_component + uptime_bonus + receipt_bonus

        Weights are chosen so that a node with 80 % SoC, 24 h uptime, and
        10 receipts comfortably wins over one with 60 % SoC but no history.
        """
        soc_component = state.soc                            # 0–100
        uptime_bonus = min(state.uptime_s / 3600.0, 24.0)   # cap at 24 h → 0–24
        receipt_bonus = math.log1p(state.receipt_count) * 5  # diminishing returns
        return soc_component + uptime_bonus + receipt_bonus

    def elect_grid_former(
        self,
        candidates: Optional[List[NodeState]] = None,
        now: Optional[float] = None,
    ) -> Optional[str]:
        """
        Elect the primary grid-former among reachable nodes.

        Returns the node_id of the winner, or None if no reachable nodes.
        Re-election runs every ELECTION_INTERVAL_S; caller may force a fresh
        election by passing candidates explicitly.

        Rules (from spec):
          - Highest election_score() wins.
          - Only reachable nodes (heard < 3 min ago) are eligible.
          - Shadow-Net silent → return None (every node goes standalone).
        """
        t = now if now is not None else time.time()

        if candidates is None:
            candidates = self.reachable_peers(t)

        if not candidates:
            self._elected_grid_former = None
            return None

        # Filter to reachable only
        eligible = [c for c in candidates if c.is_reachable(t)]
        if not eligible:
            self._elected_grid_former = None
            return None

        winner = max(eligible, key=self.election_score)
        self._elected_grid_former = winner.node_id
        self._last_election_ts = t
        return winner.node_id

    @property
    def elected_grid_former(self) -> Optional[str]:
        """Currently elected grid-former node_id (may be stale between elections)."""
        return self._elected_grid_former

    # ── Shadow-Net packet builder ─────────────────────────────────────────

    def build_shadow_packet(
        self,
        current_soc: float,
        current_timestamp: Optional[float] = None,
    ) -> dict:
        """
        Build the 1-packet-per-30-s Shadow-Net LoRa broadcast payload.

        Returns a dict that can be JSON-serialised and sent via Meshtastic.

        Fields:
          node_id, soc, forecast_12h_w, elected_grid_former, ts
        """
        now = current_timestamp if current_timestamp is not None else time.time()
        fc = self.forecast(current_soc, now)
        return {
            "node_id": self.node_id,
            "soc": round(current_soc, 1),
            "forecast_12h_w": round(fc.predicted_demand_w, 1),
            "export_locked": fc.export_locked,
            "elected_grid_former": self._elected_grid_former,
            "ts": int(now),
        }
