"""
Tests for energy.ghostbrain — demand forecasting + grid-former election.
"""
import sys
import os
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from energy.ghostbrain import (
    GhostBrain,
    NodeState,
    ForecastResult,
    DEFAULT_SOC_FLOOR,
    SOC_FLOOR_FORECAST_THRESHOLD,
    MAX_RAMP_RATE_W_PER_MIN,
    SHADOW_NET_TIMEOUT_S,
    ELECTION_INTERVAL_S,
)


class TestGhostBrainForecast(unittest.TestCase):

    def setUp(self):
        self.brain = GhostBrain(
            node_id="node1",
            battery_capacity_wh=7000.0,
            soc_floor=DEFAULT_SOC_FLOOR,
        )

    def test_forecast_no_samples_zero_demand(self):
        """With no samples, forecast should show zero demand."""
        fc = self.brain.forecast(current_soc=80.0)
        self.assertEqual(fc.predicted_demand_w, 0.0)
        self.assertIsInstance(fc, ForecastResult)

    def test_forecast_locks_at_soc_floor(self):
        """Export must be locked when SoC is at or below the floor."""
        self.brain.record_demand(100.0)
        fc = self.brain.forecast(current_soc=DEFAULT_SOC_FLOOR)
        self.assertTrue(fc.export_locked)

    def test_forecast_locks_below_soc_floor(self):
        """Export must be locked when SoC is below the floor."""
        self.brain.record_demand(100.0)
        fc = self.brain.forecast(current_soc=DEFAULT_SOC_FLOOR - 1.0)
        self.assertTrue(fc.export_locked)

    def test_forecast_unlocked_above_floor(self):
        """Export unlocked when SoC well above floor and 6h forecast safe."""
        # Record modest demand so 6h forecast stays above threshold
        for _ in range(5):
            self.brain.record_demand(200.0)
        fc = self.brain.forecast(current_soc=90.0)
        self.assertFalse(fc.export_locked)

    def test_forecast_locked_by_6h_projection(self):
        """High demand should cause 6h SoC forecast to drop below threshold."""
        # Very high demand: 7000 W on a 7000 Wh battery → SoC hits 0 in 1 h
        for _ in range(10):
            self.brain.record_demand(7000.0)
        fc = self.brain.forecast(current_soc=30.0)
        self.assertTrue(fc.export_locked)
        self.assertLess(fc.predicted_soc_at_6h, SOC_FLOOR_FORECAST_THRESHOLD)

    def test_forecast_horizon_is_12h(self):
        self.brain.record_demand(500.0)
        fc = self.brain.forecast(current_soc=80.0)
        self.assertEqual(fc.horizon_h, 12.0)

    def test_forecast_reason_is_string(self):
        self.brain.record_demand(300.0)
        fc = self.brain.forecast(current_soc=50.0)
        self.assertIsInstance(fc.reason, str)
        self.assertGreater(len(fc.reason), 0)

    def test_ewa_converges_toward_latest_demand(self):
        """EWA should be influenced by recent demand."""
        # Feed in high values, then low values; EWA should decrease
        for _ in range(20):
            self.brain.record_demand(2000.0)
        high_fc = self.brain.forecast(current_soc=80.0)
        brain2 = GhostBrain("node2", 7000.0)
        for _ in range(20):
            brain2.record_demand(2000.0)
        for _ in range(5):
            brain2.record_demand(100.0)
        low_fc = brain2.forecast(current_soc=80.0)
        self.assertGreater(high_fc.predicted_demand_w, low_fc.predicted_demand_w)

    def test_predicted_soc_at_6h_cannot_go_below_zero(self):
        """SoC prediction should clamp at 0, not go negative."""
        for _ in range(10):
            self.brain.record_demand(50000.0)
        fc = self.brain.forecast(current_soc=10.0)
        self.assertGreaterEqual(fc.predicted_soc_at_6h, 0.0)


class TestGhostBrainRampRate(unittest.TestCase):

    def setUp(self):
        self.brain = GhostBrain("node1", 7000.0)

    def test_full_ramp_in_one_minute(self):
        """Maximum ramp in 60 s must equal MAX_RAMP_RATE_W_PER_MIN."""
        new_setpoint = self.brain.clamp_export_setpoint(
            requested_w=2000.0, elapsed_s=60.0
        )
        self.assertAlmostEqual(new_setpoint, MAX_RAMP_RATE_W_PER_MIN)

    def test_ramp_scales_with_time(self):
        """30 s elapsed → max ramp is half of 60 s ramp."""
        sp30 = self.brain.clamp_export_setpoint(1000.0, elapsed_s=30.0)
        brain2 = GhostBrain("node2", 7000.0)
        sp60 = brain2.clamp_export_setpoint(1000.0, elapsed_s=60.0)
        self.assertAlmostEqual(sp30, sp60 / 2.0, places=1)

    def test_negative_ramp_limit(self):
        """Ramp down should also be limited."""
        # Ramp up over several intervals to reach a higher setpoint
        for _ in range(5):
            self.brain.clamp_export_setpoint(2000.0, elapsed_s=60.0)
        previous = self.brain._last_export_setpoint_w  # 5 × 300 = 1500
        # Now ramp down to 0 — should be limited to -300 W per minute
        new_sp = self.brain.clamp_export_setpoint(0.0, elapsed_s=60.0)
        self.assertAlmostEqual(new_sp, previous - MAX_RAMP_RATE_W_PER_MIN, places=1)

    def test_small_change_not_clamped(self):
        """A small change within ramp budget passes through unchanged."""
        sp = self.brain.clamp_export_setpoint(50.0, elapsed_s=60.0)
        self.assertAlmostEqual(sp, 50.0)

    def test_consecutive_ramps_accumulate(self):
        """Two consecutive 60-s ramps should advance setpoint by 2× ramp rate."""
        self.brain.clamp_export_setpoint(2000.0, elapsed_s=60.0)
        sp2 = self.brain.clamp_export_setpoint(2000.0, elapsed_s=60.0)
        self.assertAlmostEqual(sp2, 2 * MAX_RAMP_RATE_W_PER_MIN)


class TestGhostBrainElection(unittest.TestCase):

    def _make_node(self, node_id, soc, uptime_s, receipts, last_seen_offset=0):
        return NodeState(
            node_id=node_id,
            soc=soc,
            last_seen=time.time() - last_seen_offset,
            uptime_s=uptime_s,
            receipt_count=receipts,
        )

    def test_highest_soc_wins_simple(self):
        brain = GhostBrain("ctrl", 7000.0)
        alice = self._make_node("alice", soc=85.0, uptime_s=3600, receipts=5)
        bob   = self._make_node("bob",   soc=60.0, uptime_s=3600, receipts=5)
        winner = brain.elect_grid_former([alice, bob])
        self.assertEqual(winner, "alice")

    def test_receipts_break_soc_tie(self):
        brain = GhostBrain("ctrl", 7000.0)
        alice = self._make_node("alice", soc=80.0, uptime_s=3600, receipts=50)
        bob   = self._make_node("bob",   soc=80.0, uptime_s=3600, receipts=0)
        winner = brain.elect_grid_former([alice, bob])
        self.assertEqual(winner, "alice")

    def test_stale_node_excluded(self):
        """A node that has been silent > SHADOW_NET_TIMEOUT_S must be excluded."""
        brain = GhostBrain("ctrl", 7000.0)
        alice = self._make_node("alice", soc=90.0, uptime_s=3600, receipts=10,
                                last_seen_offset=0)
        bob   = self._make_node("bob",   soc=80.0, uptime_s=3600, receipts=5,
                                last_seen_offset=int(SHADOW_NET_TIMEOUT_S) + 10)
        winner = brain.elect_grid_former([alice, bob])
        self.assertEqual(winner, "alice")

    def test_no_candidates_returns_none(self):
        brain = GhostBrain("ctrl", 7000.0)
        winner = brain.elect_grid_former([])
        self.assertIsNone(winner)

    def test_all_stale_returns_none(self):
        brain = GhostBrain("ctrl", 7000.0)
        stale = self._make_node("alice", soc=90.0, uptime_s=3600, receipts=10,
                                last_seen_offset=int(SHADOW_NET_TIMEOUT_S) + 60)
        winner = brain.elect_grid_former([stale])
        self.assertIsNone(winner)

    def test_election_updates_property(self):
        brain = GhostBrain("ctrl", 7000.0)
        node = self._make_node("alice", soc=75.0, uptime_s=1800, receipts=3)
        brain.elect_grid_former([node])
        self.assertEqual(brain.elected_grid_former, "alice")


class TestGhostBrainShadowNetTimeout(unittest.TestCase):

    def test_silent_when_all_peers_stale(self):
        brain = GhostBrain("node1", 7000.0)
        old_ts = time.time() - SHADOW_NET_TIMEOUT_S - 10
        peer = NodeState("node2", soc=70.0, last_seen=old_ts)
        brain.update_peer(peer)
        self.assertTrue(brain.shadow_net_silent())

    def test_not_silent_when_peer_recent(self):
        brain = GhostBrain("node1", 7000.0)
        peer = NodeState("node2", soc=70.0, last_seen=time.time())
        brain.update_peer(peer)
        self.assertFalse(brain.shadow_net_silent())

    def test_not_silent_when_no_peers_known(self):
        """Fresh boot: no peers → not silent (avoid spurious standalone trips)."""
        brain = GhostBrain("node1", 7000.0)
        self.assertFalse(brain.shadow_net_silent())

    def test_reachable_peers_filters_stale(self):
        brain = GhostBrain("node1", 7000.0)
        fresh = NodeState("fresh", soc=60.0, last_seen=time.time())
        stale = NodeState("stale", soc=80.0, last_seen=time.time() - SHADOW_NET_TIMEOUT_S - 5)
        brain.update_peer(fresh)
        brain.update_peer(stale)
        reachable = brain.reachable_peers()
        ids = [p.node_id for p in reachable]
        self.assertIn("fresh", ids)
        self.assertNotIn("stale", ids)


class TestGhostBrainShadowPacket(unittest.TestCase):

    def test_build_shadow_packet_fields(self):
        brain = GhostBrain("node1", 7000.0)
        brain.record_demand(500.0)
        packet = brain.build_shadow_packet(current_soc=72.0)
        for key in ("node_id", "soc", "forecast_12h_w", "export_locked", "ts"):
            self.assertIn(key, packet)
        self.assertEqual(packet["node_id"], "node1")
        self.assertAlmostEqual(packet["soc"], 72.0, places=1)

    def test_shadow_packet_export_locked_when_low_soc(self):
        brain = GhostBrain("node1", 7000.0)
        brain.record_demand(500.0)
        packet = brain.build_shadow_packet(current_soc=10.0)
        self.assertTrue(packet["export_locked"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
