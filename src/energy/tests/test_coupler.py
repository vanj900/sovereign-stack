"""
Tests for energy.coupler — CouplerBox state machine and safety logic.
"""
import sys
import os
import time
import unittest
from unittest.mock import MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from energy.coupler import (
    CouplerBox,
    CouplerState,
    MeterReading,
    UNDERVOLTAGE_TRIP_V,
    UNDERVOLTAGE_TRIP_HOLD_S,
    OVERCURRENT_TRIP_A,
    OVERCURRENT_TRIP_HOLD_S,
    SHADOW_NET_TIMEOUT_S,
)
from energy.ghostbrain import GhostBrain, NodeState
from energy.integrity_chain import IntegrityChain


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_meter(
    ac_voltage=120.0,
    ac_current=10.0,
    dc_voltage=48.0,
    dc_current=20.0,
    soc=75.0,
) -> MeterReading:
    return MeterReading(
        timestamp=time.time(),
        dc_voltage_v=dc_voltage,
        dc_current_a=dc_current,
        ac_voltage_v=ac_voltage,
        ac_current_a=ac_current,
        soc_pct=soc,
    )


def _make_coupler(node_id="node1", soc=75.0, battery_wh=7000.0):
    brain = GhostBrain(node_id, battery_capacity_wh=battery_wh)
    chain = IntegrityChain(node_id)
    contactor_calls = []
    export_calls = []
    grid_forming_calls = []

    def read_meters():
        return _make_meter(soc=soc)

    coupler = CouplerBox(
        node_id=node_id,
        brain=brain,
        chain=chain,
        read_meters=read_meters,
        set_contactor=lambda v: contactor_calls.append(v),
        set_export_w=lambda v: export_calls.append(v),
        set_grid_forming=lambda v: grid_forming_calls.append(v),
    )
    return coupler, brain, chain, contactor_calls, export_calls, grid_forming_calls


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

class TestCouplerInitialState(unittest.TestCase):

    def test_initial_state_is_standalone(self):
        coupler, *_ = _make_coupler()
        self.assertEqual(coupler.state, CouplerState.STANDALONE)

    def test_contactor_initially_open(self):
        coupler, *_ = _make_coupler()
        self.assertFalse(coupler.contactor_closed)


# ---------------------------------------------------------------------------
# Connect / disconnect
# ---------------------------------------------------------------------------

class TestCouplerConnectDisconnect(unittest.TestCase):

    def test_connect_closes_contactor_when_soc_ok(self):
        coupler, brain, chain, contactor_calls, _, _ = _make_coupler(soc=80.0)
        # Feed in a peer so shadow_net_silent() returns False
        peer = NodeState("node2", soc=70.0, last_seen=time.time())
        brain.update_peer(peer)
        ok = coupler.connect_to_bus()
        self.assertTrue(ok)
        self.assertEqual(coupler.state, CouplerState.CONNECTED)
        self.assertTrue(coupler.contactor_closed)
        self.assertIn(True, contactor_calls)

    def test_connect_refused_when_soc_below_floor(self):
        coupler, brain, chain, contactor_calls, _, _ = _make_coupler(soc=10.0)
        brain.record_demand(500.0)
        ok = coupler.connect_to_bus()
        self.assertFalse(ok)
        self.assertEqual(coupler.state, CouplerState.STANDALONE)
        self.assertFalse(coupler.contactor_closed)

    def test_disconnect_opens_contactor(self):
        coupler, brain, chain, contactor_calls, _, _ = _make_coupler(soc=80.0)
        peer = NodeState("node2", soc=70.0, last_seen=time.time())
        brain.update_peer(peer)
        coupler.connect_to_bus()
        coupler.disconnect_from_bus("test")
        self.assertEqual(coupler.state, CouplerState.STANDALONE)
        self.assertFalse(coupler.contactor_closed)
        self.assertIn(False, contactor_calls)

    def test_connect_refused_when_faulted(self):
        coupler, brain, chain, _, export_calls, _ = _make_coupler(soc=80.0)
        peer = NodeState("node2", soc=70.0, last_seen=time.time())
        brain.update_peer(peer)
        # Force a fault
        coupler._fault("test fault")
        ok = coupler.connect_to_bus()
        self.assertFalse(ok)
        self.assertEqual(coupler.state, CouplerState.FAULTED)


# ---------------------------------------------------------------------------
# Safety — undervoltage
# ---------------------------------------------------------------------------

class TestUndervoltageTrip(unittest.TestCase):

    def test_undervoltage_trips_after_hold(self):
        brain = GhostBrain("node1", 7000.0)
        chain = IntegrityChain("node1")
        peer = NodeState("node2", soc=70.0, last_seen=time.time())
        brain.update_peer(peer)

        low_reading = _make_meter(ac_voltage=109.0, soc=80.0)  # below threshold

        coupler = CouplerBox(
            "node1", brain, chain,
            read_meters=lambda: low_reading,
        )
        coupler.connect_to_bus()
        self.assertTrue(coupler.contactor_closed)

        # First tick at undervoltage — starts the timer, should NOT trip yet
        t0 = time.time()
        coupler._check_undervoltage(low_reading, t0)
        self.assertEqual(coupler.state, CouplerState.CONNECTED)

        # Second tick after hold duration — should trip
        coupler._check_undervoltage(
            low_reading, t0 + UNDERVOLTAGE_TRIP_HOLD_S + 0.1
        )
        self.assertEqual(coupler.state, CouplerState.FAULTED)
        self.assertFalse(coupler.contactor_closed)

    def test_undervoltage_resets_on_recovery(self):
        brain = GhostBrain("node1", 7000.0)
        chain = IntegrityChain("node1")
        peer = NodeState("node2", soc=70.0, last_seen=time.time())
        brain.update_peer(peer)
        coupler = CouplerBox("node1", brain, chain, read_meters=lambda: _make_meter())
        coupler.connect_to_bus()
        t0 = time.time()
        low_reading = _make_meter(ac_voltage=108.0)
        coupler._check_undervoltage(low_reading, t0)
        # Voltage recovers — timer should reset
        ok_reading = _make_meter(ac_voltage=120.0)
        coupler._check_undervoltage(ok_reading, t0 + 0.5)
        self.assertIsNone(coupler._undervoltage_start)
        self.assertEqual(coupler.state, CouplerState.CONNECTED)


# ---------------------------------------------------------------------------
# Safety — overcurrent
# ---------------------------------------------------------------------------

class TestOvercurrentTrip(unittest.TestCase):

    def test_overcurrent_trips_after_hold(self):
        brain = GhostBrain("node1", 7000.0)
        chain = IntegrityChain("node1")
        peer = NodeState("node2", soc=70.0, last_seen=time.time())
        brain.update_peer(peer)
        coupler = CouplerBox("node1", brain, chain, read_meters=lambda: _make_meter())
        coupler.connect_to_bus()

        t0 = time.time()
        oc_reading = _make_meter(ac_current=90.0)  # > OVERCURRENT_TRIP_A
        coupler._check_overcurrent(oc_reading, t0)
        self.assertEqual(coupler.state, CouplerState.CONNECTED)

        # After hold duration → trip
        coupler._check_overcurrent(
            oc_reading, t0 + OVERCURRENT_TRIP_HOLD_S + 0.01
        )
        self.assertEqual(coupler.state, CouplerState.FAULTED)

    def test_overcurrent_within_limit_no_trip(self):
        brain = GhostBrain("node1", 7000.0)
        chain = IntegrityChain("node1")
        peer = NodeState("node2", soc=70.0, last_seen=time.time())
        brain.update_peer(peer)
        coupler = CouplerBox("node1", brain, chain, read_meters=lambda: _make_meter())
        coupler.connect_to_bus()
        normal = _make_meter(ac_current=OVERCURRENT_TRIP_A - 1)
        coupler._check_overcurrent(normal, time.time())
        self.assertEqual(coupler.state, CouplerState.CONNECTED)


# ---------------------------------------------------------------------------
# Shadow-Net timeout → STANDALONE
# ---------------------------------------------------------------------------

class TestShadowNetTimeout(unittest.TestCase):

    def test_tick_enters_standalone_on_silence(self):
        brain = GhostBrain("node1", 7000.0)
        chain = IntegrityChain("node1")

        old_ts = time.time() - SHADOW_NET_TIMEOUT_S - 10
        stale_peer = NodeState("node2", soc=70.0, last_seen=old_ts)
        brain.update_peer(stale_peer)

        coupler = CouplerBox("node1", brain, chain, read_meters=lambda: _make_meter())
        # Manually put into CONNECTED state
        coupler._state = CouplerState.CONNECTED
        coupler._contactor_closed = True

        coupler.tick()
        self.assertEqual(coupler.state, CouplerState.STANDALONE)
        self.assertFalse(coupler.contactor_closed)

    def test_tick_no_standalone_when_peer_recent(self):
        brain = GhostBrain("node1", 7000.0)
        chain = IntegrityChain("node1")
        fresh_peer = NodeState("node2", soc=70.0, last_seen=time.time())
        brain.update_peer(fresh_peer)
        coupler = CouplerBox("node1", brain, chain, read_meters=lambda: _make_meter())
        coupler._state = CouplerState.CONNECTED
        coupler._contactor_closed = True
        coupler.tick()
        self.assertEqual(coupler.state, CouplerState.CONNECTED)


# ---------------------------------------------------------------------------
# Fault reset
# ---------------------------------------------------------------------------

class TestFaultReset(unittest.TestCase):

    def test_reset_fault_returns_to_standalone(self):
        coupler, *_ = _make_coupler()
        coupler._fault("deliberate test fault")
        self.assertEqual(coupler.state, CouplerState.FAULTED)
        coupler.reset_fault()
        self.assertEqual(coupler.state, CouplerState.STANDALONE)
        self.assertEqual(coupler.fault_reason, "")

    def test_reset_fault_on_healthy_coupler_no_op(self):
        coupler, *_ = _make_coupler()
        coupler.reset_fault()   # should not raise
        self.assertEqual(coupler.state, CouplerState.STANDALONE)


# ---------------------------------------------------------------------------
# Energy accumulation and deed generation
# ---------------------------------------------------------------------------

class TestEnergyDeedGeneration(unittest.TestCase):

    def test_no_deed_when_no_energy_transferred(self):
        coupler, brain, chain, *_ = _make_coupler(soc=80.0)
        deed = coupler.close_transfer_deed("node2")
        self.assertIsNone(deed)

    def test_deed_generated_after_energy_accumulated(self):
        brain = GhostBrain("node1", 7000.0)
        chain = IntegrityChain("node1")
        peer = NodeState("node2", soc=70.0, last_seen=time.time())
        brain.update_peer(peer)

        t_base = 1000.0
        meter_vals = [
            _make_meter(dc_voltage=48.0, dc_current=20.0,
                        ac_voltage=120.0, ac_current=9.0, soc=80.0)
        ]
        meter_vals[0].timestamp = t_base

        def read_meters():
            return meter_vals[0]

        coupler = CouplerBox("node1", brain, chain, read_meters=read_meters)
        coupler.connect_to_bus()
        # Simulate two ticks 1 hour apart
        coupler._accumulate_energy(meter_vals[0], t_base)
        later_reading = _make_meter(dc_voltage=48.0, dc_current=20.0,
                                    ac_voltage=120.0, ac_current=9.0, soc=78.0)
        later_reading.timestamp = t_base + 3600.0
        coupler._accumulate_energy(later_reading, t_base + 3600.0)

        deed = coupler.close_transfer_deed("node2")
        self.assertIsNotNone(deed)
        self.assertGreater(deed.dc_kwh, 0)
        self.assertEqual(len(chain), 1)

    def test_accumulators_reset_after_deed(self):
        coupler, brain, chain, *_ = _make_coupler(soc=80.0)
        # Manually set accumulators
        coupler._dc_wh_acc = 500.0
        coupler._ac_wh_acc = 465.0
        coupler.close_transfer_deed("node2")
        self.assertEqual(coupler._dc_wh_acc, 0.0)
        self.assertEqual(coupler._ac_wh_acc, 0.0)


# ---------------------------------------------------------------------------
# Event log
# ---------------------------------------------------------------------------

class TestCouplerEventLog(unittest.TestCase):

    def test_connect_logs_event(self):
        coupler, brain, chain, *_ = _make_coupler(soc=80.0)
        peer = NodeState("node2", soc=70.0, last_seen=time.time())
        brain.update_peer(peer)
        coupler.connect_to_bus()
        events = [e["event"] for e in coupler.event_log]
        self.assertIn("connected", events)

    def test_fault_logs_event(self):
        coupler, *_ = _make_coupler()
        coupler._fault("test")
        events = [e["event"] for e in coupler.event_log]
        self.assertIn("faulted", events)

    def test_event_log_is_readonly_copy(self):
        coupler, *_ = _make_coupler()
        log = coupler.event_log
        log.append({"event": "injected"})
        self.assertEqual(len(coupler.event_log), 0)


# ---------------------------------------------------------------------------
# MeterReading computed properties
# ---------------------------------------------------------------------------

class TestMeterReading(unittest.TestCase):

    def test_dc_power(self):
        r = _make_meter(dc_voltage=48.0, dc_current=20.0)
        self.assertAlmostEqual(r.dc_power_w, 960.0)

    def test_ac_power(self):
        r = _make_meter(ac_voltage=120.0, ac_current=8.0)
        self.assertAlmostEqual(r.ac_power_w, 960.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
