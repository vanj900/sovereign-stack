"""
Tests for energy.integrity_chain — EnergyDeed + IntegrityChain.
"""
import sys
import os
import json
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from energy.integrity_chain import EnergyDeed, IntegrityChain, ChainBlock


class TestEnergyDeedCreation(unittest.TestCase):

    def test_create_computes_loss_percent(self):
        deed = EnergyDeed.create("node1", "node2", dc_kwh=1.23, ac_kwh=1.14)
        expected_loss = round((1.23 - 1.14) / 1.23 * 100, 2)
        self.assertAlmostEqual(deed.loss_percent, expected_loss, places=2)

    def test_create_zero_dc_kwh_no_div_by_zero(self):
        deed = EnergyDeed.create("node1", "node2", dc_kwh=0.0, ac_kwh=0.0)
        self.assertEqual(deed.loss_percent, 0.0)

    def test_timestamp_is_iso8601_utc(self):
        deed = EnergyDeed.create("node1", "node2", dc_kwh=1.0, ac_kwh=0.9)
        self.assertTrue(deed.timestamp.endswith("Z"))
        self.assertIn("T", deed.timestamp)

    def test_timestamp_uses_provided_value(self):
        ts = 1740924120.0  # 2025-03-02T14:22:00Z
        deed = EnergyDeed.create("node1", "node2", dc_kwh=1.0, ac_kwh=0.9,
                                 timestamp=ts)
        self.assertIn("2025", deed.timestamp)

    def test_to_dict_matches_spec_format(self):
        deed = EnergyDeed.create("node1", "node2", dc_kwh=1.23, ac_kwh=1.14)
        d = deed.to_dict()
        self.assertEqual(d["type"], "energy_transfer")
        self.assertEqual(d["from"], "node1")
        self.assertEqual(d["to"], "node2")
        self.assertIn("dc_kwh", d)
        self.assertIn("ac_kwh", d)
        self.assertIn("loss_percent", d)
        self.assertIn("timestamp", d)
        self.assertIn("signature", d)

    def test_to_json_is_valid_json(self):
        deed = EnergyDeed.create("node1", "node2", dc_kwh=0.5, ac_kwh=0.47)
        json_str = deed.to_json()
        parsed = json.loads(json_str)
        self.assertEqual(parsed["type"], "energy_transfer")

    def test_dc_kwh_rounded_to_4_places(self):
        deed = EnergyDeed.create("node1", "node2", dc_kwh=1.234567, ac_kwh=1.1234)
        self.assertEqual(deed.dc_kwh, round(1.234567, 4))


class TestIntegrityChainRecord(unittest.TestCase):

    def setUp(self):
        self.chain = IntegrityChain(node_id="node1")

    def _make_deed(self, from_n="node1", to_n="node2", dc=1.0, ac=0.9):
        return EnergyDeed.create(from_n, to_n, dc_kwh=dc, ac_kwh=ac)

    def test_chain_starts_empty(self):
        self.assertEqual(len(self.chain), 0)

    def test_record_appends_block(self):
        deed = self._make_deed()
        self.chain.record(deed)
        self.assertEqual(len(self.chain), 1)

    def test_deed_id_set_after_record(self):
        deed = self._make_deed()
        self.chain.record(deed)
        self.assertNotEqual(deed.deed_id, "")
        self.assertEqual(len(deed.deed_id), 16)  # 16-char hex

    def test_signature_set_after_record(self):
        deed = self._make_deed()
        self.chain.record(deed)
        self.assertNotEqual(deed.signature, "")

    def test_multiple_records(self):
        for i in range(5):
            deed = self._make_deed(dc=float(i + 1) * 0.5, ac=float(i + 1) * 0.45)
            self.chain.record(deed)
        self.assertEqual(len(self.chain), 5)

    def test_deeds_returns_all_recorded(self):
        for _ in range(3):
            self.chain.record(self._make_deed())
        self.assertEqual(len(self.chain.deeds()), 3)

    def test_latest_block_is_last_appended(self):
        deed1 = self._make_deed(dc=1.0, ac=0.9)
        deed2 = self._make_deed(dc=2.0, ac=1.8)
        self.chain.record(deed1)
        self.chain.record(deed2)
        latest = self.chain.latest_block()
        self.assertIsNotNone(latest)
        self.assertEqual(latest.deed.dc_kwh, 2.0)

    def test_latest_block_none_when_empty(self):
        self.assertIsNone(self.chain.latest_block())


class TestIntegrityChainVerification(unittest.TestCase):

    def setUp(self):
        self.chain = IntegrityChain(node_id="node1")

    def _make_deed(self):
        return EnergyDeed.create("node1", "node2", dc_kwh=1.0, ac_kwh=0.93)

    def test_empty_chain_verifies(self):
        self.assertTrue(self.chain.verify())

    def test_single_block_verifies(self):
        self.chain.record(self._make_deed())
        self.assertTrue(self.chain.verify())

    def test_multi_block_chain_verifies(self):
        for _ in range(5):
            self.chain.record(self._make_deed())
        self.assertTrue(self.chain.verify())

    def test_tampered_hash_fails_verification(self):
        self.chain.record(self._make_deed())
        self.chain.record(self._make_deed())
        # Tamper with block 0's stored hash
        self.chain._chain[0].hash = "badhash"
        self.assertFalse(self.chain.verify())

    def test_tampered_prev_hash_fails_verification(self):
        self.chain.record(self._make_deed())
        self.chain.record(self._make_deed())
        # Break the linkage from block 1 to block 0
        self.chain._chain[1].prev_hash = "deadbeef"
        self.assertFalse(self.chain.verify())

    def test_genesis_prev_hash_is_zeros(self):
        self.chain.record(self._make_deed())
        self.assertEqual(self.chain._chain[0].prev_hash, "0" * 64)

    def test_chain_links_correctly(self):
        for _ in range(4):
            self.chain.record(self._make_deed())
        blocks = self.chain._chain
        for i in range(1, len(blocks)):
            self.assertEqual(
                blocks[i].prev_hash,
                blocks[i - 1].hash,
                f"Link broken at block {i}",
            )


class TestIntegrityChainExport(unittest.TestCase):

    def test_export_json_is_valid(self):
        chain = IntegrityChain("node1")
        for _ in range(3):
            chain.record(EnergyDeed.create("node1", "node2", 1.0, 0.9))
        exported = chain.export_json()
        data = json.loads(exported)
        self.assertEqual(len(data), 3)
        for block in data:
            self.assertIn("index", block)
            self.assertIn("prev_hash", block)
            self.assertIn("hash", block)
            self.assertIn("deed", block)

    def test_export_deed_has_spec_fields(self):
        chain = IntegrityChain("node1")
        chain.record(EnergyDeed.create("node1", "node2", 1.23, 1.14))
        data = json.loads(chain.export_json())
        deed_dict = data[0]["deed"]
        self.assertEqual(deed_dict["type"], "energy_transfer")
        self.assertIn("from", deed_dict)
        self.assertIn("to", deed_dict)


class TestIntegrityChainDifferentKeys(unittest.TestCase):

    def test_different_keys_produce_different_signatures(self):
        chain_a = IntegrityChain("node1", private_key="secret_a")
        chain_b = IntegrityChain("node1", private_key="secret_b")
        ts = time.time()
        deed_a = EnergyDeed.create("node1", "node2", 1.0, 0.9, timestamp=ts)
        deed_b = EnergyDeed.create("node1", "node2", 1.0, 0.9, timestamp=ts)
        chain_a.record(deed_a)
        chain_b.record(deed_b)
        self.assertNotEqual(deed_a.signature, deed_b.signature)


if __name__ == "__main__":
    unittest.main(verbosity=2)
