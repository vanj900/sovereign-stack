"""
coupler.py — Per-node Energy Coupler firmware (AC-Coupled, v1).
===============================================================
Implements the state machine for a single Coupler Box on the shared 240 V bus.

Physical components modelled:
  - 100 A 4-pole contactor (physical bus isolation in < 50 ms)
  - DC shunt meter (battery bank, true energy leaving your bank)
  - AC CT clamp meter (bus delivery, what actually arrived)
  - Safety relay: undervoltage trip at 110 V sustained
  - Overcurrent trip: >80 A for >100 ms → open contactor

Control flow:
  1. Poll inverter Modbus registers every second.
  2. GhostBrain evaluates SoC forecast → set export permission.
  3. Shadow-Net packet received → update peer state.
  4. Every 15 min → re-elect primary grid-former via GhostBrain.
  5. If Shadow-Net silent >3 min → enter STANDALONE mode (zero export).
  6. Safety checks run continuously regardless of GhostBrain state.

Philosophy: Flow Over Containment.
  If this coupler crashes or the bus disconnects, the node stays live on its
  own inverter.  Standalone is the safe default, not the failure state.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Dict, List, Optional

from .ghostbrain import GhostBrain, NodeState
from .integrity_chain import EnergyDeed, IntegrityChain


# ---------------------------------------------------------------------------
# Constants (spec-derived)
# ---------------------------------------------------------------------------

UNDERVOLTAGE_TRIP_V: float = 110.0         # V — trip contactor if AC < this
UNDERVOLTAGE_TRIP_HOLD_S: float = 1.0      # seconds sustained < threshold
OVERCURRENT_TRIP_A: float = 80.0           # A — trip if current > this
OVERCURRENT_TRIP_HOLD_S: float = 0.1       # seconds (100 ms)
OVERCURRENT_TRIP_HOLD_MS: float = OVERCURRENT_TRIP_HOLD_S * 1000
ELECTION_INTERVAL_S: float = 15 * 60.0     # 15 minutes
SHADOW_NET_PACKET_INTERVAL_S: float = 30.0 # max 1 packet per 30 s
SHADOW_NET_TIMEOUT_S: float = 3 * 60.0     # 3 minutes silence → standalone
MODBUS_POLL_INTERVAL_S: float = 1.0        # poll inverter every second


# ---------------------------------------------------------------------------
# Coupler state machine
# ---------------------------------------------------------------------------

class CouplerState(Enum):
    STANDALONE   = auto()   # contactor open, zero export, fully independent
    CONNECTED    = auto()   # contactor closed, participating in shared bus
    GRID_FORMING = auto()   # contactor closed, this node is primary grid-former
    FAULTED      = auto()   # contactor open, safety trip — requires manual reset


# ---------------------------------------------------------------------------
# Meter readings
# ---------------------------------------------------------------------------

@dataclass
class MeterReading:
    """Dual metering snapshot (DC shunt + AC CT clamp)."""
    timestamp: float       # unix timestamp
    dc_voltage_v: float    # battery bank voltage (DC shunt)
    dc_current_a: float    # battery bank current, + = discharging
    ac_voltage_v: float    # AC bus voltage at coupler output
    ac_current_a: float    # AC current at coupler output
    soc_pct: float         # battery state-of-charge [0–100 %]

    @property
    def dc_power_w(self) -> float:
        return self.dc_voltage_v * self.dc_current_a

    @property
    def ac_power_w(self) -> float:
        return self.ac_voltage_v * self.ac_current_a


# ---------------------------------------------------------------------------
# Coupler Box
# ---------------------------------------------------------------------------

class CouplerBox:
    """
    Software model of one per-node Coupler Box.

    In production this class runs on a Raspberry Pi CM4 or ESP32-S3 and calls
    real Modbus/GPIO drivers.  In tests, all hardware calls are replaced by
    injected callbacks so the logic can run without hardware.

    Parameters
    ----------
    node_id         : str   — unique node identifier
    brain           : GhostBrain
    chain           : IntegrityChain
    read_meters     : Callable[[], MeterReading]   — hardware abstraction
    set_contactor   : Callable[[bool], None]       — True = closed (connected)
    set_export_w    : Callable[[float], None]      — set inverter export setpoint
    set_grid_forming: Callable[[bool], None]       — True = grid-forming mode
    """

    def __init__(
        self,
        node_id: str,
        brain: GhostBrain,
        chain: IntegrityChain,
        read_meters: Callable[[], MeterReading],
        set_contactor: Optional[Callable[[bool], None]] = None,
        set_export_w: Optional[Callable[[float], None]] = None,
        set_grid_forming: Optional[Callable[[bool], None]] = None,
    ) -> None:
        self.node_id = node_id
        self.brain = brain
        self.chain = chain
        self._read_meters = read_meters
        self._set_contactor = set_contactor or (lambda _: None)
        self._set_export_w = set_export_w or (lambda _: None)
        self._set_grid_forming = set_grid_forming or (lambda _: None)

        self._state: CouplerState = CouplerState.STANDALONE
        self._contactor_closed: bool = False
        self._last_election_ts: float = 0.0
        self._last_shadow_packet_ts: float = 0.0

        # Safety tracking
        self._undervoltage_start: Optional[float] = None
        self._overcurrent_start: Optional[float] = None

        # Energy accumulation for deed generation (kWh since last deed)
        self._dc_wh_acc: float = 0.0
        self._ac_wh_acc: float = 0.0
        self._last_meter_ts: Optional[float] = None

        self._fault_reason: str = ""
        self._event_log: List[Dict] = []

    # ── State ──────────────────────────────────────────────────────────────

    @property
    def state(self) -> CouplerState:
        return self._state

    @property
    def contactor_closed(self) -> bool:
        return self._contactor_closed

    # ── Main tick (call every MODBUS_POLL_INTERVAL_S) ─────────────────────

    def tick(self, now: Optional[float] = None) -> None:
        """
        One control-loop iteration.

        1. Read meters.
        2. Run safety checks (these can trip the contactor immediately).
        3. If not faulted: run GhostBrain advisory checks.
        4. Accumulate energy for deed generation.
        """
        t = now if now is not None else time.time()
        reading = self._read_meters()

        # Safety checks always run first, regardless of state
        self._check_undervoltage(reading, t)
        self._check_overcurrent(reading, t)

        if self._state == CouplerState.FAULTED:
            return

        # Shadow-Net timeout → standalone
        if self.brain.shadow_net_silent(t):
            if self._state != CouplerState.STANDALONE:
                self._log("shadow_net_timeout", "Silence > 3 min → STANDALONE")
                self._enter_standalone()
            return

        # GhostBrain forecast advisory
        fc = self.brain.forecast(reading.soc_pct, t)
        if fc.export_locked and self._state == CouplerState.CONNECTED:
            self._log("export_locked", fc.reason)
            self._set_export_w(0.0)

        # Accumulate energy when contactor is closed
        if self._contactor_closed:
            self._accumulate_energy(reading, t)

    # ── Shadow-Net packet handler ─────────────────────────────────────────

    def on_shadow_packet(
        self,
        peer_state: NodeState,
        now: Optional[float] = None,
    ) -> None:
        """
        Called when a Shadow-Net LoRa packet is received from a peer.

        Updates GhostBrain peer state and triggers grid-former election if
        the election interval has elapsed.
        """
        t = now if now is not None else time.time()
        self.brain.update_peer(peer_state)
        self._last_shadow_packet_ts = t

        if (t - self._last_election_ts) >= ELECTION_INTERVAL_S:
            self._run_election(t)

    # ── Bus connect / disconnect ──────────────────────────────────────────

    def connect_to_bus(self, now: Optional[float] = None) -> bool:
        """
        Attempt to close the contactor and join the shared AC bus.

        Returns True on success, False if export is locked or node is faulted.
        """
        t = now if now is not None else time.time()
        if self._state == CouplerState.FAULTED:
            self._log("connect_refused", "Node is FAULTED — manual reset required")
            return False
        reading = self._read_meters()
        fc = self.brain.forecast(reading.soc_pct, t)
        if fc.export_locked:
            self._log("connect_refused", f"Export locked: {fc.reason}")
            return False
        self._close_contactor()
        self._state = CouplerState.CONNECTED
        self._log("connected", "Contactor closed — joined shared bus")
        return True

    def disconnect_from_bus(self, reason: str = "manual") -> None:
        """Open the contactor and enter STANDALONE mode."""
        self._open_contactor()
        self._state = CouplerState.STANDALONE
        self._log("disconnected", reason)

    # ── Energy deed generation ────────────────────────────────────────────

    def close_transfer_deed(
        self,
        to_node: str,
        now: Optional[float] = None,
    ) -> Optional[EnergyDeed]:
        """
        Finalise an energy transfer deed from accumulated DC/AC meter data.

        Call this after a defined transfer window (e.g., every 15 min or
        on disconnect).  Returns None if no energy has been transferred.
        """
        if self._dc_wh_acc <= 0:
            return None
        t = now if now is not None else time.time()
        deed = EnergyDeed.create(
            from_node=self.node_id,
            to_node=to_node,
            dc_kwh=self._dc_wh_acc / 1000.0,
            ac_kwh=self._ac_wh_acc / 1000.0,
            timestamp=t,
        )
        self.chain.record(deed)
        self._log("deed_recorded", deed.to_dict())
        # Reset accumulators
        self._dc_wh_acc = 0.0
        self._ac_wh_acc = 0.0
        return deed

    # ── Safety internals ──────────────────────────────────────────────────

    def _check_undervoltage(self, reading: MeterReading, now: float) -> None:
        """Trip contactor if AC voltage sustained below UNDERVOLTAGE_TRIP_V."""
        if reading.ac_voltage_v < UNDERVOLTAGE_TRIP_V and self._contactor_closed:
            if self._undervoltage_start is None:
                self._undervoltage_start = now
            elif (now - self._undervoltage_start) >= UNDERVOLTAGE_TRIP_HOLD_S:
                self._log(
                    "undervoltage_trip",
                    f"AC {reading.ac_voltage_v:.1f} V < {UNDERVOLTAGE_TRIP_V} V "
                    f"for {UNDERVOLTAGE_TRIP_HOLD_S} s",
                )
                self._fault(
                    f"Undervoltage trip: {reading.ac_voltage_v:.1f} V"
                )
        else:
            self._undervoltage_start = None

    def _check_overcurrent(self, reading: MeterReading, now: float) -> None:
        """Trip contactor if AC current exceeds OVERCURRENT_TRIP_A for 100 ms."""
        if abs(reading.ac_current_a) > OVERCURRENT_TRIP_A and self._contactor_closed:
            if self._overcurrent_start is None:
                self._overcurrent_start = now
            elif (now - self._overcurrent_start) >= OVERCURRENT_TRIP_HOLD_S:
                self._log(
                    "overcurrent_trip",
                    f"AC {reading.ac_current_a:.1f} A > {OVERCURRENT_TRIP_A} A "
                    f"for {OVERCURRENT_TRIP_HOLD_MS:.0f} ms",
                )
                self._fault(
                    f"Overcurrent trip: {reading.ac_current_a:.1f} A"
                )
        else:
            self._overcurrent_start = None

    # ── Grid-former election internals ────────────────────────────────────

    def _run_election(self, now: float) -> None:
        """Re-elect the primary grid-former and update inverter mode."""
        winner = self.brain.elect_grid_former(now=now)
        self._last_election_ts = now

        if winner == self.node_id:
            if self._state != CouplerState.GRID_FORMING:
                self._state = CouplerState.GRID_FORMING
                self._set_grid_forming(True)
                self._log("grid_former_elected", f"{self.node_id} is now grid-former")
        else:
            if self._state == CouplerState.GRID_FORMING:
                self._state = CouplerState.CONNECTED
                self._set_grid_forming(False)
                self._log("grid_former_yielded", f"Yielded to {winner}")

    # ── Energy accumulation ───────────────────────────────────────────────

    def _accumulate_energy(self, reading: MeterReading, now: float) -> None:
        """Integrate power readings into Wh accumulators (trapezoidal rule)."""
        if self._last_meter_ts is not None:
            dt_h = (now - self._last_meter_ts) / 3600.0
            # Only accumulate when exporting (dc_current > 0 = discharging)
            if reading.dc_current_a > 0:
                self._dc_wh_acc += reading.dc_power_w * dt_h
                self._ac_wh_acc += reading.ac_power_w * dt_h
        self._last_meter_ts = now

    # ── Contactor helpers ─────────────────────────────────────────────────

    def _close_contactor(self) -> None:
        self._contactor_closed = True
        self._set_contactor(True)

    def _open_contactor(self) -> None:
        self._contactor_closed = False
        self._set_contactor(False)
        self._dc_wh_acc = 0.0
        self._ac_wh_acc = 0.0
        self._last_meter_ts = None

    def _enter_standalone(self) -> None:
        self._open_contactor()
        self._set_export_w(0.0)
        self._state = CouplerState.STANDALONE

    def _fault(self, reason: str) -> None:
        self._fault_reason = reason
        self._open_contactor()
        self._set_export_w(0.0)
        self._state = CouplerState.FAULTED
        self._log("faulted", reason)

    # ── Manual reset ──────────────────────────────────────────────────────

    def reset_fault(self) -> None:
        """
        Clear the FAULTED state after a human has inspected and reset the box.

        This does NOT automatically reconnect to the bus.
        """
        if self._state == CouplerState.FAULTED:
            self._state = CouplerState.STANDALONE
            self._fault_reason = ""
            self._undervoltage_start = None
            self._overcurrent_start = None
            self._log("fault_reset", "Manual reset by operator")

    # ── Logging ───────────────────────────────────────────────────────────

    def _log(self, event: str, detail) -> None:
        entry = {
            "event": event,
            "node": self.node_id,
            "ts": time.time(),
            "detail": detail,
        }
        self._event_log.append(entry)

    @property
    def event_log(self) -> List[Dict]:
        """Read-only view of the coupler event log."""
        return list(self._event_log)

    @property
    def fault_reason(self) -> str:
        return self._fault_reason

