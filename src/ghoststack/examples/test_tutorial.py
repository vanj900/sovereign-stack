"""
Tutorial Test Suite
====================
Automated tests for the full GhostStack tutorial stack and deed-ledger
scar/receipt lifecycle.

Tests cover:
  - Layer 1: MessageQueue, MeshDaemon, sync_deliver (offline → online delivery)
  - Layer 2: DIDService, GovernanceService (hash-chain anchoring / receipts),
             ReputationService, IncentiveService
  - Layer 3: BrainSimulation (LimbicSystem, FrontalLobe, state persistence)
  - Bridge : GhostAgent (combines all three layers)
  - Cell   : 3-node scenario (alice, bob, carol) from 06_three_node_cell.py
  - Deed-ledger: DeedLedger scar/receipt lifecycle (record, submit_recovery,
                 approve_recovery, verify_chain)

Run:
    python -m pytest test_tutorial.py -v
    # or without pytest:
    python test_tutorial.py
"""

import hashlib
import importlib.util
import json
import math
import os
import random
import sqlite3
import sys
import tempfile
import time
import unittest
import uuid


# ---------------------------------------------------------------------------
# Helpers: load modules under test inline so tests are self-contained
# ---------------------------------------------------------------------------

def _load_module(script_name: str):
    """Import an example script as a module without executing its main()."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, script_name)
    spec = importlib.util.spec_from_file_location(script_name[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ===========================================================================
# Layer 1 — offline-first messaging
# ===========================================================================

class TestLayer1Messaging(unittest.TestCase):
    """Tests from 01_layer1_messaging.py."""

    def setUp(self):
        self.mod = _load_module("01_layer1_messaging.py")
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db", prefix="test_layer1_")
        os.close(self.db_fd)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_enqueue_and_pending(self):
        q = self.mod.MessageQueue("alice", self.db_path)
        q.enqueue("bob", "hello")
        q.enqueue("bob", "world")
        pending = q.pending("bob")
        self.assertEqual(len(pending), 2)
        q.close()

    def test_sync_deliver_offline(self):
        """No messages delivered when daemon is offline."""
        q = self.mod.MessageQueue("alice", self.db_path)
        q.enqueue("bob", "msg1")
        daemon = self.mod.MeshDaemon("bob")
        inbox = self.mod.Inbox("bob")
        delivered = self.mod.sync_deliver(q, daemon, inbox)
        self.assertEqual(delivered, 0)
        self.assertEqual(len(inbox.messages), 0)
        q.close()

    def test_sync_deliver_online(self):
        """All pending messages delivered once daemon comes online."""
        q = self.mod.MessageQueue("alice", self.db_path)
        q.enqueue("bob", "msg1")
        q.enqueue("bob", "msg2")
        daemon = self.mod.MeshDaemon("bob")
        inbox = self.mod.Inbox("bob")
        daemon.bring_online()
        delivered = self.mod.sync_deliver(q, daemon, inbox)
        self.assertEqual(delivered, 2)
        self.assertEqual(len(inbox.messages), 2)
        q.close()

    def test_messages_marked_delivered(self):
        """After sync, pending() returns empty list."""
        q = self.mod.MessageQueue("alice", self.db_path)
        q.enqueue("bob", "hello")
        daemon = self.mod.MeshDaemon("bob")
        inbox = self.mod.Inbox("bob")
        daemon.bring_online()
        self.mod.sync_deliver(q, daemon, inbox)
        self.assertEqual(len(q.pending("bob")), 0)
        q.close()

    def test_offline_then_online_sequence(self):
        """Simulate the canonical offline → hold → online → deliver sequence."""
        q = self.mod.MessageQueue("alice", self.db_path)
        q.enqueue("bob", "Hello Bob, sync later!")
        q.enqueue("bob", "Offline message 2")
        daemon = self.mod.MeshDaemon("bob")
        inbox = self.mod.Inbox("bob")

        # Offline: nothing delivered
        self.assertEqual(self.mod.sync_deliver(q, daemon, inbox), 0)

        # Online: both messages delivered
        daemon.bring_online()
        count = self.mod.sync_deliver(q, daemon, inbox)
        self.assertEqual(count, 2)
        payloads = [m[2] for m in inbox.messages]
        self.assertIn("Hello Bob, sync later!", payloads)
        self.assertIn("Offline message 2", payloads)
        q.close()


# ===========================================================================
# Layer 2 — governance & trust
# ===========================================================================

class TestLayer2Governance(unittest.TestCase):
    """Tests from 02_layer2_governance.py."""

    def setUp(self):
        self.mod = _load_module("02_layer2_governance.py")

    # --- DIDService ---

    def test_create_did(self):
        svc = self.mod.DIDService()
        did = svc.create_did("alice")
        self.assertEqual(did, "did:sov:alice")

    def test_issue_and_verify_credential(self):
        svc = self.mod.DIDService()
        alice_did = svc.create_did("alice")
        bob_did = svc.create_did("bob")
        cred_id = svc.issue_credential(
            issuer_did=alice_did,
            subject_did=bob_did,
            credential_type="MeshMember",
            claims={"node_id": "bob", "role": "relay"},
        )
        self.assertTrue(svc.verify_credential(cred_id))

    def test_selective_disclosure(self):
        svc = self.mod.DIDService()
        alice_did = svc.create_did("alice")
        bob_did = svc.create_did("bob")
        cred_id = svc.issue_credential(
            issuer_did=alice_did,
            subject_did=bob_did,
            credential_type="MeshMember",
            claims={"node_id": "bob", "role": "relay", "cell": "cell-01"},
        )
        disclosed = svc.selective_disclosure(cred_id, ["node_id", "role"])
        self.assertIn("node_id", disclosed)
        self.assertIn("role", disclosed)
        self.assertNotIn("cell", disclosed)

    # --- GovernanceService ---

    def test_proposal_lifecycle(self):
        gov = self.mod.GovernanceService()
        svc = self.mod.DIDService()
        alice_did = svc.create_did("alice")
        bob_did = svc.create_did("bob")
        prop_id = gov.create_proposal(alice_did, "Test proposal")
        gov.vote(prop_id, alice_did, "APPROVE")
        gov.vote(prop_id, bob_did,   "APPROVE")
        result = gov.tally(prop_id)
        self.assertEqual(result, "PASSED")

    def test_proposal_fails_on_majority_reject(self):
        gov = self.mod.GovernanceService()
        svc = self.mod.DIDService()
        alice_did = svc.create_did("alice")
        bob_did = svc.create_did("bob")
        prop_id = gov.create_proposal(alice_did, "Failing proposal")
        gov.vote(prop_id, alice_did, "REJECT")
        gov.vote(prop_id, bob_did,   "REJECT")
        result = gov.tally(prop_id)
        self.assertEqual(result, "FAILED")

    def test_hash_chain_grows_with_each_tally(self):
        """Each tally appends exactly one block to the hash chain."""
        gov = self.mod.GovernanceService()
        svc = self.mod.DIDService()
        alice_did = svc.create_did("alice")

        for i in range(3):
            prop_id = gov.create_proposal(alice_did, f"Proposal {i}")
            gov.vote(prop_id, alice_did, "APPROVE")
            gov.tally(prop_id)

        self.assertEqual(len(gov._chain), 3)

    def test_hash_chain_integrity(self):
        """Each block's prev_hash equals the previous block's hash."""
        gov = self.mod.GovernanceService()
        svc = self.mod.DIDService()
        alice_did = svc.create_did("alice")
        bob_did = svc.create_did("bob")

        for desc in ["Alpha", "Beta", "Gamma"]:
            p = gov.create_proposal(alice_did, desc)
            gov.vote(p, alice_did, "APPROVE")
            gov.vote(p, bob_did,   "APPROVE")
            gov.tally(p)

        chain = gov._chain
        for i in range(1, len(chain)):
            self.assertEqual(
                chain[i]["prev_hash"],
                chain[i - 1]["hash"],
                msg=f"Chain broken at block {i}",
            )

    # --- ReputationService ---

    def test_reputation_two_nodes_symmetric(self):
        rep = self.mod.ReputationService()
        rep.add_endorsement("alice", "bob", weight=1.0)
        rep.add_endorsement("bob",   "alice", weight=1.0)
        scores = rep.compute_scores()
        # Symmetric endorsements → equal scores
        self.assertAlmostEqual(scores["alice"], scores["bob"], places=3)

    def test_reputation_asymmetric_weights(self):
        """Node with more in-weight should score higher."""
        rep = self.mod.ReputationService()
        rep.add_node("alice")
        rep.add_node("bob")
        rep.add_node("carol")
        # Alice and bob both endorse carol with high weight;
        # carol endorses both with low weight so in-flow concentrates at carol.
        rep.add_endorsement("alice", "carol", weight=2.0)
        rep.add_endorsement("bob",   "carol", weight=2.0)
        rep.add_endorsement("alice", "bob",   weight=0.5)
        rep.add_endorsement("bob",   "alice", weight=0.5)
        rep.add_endorsement("carol", "alice", weight=0.3)
        rep.add_endorsement("carol", "bob",   weight=0.3)
        scores = rep.compute_scores()
        self.assertGreater(scores["carol"], scores["alice"])
        self.assertGreater(scores["carol"], scores["bob"])

    def test_reputation_scores_sum_to_one(self):
        rep = self.mod.ReputationService()
        rep.add_endorsement("a", "b", weight=1.0)
        rep.add_endorsement("b", "c", weight=2.0)
        rep.add_endorsement("c", "a", weight=0.5)
        scores = rep.compute_scores()
        total = sum(scores.values())
        self.assertAlmostEqual(total, 1.0, places=3)

    # --- IncentiveService ---

    def test_incentive_register_and_reward(self):
        inc = self.mod.IncentiveService()
        inc.register("alice", initial_balance=100)
        inc.reward("alice", 10, "proposal creation")
        self.assertEqual(inc._balances["alice"], 110)

    def test_incentive_reward_unregistered_node(self):
        """Rewarding an unregistered node starts from 0."""
        inc = self.mod.IncentiveService()
        inc.reward("ghost", 5)
        self.assertEqual(inc._balances["ghost"], 5)


# ===========================================================================
# Layer 3 — brain simulation
# ===========================================================================

class TestLayer3Brain(unittest.TestCase):
    """Tests from 03_layer3_brain.py."""

    def setUp(self):
        self.mod = _load_module("03_layer3_brain.py")

    def test_limbic_update_clamps_to_unit_interval(self):
        limbic = self.mod.LimbicSystem()
        limbic.update({"intensity": 10.0, "novelty": 10.0})
        self.assertLessEqual(limbic.valence, 1.0)
        self.assertLessEqual(limbic.arousal, 1.0)
        self.assertGreaterEqual(limbic.valence, 0.0)
        self.assertGreaterEqual(limbic.arousal, 0.0)

    def test_dopamine_clamped(self):
        limbic = self.mod.LimbicSystem()
        # Extreme RPE should still clamp dopamine to [0, 1]
        dopamine = limbic.compute_dopamine(reward=100.0, predicted_reward=0.0)
        self.assertLessEqual(dopamine, 1.0)
        self.assertGreaterEqual(dopamine, 0.0)

    def test_frontal_lobe_returns_valid_action(self):
        frontal = self.mod.FrontalLobe()
        state = {"valence": 0.6, "arousal": 0.4, "dopamine": 0.7}
        action = frontal.decide(state)
        self.assertIn(action, ["explore", "wait", "signal", "conserve"])

    def test_brain_step_returns_complete_summary(self):
        brain = self.mod.BrainSimulation()
        result = brain.step("visual", 0.8, 0.9)
        for key in ("cycle", "stimulus", "emotion", "action", "dopamine"):
            self.assertIn(key, result)
        self.assertEqual(result["cycle"], 1)
        self.assertEqual(result["stimulus"], "visual")

    def test_brain_state_persistence(self):
        state_path = "/tmp/test_brain_persist.json"
        try:
            brain = self.mod.BrainSimulation()
            brain.STATE_PATH = state_path
            brain.step("visual", 0.8, 0.9)
            brain.step("auditory", 0.5, 0.4)
            brain.save_state(state_path)
            self.assertTrue(os.path.exists(state_path))

            brain2 = self.mod.BrainSimulation()
            loaded = brain2.load_state(state_path)
            self.assertTrue(loaded)
            self.assertEqual(brain2._cycle, 2)
        finally:
            if os.path.exists(state_path):
                os.remove(state_path)

    def test_hippocampus_stores_episodes(self):
        brain = self.mod.BrainSimulation()
        for stim, i, n in [("visual", 0.8, 0.9), ("auditory", 0.5, 0.4)]:
            brain.step(stim, i, n)
        self.assertEqual(len(brain.hippocampus.to_list()), 2)


# ===========================================================================
# Bridge — GhostAgent (single agent)
# ===========================================================================

class TestBridgeAgent(unittest.TestCase):
    """Tests from 04_bridge_agent.py."""

    def setUp(self):
        self.mod = _load_module("04_bridge_agent.py")
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db", prefix="test_bridge_")
        os.close(self.db_fd)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_agent_initialisation(self):
        did_svc = self.mod.DIDService()
        gov_svc = self.mod.GovernanceService()
        inc_svc = self.mod.IncentiveService()
        agent = self.mod.GhostAgent(
            agent_id="agent001",
            did_svc=did_svc,
            gov_svc=gov_svc,
            inc_svc=inc_svc,
            db_path=self.db_path,
        )
        self.assertEqual(agent.did, "did:sov:agent001")
        self.assertEqual(inc_svc._balances["agent001"], 100)

    def test_agent_brain_cycle_returns_valid_action(self):
        did_svc = self.mod.DIDService()
        gov_svc = self.mod.GovernanceService()
        inc_svc = self.mod.IncentiveService()
        agent = self.mod.GhostAgent(
            agent_id="agent001",
            did_svc=did_svc,
            gov_svc=gov_svc,
            inc_svc=inc_svc,
            db_path=self.db_path,
        )
        action = agent.run_brain_cycle("visual", intensity=0.8, novelty=0.9)
        self.assertIn(action, ["explore", "wait", "signal", "conserve"])

    def test_agent_propose_action_creates_passed_proposal(self):
        did_svc = self.mod.DIDService()
        gov_svc = self.mod.GovernanceService()
        inc_svc = self.mod.IncentiveService()
        agent = self.mod.GhostAgent(
            agent_id="agent001",
            did_svc=did_svc,
            gov_svc=gov_svc,
            inc_svc=inc_svc,
            db_path=self.db_path,
        )
        prop_id = agent.propose_action("explore")
        result = gov_svc.tally(prop_id)
        # Agent self-votes APPROVE, so it must PASS
        self.assertEqual(result, "PASSED")

    def test_agent_send_message_queues_message(self):
        did_svc = self.mod.DIDService()
        gov_svc = self.mod.GovernanceService()
        inc_svc = self.mod.IncentiveService()
        agent = self.mod.GhostAgent(
            agent_id="agent001",
            did_svc=did_svc,
            gov_svc=gov_svc,
            inc_svc=inc_svc,
            db_path=self.db_path,
        )
        agent.send_message("broadcast", "hello world")
        pending = agent.queue.pending("broadcast")
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0][3], "hello world")


# ===========================================================================
# Multi-agent (05) — two-agent scenario
# ===========================================================================

class TestMultiAgentDemo(unittest.TestCase):
    """Tests from 05_multi_agent_demo.py."""

    def setUp(self):
        self.mod = _load_module("05_multi_agent_demo.py")
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db", prefix="test_multi_")
        os.close(self.db_fd)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def _make_agents(self):
        did_svc = self.mod.DIDService()
        gov_svc = self.mod.GovernanceService()
        rep_svc = self.mod.ReputationService()
        inc_svc = self.mod.IncentiveService()
        alice = self.mod.GhostAgent(
            "alice", did_svc, gov_svc, rep_svc, inc_svc, self.db_path
        )
        bob = self.mod.GhostAgent(
            "bob", did_svc, gov_svc, rep_svc, inc_svc, self.db_path
        )
        return alice, bob, gov_svc, rep_svc, inc_svc

    def test_offline_hold_then_online_delivery(self):
        alice, bob, gov_svc, rep_svc, inc_svc = self._make_agents()
        alice.come_online()
        alice.queue.enqueue("bob", "hello bob")
        # Bob offline → 0 delivered
        delivered = self.mod.sync_deliver(alice.queue, bob.daemon, bob.inbox)
        self.assertEqual(delivered, 0)
        # Bob online → 1 delivered
        bob.come_online()
        delivered = self.mod.sync_deliver(alice.queue, bob.daemon, bob.inbox)
        self.assertEqual(delivered, 1)
        self.assertEqual(bob.inbox.messages[0][2], "hello bob")
        alice.close()
        bob.close()

    def test_joint_governance_both_approve(self):
        alice, bob, gov_svc, rep_svc, inc_svc = self._make_agents()
        prop_id = gov_svc.create_proposal(alice.did, "joint test")
        alice.vote(prop_id, "APPROVE")
        bob.vote(prop_id, "APPROVE")
        result = gov_svc.tally(prop_id)
        self.assertEqual(result, "PASSED")
        alice.close()
        bob.close()

    def test_reputation_mutual_endorsement(self):
        alice, bob, gov_svc, rep_svc, inc_svc = self._make_agents()
        rep_svc.add_endorsement("alice", "bob",   weight=1.0)
        rep_svc.add_endorsement("bob",   "alice", weight=0.5)
        scores = rep_svc.compute_scores()
        # Both scores should be positive and sum to ≈1
        self.assertGreater(scores.get("alice", 0), 0)
        self.assertGreater(scores.get("bob", 0), 0)
        self.assertAlmostEqual(sum(scores.values()), 1.0, places=3)
        alice.close()
        bob.close()


# ===========================================================================
# Three-node Cell (06) and Deed-ledger scar/receipt lifecycle
# ===========================================================================

class TestThreeNodeCell(unittest.TestCase):
    """Tests from 06_three_node_cell.py — 3-agent Cell + DeedLedger."""

    def setUp(self):
        self.mod = _load_module("06_three_node_cell.py")
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db", prefix="test_cell3_")
        os.close(self.db_fd)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def _make_cell(self):
        did_svc  = self.mod.DIDService()
        gov_svc  = self.mod.GovernanceService()
        rep_svc  = self.mod.ReputationService()
        inc_svc  = self.mod.IncentiveService()
        ledger   = self.mod.DeedLedger()
        alice = self.mod.GhostAgent(
            "alice", did_svc, gov_svc, rep_svc, inc_svc, ledger, self.db_path
        )
        bob = self.mod.GhostAgent(
            "bob", did_svc, gov_svc, rep_svc, inc_svc, ledger, self.db_path
        )
        carol = self.mod.GhostAgent(
            "carol", did_svc, gov_svc, rep_svc, inc_svc, ledger, self.db_path
        )
        return alice, bob, carol, gov_svc, rep_svc, inc_svc, ledger

    # --- 3-node messaging ---

    def test_three_node_offline_hold_then_sync(self):
        """Messages queued while nodes are offline are delivered once they go online."""
        alice, bob, carol, gov_svc, rep_svc, inc_svc, ledger = self._make_cell()
        alice.come_online()
        alice.queue.enqueue("bob",   "hi bob")
        alice.queue.enqueue("carol", "hi carol")

        self.assertEqual(self.mod.sync_deliver(alice.queue, bob.daemon,   bob.inbox),   0)
        self.assertEqual(self.mod.sync_deliver(alice.queue, carol.daemon, carol.inbox), 0)

        bob.come_online()
        self.assertEqual(self.mod.sync_deliver(alice.queue, bob.daemon, bob.inbox), 1)
        carol.come_online()
        self.assertEqual(self.mod.sync_deliver(alice.queue, carol.daemon, carol.inbox), 1)

        alice.close(); bob.close(); carol.close()

    # --- Governance with 3 voters ---

    def test_majority_vote_passes(self):
        """2/3 APPROVE → PASSED."""
        alice, bob, carol, gov_svc, rep_svc, inc_svc, ledger = self._make_cell()
        prop = gov_svc.create_proposal(alice.did, "majority test")
        alice.vote(prop, "APPROVE")
        bob.vote(prop,   "REJECT")
        carol.vote(prop, "APPROVE")
        self.assertEqual(gov_svc.tally(prop), "PASSED")
        alice.close(); bob.close(); carol.close()

    def test_minority_vote_fails(self):
        """1/3 APPROVE → FAILED."""
        alice, bob, carol, gov_svc, rep_svc, inc_svc, ledger = self._make_cell()
        prop = gov_svc.create_proposal(alice.did, "minority test")
        alice.vote(prop, "APPROVE")
        bob.vote(prop,   "REJECT")
        carol.vote(prop, "REJECT")
        self.assertEqual(gov_svc.tally(prop), "FAILED")
        alice.close(); bob.close(); carol.close()

    # --- DeedLedger: receipts ---

    def test_passed_proposal_creates_receipt(self):
        alice, bob, carol, gov_svc, rep_svc, inc_svc, ledger = self._make_cell()
        prop = gov_svc.create_proposal(alice.did, "receipt test")
        alice.vote(prop, "APPROVE"); bob.vote(prop, "APPROVE"); carol.vote(prop, "APPROVE")
        result = gov_svc.tally(prop)
        ledger.record(prop, result)
        self.assertEqual(len(ledger.receipts()), 1)
        self.assertEqual(len(ledger.scars()), 0)
        alice.close(); bob.close(); carol.close()

    def test_failed_proposal_creates_scar(self):
        alice, bob, carol, gov_svc, rep_svc, inc_svc, ledger = self._make_cell()
        prop = gov_svc.create_proposal(alice.did, "scar test")
        alice.vote(prop, "REJECT"); bob.vote(prop, "REJECT"); carol.vote(prop, "APPROVE")
        result = gov_svc.tally(prop)
        ledger.record(prop, result)
        self.assertEqual(len(ledger.scars()), 1)
        self.assertEqual(len(ledger.receipts()), 0)
        alice.close(); bob.close(); carol.close()

    def test_mixed_proposals_receipts_and_scars(self):
        """Two passed + one failed → 2 receipts, 1 scar."""
        alice, bob, carol, gov_svc, rep_svc, inc_svc, ledger = self._make_cell()

        p1 = gov_svc.create_proposal(alice.did, "pass 1")
        alice.vote(p1, "APPROVE"); bob.vote(p1, "APPROVE"); carol.vote(p1, "APPROVE")
        ledger.record(p1, gov_svc.tally(p1))

        p2 = gov_svc.create_proposal(carol.did, "pass 2")
        alice.vote(p2, "APPROVE"); bob.vote(p2, "REJECT"); carol.vote(p2, "APPROVE")
        ledger.record(p2, gov_svc.tally(p2))

        p3 = gov_svc.create_proposal(bob.did, "fail")
        alice.vote(p3, "REJECT"); bob.vote(p3, "APPROVE"); carol.vote(p3, "REJECT")
        ledger.record(p3, gov_svc.tally(p3))

        self.assertEqual(len(ledger.receipts()), 2)
        self.assertEqual(len(ledger.scars()), 1)
        alice.close(); bob.close(); carol.close()

    # --- DeedLedger: scar recovery lifecycle ---

    def test_scar_recovery_submit_and_approve(self):
        """Submit a recovery for a scarred proposal; approving it marks it approved."""
        alice, bob, carol, gov_svc, rep_svc, inc_svc, ledger = self._make_cell()
        prop = gov_svc.create_proposal(bob.did, "controversial proposal")
        alice.vote(prop, "REJECT"); bob.vote(prop, "APPROVE"); carol.vote(prop, "REJECT")
        result = gov_svc.tally(prop)
        ledger.record(prop, result)

        recovery_id = ledger.submit_recovery(
            prop,
            note="Revised after feedback",
            recoverer_did=bob.did,
        )
        self.assertEqual(ledger._recoveries[recovery_id]["status"], "pending")

        ledger.approve_recovery(recovery_id, reviewer_did=alice.did)
        self.assertEqual(ledger._recoveries[recovery_id]["status"], "approved")
        alice.close(); bob.close(); carol.close()

    def test_recovery_on_nonexistent_scar_raises(self):
        alice, bob, carol, gov_svc, rep_svc, inc_svc, ledger = self._make_cell()
        with self.assertRaises(ValueError):
            ledger.submit_recovery("P-999", note="no scar here", recoverer_did=alice.did)
        alice.close(); bob.close(); carol.close()

    def test_approve_unknown_recovery_raises(self):
        alice, bob, carol, gov_svc, rep_svc, inc_svc, ledger = self._make_cell()
        with self.assertRaises(KeyError):
            ledger.approve_recovery("no-such-id", reviewer_did=alice.did)
        alice.close(); bob.close(); carol.close()

    # --- DeedLedger: hash-chain integrity ---

    def test_chain_integrity_after_multiple_records(self):
        alice, bob, carol, gov_svc, rep_svc, inc_svc, ledger = self._make_cell()
        for desc in ["A", "B", "C", "D"]:
            p = gov_svc.create_proposal(alice.did, desc)
            alice.vote(p, "APPROVE"); bob.vote(p, "APPROVE"); carol.vote(p, "APPROVE")
            ledger.record(p, gov_svc.tally(p))
        self.assertTrue(ledger.verify_chain())
        alice.close(); bob.close(); carol.close()

    def test_tampered_chain_fails_verification(self):
        alice, bob, carol, gov_svc, rep_svc, inc_svc, ledger = self._make_cell()
        # Create two blocks so the linkage can be checked
        p1 = gov_svc.create_proposal(alice.did, "first")
        alice.vote(p1, "APPROVE"); bob.vote(p1, "APPROVE"); carol.vote(p1, "APPROVE")
        ledger.record(p1, gov_svc.tally(p1))
        p2 = gov_svc.create_proposal(alice.did, "second")
        alice.vote(p2, "APPROVE"); bob.vote(p2, "APPROVE"); carol.vote(p2, "APPROVE")
        ledger.record(p2, gov_svc.tally(p2))
        # Tamper with the prev_hash of block 1, breaking the linkage to block 0
        ledger._chain[1]["prev_hash"] = "badhash"
        self.assertFalse(ledger.verify_chain())
        alice.close(); bob.close(); carol.close()

    # --- Reputation with 3 nodes ---

    def test_three_node_reputation_carol_wins(self):
        """Carol receives more endorsement weight → highest score."""
        alice, bob, carol, gov_svc, rep_svc, inc_svc, ledger = self._make_cell()
        rep_svc.add_endorsement("alice", "carol", weight=2.0)
        rep_svc.add_endorsement("bob",   "carol", weight=2.0)
        rep_svc.add_endorsement("alice", "bob",   weight=0.5)
        rep_svc.add_endorsement("bob",   "alice", weight=0.5)
        rep_svc.add_endorsement("carol", "alice", weight=0.3)
        rep_svc.add_endorsement("carol", "bob",   weight=0.3)
        scores = rep_svc.compute_scores()
        self.assertGreater(scores["carol"], scores["alice"])
        self.assertGreater(scores["carol"], scores["bob"])
        alice.close(); bob.close(); carol.close()


# ===========================================================================
# Cell / Unit / Federation Hierarchy (07)
# ===========================================================================

class TestCellUnitHierarchy(unittest.TestCase):
    """Tests from 07_cell_unit_hierarchy.py — Node, Cell, Unit, FederationAlliance."""

    def setUp(self):
        self.mod = _load_module("07_cell_unit_hierarchy.py")

    # -----------------------------------------------------------------------
    # SovereignNode
    # -----------------------------------------------------------------------

    def test_node_creates_master_did(self):
        node = self.mod.SovereignNode("alice", "human")
        self.assertEqual(node.master_did, "did:sov:alice")

    def test_node_types_accepted(self):
        for ntype in ("human", "sov_hab", "ghost_brain"):
            n = self.mod.SovereignNode(f"n_{ntype}", ntype)
            self.assertEqual(n.node_type, ntype)

    def test_node_invalid_type_raises(self):
        with self.assertRaises(ValueError):
            self.mod.SovereignNode("x", "robot")

    def test_context_did_is_deterministic(self):
        node = self.mod.SovereignNode("alice", "human")
        cdid1 = node.derive_context_did("cell-A")
        cdid2 = node.derive_context_did("cell-A")
        self.assertEqual(cdid1, cdid2)

    def test_context_dids_differ_across_cells(self):
        node = self.mod.SovereignNode("alice", "human")
        cdid_a = node.derive_context_did("cell-A")
        cdid_b = node.derive_context_did("cell-B")
        self.assertNotEqual(cdid_a, cdid_b)

    def test_phc_assignment(self):
        node = self.mod.SovereignNode("alice", "human")
        node.set_phc("PHC-1")
        self.assertEqual(node.phc_id, "PHC-1")

    def test_duplicate_phc_raises(self):
        node = self.mod.SovereignNode("alice", "human")
        node.set_phc("PHC-1")
        with self.assertRaises(ValueError):
            node.set_phc("PHC-2")

    def test_fc_join_up_to_three(self):
        node = self.mod.SovereignNode("alice", "human")
        node.join_fc("FC-1")
        node.join_fc("FC-2")
        node.join_fc("FC-3")
        self.assertEqual(node.fc_ids, ["FC-1", "FC-2", "FC-3"])

    def test_fourth_fc_raises(self):
        node = self.mod.SovereignNode("alice", "human")
        node.join_fc("FC-1")
        node.join_fc("FC-2")
        node.join_fc("FC-3")
        with self.assertRaises(ValueError):
            node.join_fc("FC-4")

    def test_duplicate_fc_is_idempotent(self):
        node = self.mod.SovereignNode("alice", "human")
        node.join_fc("FC-1")
        node.join_fc("FC-1")   # should not raise or double-count
        self.assertEqual(node.fc_ids, ["FC-1"])

    # -----------------------------------------------------------------------
    # Cell
    # -----------------------------------------------------------------------

    def test_cell_creation_phc(self):
        cell = self.mod.Cell("PHC-test", "primary_home_cell")
        self.assertEqual(cell.cell_id, "PHC-test")
        self.assertEqual(cell.cell_type, "primary_home_cell")

    def test_cell_creation_fc(self):
        cell = self.mod.Cell("FC-test", "functional_cell")
        self.assertEqual(cell.cell_type, "functional_cell")

    def test_cell_invalid_type_raises(self):
        with self.assertRaises(ValueError):
            self.mod.Cell("bad", "super_cell")

    def test_cell_not_quorate_below_min(self):
        cell = self.mod.Cell("PHC-q", "primary_home_cell")
        cell.add_node(self.mod.SovereignNode("a", "human"))
        cell.add_node(self.mod.SovereignNode("b", "human"))
        self.assertFalse(cell.is_quorate())

    def test_cell_quorate_at_min(self):
        cell = self.mod.Cell("PHC-q", "primary_home_cell")
        for name in ("a", "b", "c"):
            cell.add_node(self.mod.SovereignNode(name, "human"))
        self.assertTrue(cell.is_quorate())

    def test_phc_add_node_sets_phc_on_node(self):
        cell = self.mod.Cell("PHC-1", "primary_home_cell")
        node = self.mod.SovereignNode("alice", "human")
        cell.add_node(node)
        self.assertEqual(node.phc_id, "PHC-1")

    def test_fc_add_node_sets_fc_on_node(self):
        cell = self.mod.Cell("FC-1", "functional_cell")
        node = self.mod.SovereignNode("alice", "human")
        cell.add_node(node)
        self.assertIn("FC-1", node.fc_ids)

    def test_duplicate_node_raises(self):
        cell = self.mod.Cell("PHC-1", "primary_home_cell")
        node = self.mod.SovereignNode("alice", "human")
        cell.add_node(node)
        with self.assertRaises(ValueError):
            cell.add_node(node)

    def test_cell_cap_at_seven(self):
        cell = self.mod.Cell("PHC-cap", "primary_home_cell")
        for i in range(self.mod.CELL_MAX):
            cell.add_node(self.mod.SovereignNode(f"n{i}", "human"))
        overflow = self.mod.SovereignNode("overflow", "human")
        with self.assertRaises(ValueError):
            cell.add_node(overflow)

    def test_cell_fork_requires_over_max(self):
        cell = self.mod.Cell("PHC-nofork", "primary_home_cell")
        for i in range(3):
            cell.add_node(self.mod.SovereignNode(f"x{i}", "human"))
        with self.assertRaises(ValueError):
            cell.fork()

    def test_cell_fork_splits_nodes(self):
        cell = self.mod.Cell("PHC-fork", "primary_home_cell")
        # Inject 8 nodes directly to simulate over-limit state
        for i in range(8):
            n = self.mod.SovereignNode(f"fn{i}", "human")
            n._phc_id = cell.cell_id
            cell._nodes.append(n)
        left, right = cell.fork()
        self.assertEqual(left.size + right.size, 8)
        self.assertEqual(left.forked_from, "PHC-fork")
        self.assertEqual(right.forked_from, "PHC-fork")

    def test_cell_fork_child_ids_correct(self):
        cell = self.mod.Cell("PHC-x", "primary_home_cell")
        for i in range(8):
            n = self.mod.SovereignNode(f"gn{i}", "human")
            n._phc_id = cell.cell_id
            cell._nodes.append(n)
        left, right = cell.fork()
        self.assertEqual(left.cell_id, "PHC-x-fork-0")
        self.assertEqual(right.cell_id, "PHC-x-fork-1")

    def test_cell_treasury_contribution(self):
        cell = self.mod.Cell("PHC-t", "primary_home_cell")
        cell.contribute(50, "alice")
        cell.contribute(30, "bob")
        self.assertEqual(cell.treasury, 80)

    def test_cell_vote_majority_passes(self):
        cell = self.mod.Cell("PHC-v", "primary_home_cell")
        nodes = [self.mod.SovereignNode(n, "human") for n in ("a", "b", "c")]
        for node in nodes:
            cell.add_node(node)
        result = cell.vote("test proposal", {"a": "APPROVE", "b": "APPROVE", "c": "REJECT"})
        self.assertEqual(result, "PASSED")

    def test_cell_vote_majority_fails(self):
        cell = self.mod.Cell("PHC-v2", "primary_home_cell")
        nodes = [self.mod.SovereignNode(n, "human") for n in ("a", "b", "c")]
        for node in nodes:
            cell.add_node(node)
        result = cell.vote("test proposal", {"a": "REJECT", "b": "REJECT", "c": "APPROVE"})
        self.assertEqual(result, "FAILED")

    def test_cell_vote_non_member_raises(self):
        cell = self.mod.Cell("PHC-v3", "primary_home_cell")
        for n in ("a", "b", "c"):
            cell.add_node(self.mod.SovereignNode(n, "human"))
        with self.assertRaises(ValueError):
            cell.vote("test", {"a": "APPROVE", "outsider": "APPROVE", "b": "REJECT"})

    # -----------------------------------------------------------------------
    # BridgeContract
    # -----------------------------------------------------------------------

    def test_bridge_contract_requires_two_cells(self):
        with self.assertRaises(ValueError):
            self.mod.BridgeContract("BC-bad", ["only-one"], "desc", "terms")

    def test_bridge_contract_not_expired_immediately(self):
        bc = self.mod.BridgeContract("BC-1", ["c1", "c2"], "desc", "terms",
                                     duration_seconds=86400)
        self.assertFalse(bc.is_expired())

    def test_bridge_contract_status_active_on_create(self):
        bc = self.mod.BridgeContract("BC-2", ["c1", "c2"], "desc", "terms")
        self.assertEqual(bc.status, "active")

    def test_bridge_contract_expire(self):
        bc = self.mod.BridgeContract("BC-3", ["c1", "c2"], "desc", "terms")
        bc.expire()
        self.assertEqual(bc.status, "expired")

    def test_bridge_contract_complete(self):
        bc = self.mod.BridgeContract("BC-4", ["c1", "c2"], "desc", "terms")
        bc.complete()
        self.assertEqual(bc.status, "completed")

    # -----------------------------------------------------------------------
    # Unit
    # -----------------------------------------------------------------------

    def _make_quorate_unit(self, unit_id: str = "U-test") -> tuple:
        """Return a Unit with 3 minimal cells already added."""
        unit = self.mod.Unit(unit_id)
        cells = []
        for i in range(3):
            c = self.mod.Cell(f"C-{unit_id}-{i}", "functional_cell")
            c.add_node(self.mod.SovereignNode(f"un{unit_id}{i}", "human"))
            unit.add_cell(c)
            cells.append(c)
        return unit, cells

    def test_unit_creation(self):
        unit = self.mod.Unit("U-1")
        self.assertEqual(unit.unit_id, "U-1")
        self.assertEqual(unit.size, 0)

    def test_unit_add_cell(self):
        unit, cells = self._make_quorate_unit()
        self.assertEqual(unit.size, 3)

    def test_unit_quorate_at_min(self):
        unit, _ = self._make_quorate_unit()
        self.assertTrue(unit.is_quorate())

    def test_unit_not_quorate_below_min(self):
        unit = self.mod.Unit("U-nq")
        c = self.mod.Cell("C-nq", "functional_cell")
        c.add_node(self.mod.SovereignNode("n0", "human"))
        unit.add_cell(c)
        self.assertFalse(unit.is_quorate())

    def test_unit_node_count(self):
        unit = self.mod.Unit("U-nc")
        for i in range(3):
            c = self.mod.Cell(f"C-nc-{i}", "functional_cell")
            for j in range(3):
                c.add_node(self.mod.SovereignNode(f"nc{i}{j}", "human"))
            unit.add_cell(c)
        self.assertEqual(unit.node_count(), 9)

    def test_unit_cap_at_seven(self):
        unit = self.mod.Unit("U-cap")
        for i in range(self.mod.UNIT_MAX):
            c = self.mod.Cell(f"C-cap-{i}", "functional_cell")
            c.add_node(self.mod.SovereignNode(f"uc{i}", "human"))
            unit.add_cell(c)
        overflow = self.mod.Cell("C-overflow", "functional_cell")
        overflow.add_node(self.mod.SovereignNode("uo", "human"))
        with self.assertRaises(ValueError):
            unit.add_cell(overflow)

    def test_unit_duplicate_cell_raises(self):
        unit = self.mod.Unit("U-dup")
        c = self.mod.Cell("C-dup", "functional_cell")
        c.add_node(self.mod.SovereignNode("n0", "human"))
        unit.add_cell(c)
        with self.assertRaises(ValueError):
            unit.add_cell(c)

    def test_unit_bridge_contract_registered(self):
        unit, cells = self._make_quorate_unit("U-bc")
        bc = self.mod.BridgeContract(
            "BC-test", [cells[0].cell_id, cells[1].cell_id], "desc", "terms"
        )
        unit.add_bridge_contract(bc)
        self.assertIn(bc, unit.bridge_contracts)

    def test_unit_bridge_contract_non_member_raises(self):
        unit, _ = self._make_quorate_unit("U-bcr")
        bc = self.mod.BridgeContract("BC-bad", ["stranger-1", "stranger-2"], "d", "t")
        with self.assertRaises(ValueError):
            unit.add_bridge_contract(bc)

    def test_unit_fork_requires_over_max(self):
        unit, _ = self._make_quorate_unit("U-nf")
        with self.assertRaises(ValueError):
            unit.fork()

    def test_unit_fork_splits_cells(self):
        unit = self.mod.Unit("U-f")
        # Inject 8 cells directly to simulate over-limit state
        for i in range(8):
            c = self.mod.Cell(f"CF-{i}", "functional_cell")
            unit._cells.append(c)
        left, right = unit.fork()
        self.assertEqual(left.size + right.size, 8)
        self.assertEqual(left.forked_from, "U-f")
        self.assertEqual(right.forked_from, "U-f")

    def test_unit_fork_child_ids_correct(self):
        unit = self.mod.Unit("U-fi")
        for i in range(8):
            unit._cells.append(self.mod.Cell(f"CFI-{i}", "functional_cell"))
        left, right = unit.fork()
        self.assertEqual(left.unit_id, "U-fi-fork-0")
        self.assertEqual(right.unit_id, "U-fi-fork-1")

    # -----------------------------------------------------------------------
    # FederationAlliance
    # -----------------------------------------------------------------------

    def _make_unit(self, uid: str) -> object:
        return self.mod.Unit(uid)

    def test_federation_creation(self):
        u1, u2 = self._make_unit("F-U1"), self._make_unit("F-U2")
        fed = self.mod.FederationAlliance("FED-1", "federation", [u1, u2],
                                          "test purpose", 2592000)
        self.assertEqual(fed.fa_id, "FED-1")
        self.assertEqual(fed.fa_type, "federation")
        self.assertTrue(fed.is_opt_in)

    def test_alliance_creation(self):
        u = self._make_unit("A-U1")
        alliance = self.mod.FederationAlliance("ALL-1", "alliance", [u],
                                               "crisis mesh", 604800)
        self.assertEqual(alliance.fa_type, "alliance")

    def test_federation_invalid_type_raises(self):
        u = self._make_unit("X-U1")
        with self.assertRaises(ValueError):
            self.mod.FederationAlliance("BAD", "commune", [u], "p", 1000)

    def test_federation_empty_units_raises(self):
        with self.assertRaises(ValueError):
            self.mod.FederationAlliance("BAD", "federation", [], "p", 1000)

    def test_federation_not_expired_immediately(self):
        u = self._make_unit("NE-U1")
        fed = self.mod.FederationAlliance("FED-NE", "federation", [u], "p", 86400)
        self.assertFalse(fed.is_expired())

    def test_federation_is_opt_in_invariant(self):
        u = self._make_unit("OI-U1")
        fed = self.mod.FederationAlliance("FED-OI", "federation", [u], "p", 1000)
        self.assertIs(fed.is_opt_in, True)

    def test_federation_add_unit_opt_in(self):
        u1 = self._make_unit("FA-U1")
        u2 = self._make_unit("FA-U2")
        fed = self.mod.FederationAlliance("FED-FA", "federation", [u1], "p", 1000)
        fed.add_unit(u2)
        self.assertEqual(len(fed.units), 2)

    def test_federation_add_duplicate_unit_is_idempotent(self):
        u1 = self._make_unit("FD-U1")
        fed = self.mod.FederationAlliance("FED-FD", "federation", [u1], "p", 1000)
        fed.add_unit(u1)   # adding the same unit again should be a no-op
        self.assertEqual(len(fed.units), 1)


# ===========================================================================
# Run all tests
# ===========================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
