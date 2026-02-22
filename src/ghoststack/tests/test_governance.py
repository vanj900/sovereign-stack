"""
Unit tests for the Sovereign Stack Governance Engine.

Run with:
    pytest src/ghoststack/tests/test_governance.py -v
"""

from __future__ import annotations

import pytest

from ghoststack.governance.core.did_service import DIDService
from ghoststack.governance.core.governance_service import GovernanceService
from ghoststack.governance.core.incentive_service import IncentiveService
from ghoststack.governance.core.reputation_service import ReputationService
from ghoststack.governance.core.storage_service import StorageService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def storage():
    """In-memory SQLite storage (fresh per test)."""
    return StorageService("sqlite:///:memory:")


@pytest.fixture()
def did_svc(storage):
    return DIDService(storage)


@pytest.fixture()
def gov_svc(storage):
    return GovernanceService(storage, quorum=0.5)


@pytest.fixture()
def rep_svc(storage):
    return ReputationService(storage, decay_half_life_days=None)


@pytest.fixture()
def inc_svc(storage):
    return IncentiveService(storage)


# ---------------------------------------------------------------------------
# StorageService tests
# ---------------------------------------------------------------------------

class TestStorageService:
    def test_save_and_get_did(self, storage):
        storage.save_did("did:sov:alice", "alice")
        row = storage.get_did("did:sov:alice")
        assert row is not None
        assert row["owner"] == "alice"

    def test_get_missing_did_returns_none(self, storage):
        assert storage.get_did("did:sov:nobody") is None

    def test_save_and_get_credential(self, storage):
        cred = {
            "id": "cred-1",
            "type": "MeshMember",
            "issuer": "did:sov:alice",
            "subject": "did:sov:bob",
            "claims": {"role": "relay"},
            "signature": "abc123",
        }
        storage.save_credential(cred)
        row = storage.get_credential("cred-1")
        assert row is not None
        assert row["claims"] == {"role": "relay"}
        assert row["signature"] == "abc123"

    def test_save_and_list_proposals(self, storage):
        proposal = {
            "id": "P-1",
            "proposer": "did:sov:alice",
            "description": "Test",
            "status": "open",
        }
        storage.save_proposal(proposal)
        proposals = storage.list_proposals()
        assert len(proposals) == 1
        assert proposals[0]["id"] == "P-1"

    def test_save_and_get_votes(self, storage):
        storage.save_vote("P-1", "did:sov:alice", "APPROVE")
        storage.save_vote("P-1", "did:sov:bob", "REJECT")
        votes = storage.get_votes("P-1")
        assert len(votes) == 2

    def test_vote_upsert(self, storage):
        """Voting twice should replace the first vote."""
        storage.save_vote("P-1", "did:sov:alice", "APPROVE")
        storage.save_vote("P-1", "did:sov:alice", "REJECT")
        votes = storage.get_votes("P-1")
        assert len(votes) == 1
        assert votes[0]["choice"] == "REJECT"

    def test_chain_blocks(self, storage):
        storage.append_block("0" * 16, '{"test": 1}', "hash1")
        storage.append_block("hash1", '{"test": 2}', "hash2")
        chain = storage.get_chain()
        assert len(chain) == 2
        assert chain[-1]["block_hash"] == "hash2"

    def test_get_last_block_hash_empty(self, storage):
        assert storage.get_last_block_hash() == "0" * 16

    def test_balance_operations(self, storage):
        storage.save_balance("alice", 100)
        assert storage.get_balance("alice") == 100
        storage.save_balance("alice", 150)
        assert storage.get_balance("alice") == 150

    def test_get_all_balances(self, storage):
        storage.save_balance("alice", 100)
        storage.save_balance("bob", 200)
        balances = storage.get_all_balances()
        assert balances == {"alice": 100, "bob": 200}

    def test_reputation_scores(self, storage):
        storage.save_reputation_score("alice", 0.7)
        storage.save_reputation_score("bob", 0.3)
        scores = storage.get_reputation_scores()
        assert scores == {"alice": 0.7, "bob": 0.3}


# ---------------------------------------------------------------------------
# DIDService tests
# ---------------------------------------------------------------------------

class TestDIDService:
    def test_create_did(self, did_svc):
        did = did_svc.create_did("alice")
        assert did == "did:sov:alice"

    def test_create_did_persisted(self, storage):
        did_svc = DIDService(storage)
        did_svc.create_did("alice")
        # New instance should load from storage
        did_svc2 = DIDService(storage)
        assert did_svc2.get_did("alice") == "did:sov:alice"

    def test_get_did_missing(self, did_svc):
        assert did_svc.get_did("nobody") is None

    def test_issue_credential(self, did_svc):
        did_svc.create_did("alice")
        did_svc.create_did("bob")
        cred_id = did_svc.issue_credential(
            "did:sov:alice",
            "did:sov:bob",
            "MeshMember",
            {"role": "relay"},
        )
        assert cred_id is not None

    def test_issue_credential_bad_issuer(self, did_svc):
        with pytest.raises(ValueError, match="Issuer DID not registered"):
            did_svc.issue_credential(
                "did:sov:nobody", "did:sov:bob", "Type", {}
            )

    def test_issue_credential_bad_subject(self, did_svc):
        did_svc.create_did("alice")
        with pytest.raises(ValueError, match="Subject DID not registered"):
            did_svc.issue_credential(
                "did:sov:alice", "did:sov:nobody", "Type", {}
            )

    def test_verify_credential_valid(self, did_svc):
        did_svc.create_did("alice")
        did_svc.create_did("bob")
        cred_id = did_svc.issue_credential(
            "did:sov:alice", "did:sov:bob", "MeshMember", {"role": "relay"}
        )
        assert did_svc.verify_credential(cred_id) is True

    def test_verify_credential_not_found(self, did_svc):
        assert did_svc.verify_credential("nonexistent") is False

    def test_selective_disclosure(self, did_svc):
        did_svc.create_did("alice")
        did_svc.create_did("bob")
        cred_id = did_svc.issue_credential(
            "did:sov:alice",
            "did:sov:bob",
            "MeshMember",
            {"node_id": "bob", "role": "relay", "cell": "cell-01"},
        )
        disclosed = did_svc.selective_disclosure(cred_id, ["node_id", "role"])
        assert "node_id" in disclosed
        assert "role" in disclosed
        assert "cell" not in disclosed

    def test_selective_disclosure_missing_fields(self, did_svc):
        did_svc.create_did("alice")
        did_svc.create_did("bob")
        cred_id = did_svc.issue_credential(
            "did:sov:alice", "did:sov:bob", "T", {"x": 1}
        )
        disclosed = did_svc.selective_disclosure(cred_id, ["x", "missing"])
        assert "x" in disclosed
        assert "missing" not in disclosed


# ---------------------------------------------------------------------------
# GovernanceService tests
# ---------------------------------------------------------------------------

class TestGovernanceService:
    def test_create_proposal(self, gov_svc):
        prop_id = gov_svc.create_proposal("did:sov:alice", "Test proposal")
        assert prop_id == "P-1"

    def test_proposal_sequential_ids(self, gov_svc):
        p1 = gov_svc.create_proposal("did:sov:alice", "Proposal 1")
        p2 = gov_svc.create_proposal("did:sov:alice", "Proposal 2")
        assert p1 == "P-1"
        assert p2 == "P-2"

    def test_vote_approve(self, gov_svc):
        prop_id = gov_svc.create_proposal("did:sov:alice", "Test")
        gov_svc.vote(prop_id, "did:sov:alice", "APPROVE")
        votes = gov_svc.get_votes(prop_id)
        assert votes["did:sov:alice"] == "APPROVE"

    def test_vote_invalid_choice(self, gov_svc):
        prop_id = gov_svc.create_proposal("did:sov:alice", "Test")
        with pytest.raises(ValueError, match="Invalid choice"):
            gov_svc.vote(prop_id, "did:sov:alice", "MAYBE")

    def test_vote_unknown_proposal(self, gov_svc):
        with pytest.raises(KeyError):
            gov_svc.vote("P-999", "did:sov:alice", "APPROVE")

    def test_vote_closed_proposal(self, gov_svc):
        prop_id = gov_svc.create_proposal("did:sov:alice", "Test")
        gov_svc.vote(prop_id, "did:sov:alice", "APPROVE")
        gov_svc.tally(prop_id)
        with pytest.raises(RuntimeError, match="already closed"):
            gov_svc.vote(prop_id, "did:sov:bob", "REJECT")

    def test_tally_passed(self, gov_svc):
        prop_id = gov_svc.create_proposal("did:sov:alice", "Test")
        gov_svc.vote(prop_id, "did:sov:alice", "APPROVE")
        gov_svc.vote(prop_id, "did:sov:bob", "APPROVE")
        gov_svc.vote(prop_id, "did:sov:carol", "REJECT")
        result = gov_svc.tally(prop_id)
        assert result == "PASSED"

    def test_tally_failed(self, gov_svc):
        prop_id = gov_svc.create_proposal("did:sov:alice", "Test")
        gov_svc.vote(prop_id, "did:sov:alice", "REJECT")
        gov_svc.vote(prop_id, "did:sov:bob", "REJECT")
        result = gov_svc.tally(prop_id)
        assert result == "FAILED"

    def test_tally_no_quorum(self):
        storage = StorageService("sqlite:///:memory:")
        gov_svc = GovernanceService(storage, quorum=0.6)
        prop_id = gov_svc.create_proposal("did:sov:alice", "Test")
        gov_svc.vote(prop_id, "did:sov:alice", "APPROVE")
        # Only 1 of 5 eligible voters voted → below 0.6 quorum
        result = gov_svc.tally(prop_id, total_voters=5)
        assert result == "NO_QUORUM"

    def test_tally_anchors_chain(self, storage, gov_svc):
        prop_id = gov_svc.create_proposal("did:sov:alice", "Test")
        gov_svc.vote(prop_id, "did:sov:alice", "APPROVE")
        gov_svc.tally(prop_id)
        chain = storage.get_chain()
        assert len(chain) == 1
        assert chain[0]["prev_hash"] == "0" * 16

    def test_chain_links(self, storage, gov_svc):
        for i in range(3):
            p = gov_svc.create_proposal("did:sov:alice", f"Proposal {i}")
            gov_svc.vote(p, "did:sov:alice", "APPROVE")
            gov_svc.tally(p)
        chain = storage.get_chain()
        assert len(chain) == 3
        for i in range(1, 3):
            assert chain[i]["prev_hash"] == chain[i - 1]["block_hash"]

    def test_list_proposals(self, gov_svc):
        gov_svc.create_proposal("did:sov:alice", "A")
        gov_svc.create_proposal("did:sov:bob", "B")
        assert len(gov_svc.list_proposals()) == 2

    def test_get_proposal_not_found(self, gov_svc):
        assert gov_svc.get_proposal("P-999") is None

    def test_abstain_vote(self, gov_svc):
        prop_id = gov_svc.create_proposal("did:sov:alice", "Test")
        gov_svc.vote(prop_id, "did:sov:alice", "ABSTAIN")
        # ABSTAIN doesn't affect APPROVE/REJECT balance
        result = gov_svc.tally(prop_id)
        assert result == "FAILED"  # 0 approve, 0 reject → failed


# ---------------------------------------------------------------------------
# ReputationService tests
# ---------------------------------------------------------------------------

class TestReputationService:
    def test_compute_scores_empty(self, rep_svc):
        assert rep_svc.compute_scores() == {}

    def test_compute_scores_single_node(self, rep_svc):
        rep_svc.add_node("alice")
        scores = rep_svc.compute_scores()
        assert "alice" in scores
        assert abs(scores["alice"] - 1.0) < 1e-6

    def test_compute_scores_two_nodes(self, rep_svc):
        rep_svc.add_endorsement("alice", "bob", weight=1.0)
        scores = rep_svc.compute_scores()
        # Both nodes present
        assert "alice" in scores
        assert "bob" in scores
        # Scores sum to ~1
        assert abs(sum(scores.values()) - 1.0) < 1e-4

    def test_node_with_more_endorsements_scores_higher(self, rep_svc):
        rep_svc.add_endorsement("alice", "bob", weight=3.0)
        rep_svc.add_endorsement("carol", "bob", weight=2.0)
        rep_svc.add_endorsement("alice", "carol", weight=1.0)
        scores = rep_svc.compute_scores()
        # bob gets more endorsements than carol
        assert scores.get("bob", 0) > scores.get("carol", 0)

    def test_scores_persisted(self, storage):
        rep = ReputationService(storage, decay_half_life_days=None)
        rep.add_endorsement("alice", "bob")
        rep.compute_scores()
        scores = storage.get_reputation_scores()
        assert "alice" in scores
        assert "bob" in scores

    def test_get_scores_without_compute(self, rep_svc):
        # Before any computation, should return empty
        assert rep_svc.get_scores() == {}

    def test_add_node_explicit(self, rep_svc):
        rep_svc.add_node("alice")
        rep_svc.add_node("bob")
        scores = rep_svc.compute_scores()
        assert "alice" in scores
        assert "bob" in scores


# ---------------------------------------------------------------------------
# IncentiveService tests
# ---------------------------------------------------------------------------

class TestIncentiveService:
    def test_register(self, inc_svc):
        inc_svc.register("alice", 100)
        assert inc_svc.get_balance("alice") == 100

    def test_register_idempotent(self, inc_svc):
        inc_svc.register("alice", 100)
        inc_svc.register("alice", 999)  # Should not overwrite
        assert inc_svc.get_balance("alice") == 100

    def test_reward_positive(self, inc_svc):
        inc_svc.register("alice", 100)
        new_bal = inc_svc.reward("alice", 50)
        assert new_bal == 150

    def test_reward_negative(self, inc_svc):
        inc_svc.register("alice", 100)
        new_bal = inc_svc.reward("alice", -20)
        assert new_bal == 80

    def test_reward_unregistered_node(self, inc_svc):
        """Rewarding an unregistered node starts from 0."""
        new_bal = inc_svc.reward("newbie", 10)
        assert new_bal == 10

    def test_get_balance_unregistered(self, inc_svc):
        assert inc_svc.get_balance("nobody") == 0

    def test_get_all_balances(self, inc_svc):
        inc_svc.register("alice", 100)
        inc_svc.register("bob", 200)
        balances = inc_svc.get_all_balances()
        assert balances == {"alice": 100, "bob": 200}

    def test_distribute_reward_even(self, inc_svc):
        inc_svc.register("alice", 0)
        inc_svc.register("bob", 0)
        awarded = inc_svc.distribute_reward(["alice", "bob"], 100)
        assert awarded["alice"] + awarded["bob"] == 100

    def test_distribute_reward_weighted(self, inc_svc):
        inc_svc.register("alice", 0)
        inc_svc.register("bob", 0)
        awarded = inc_svc.distribute_reward(
            ["alice", "bob"], 100, weights=[3.0, 1.0]
        )
        assert awarded["alice"] == 75
        assert awarded["bob"] == 25

    def test_distribute_reward_empty(self, inc_svc):
        assert inc_svc.distribute_reward([], 100) == {}

    def test_distribute_reward_weight_mismatch(self, inc_svc):
        with pytest.raises(ValueError, match="weights length"):
            inc_svc.distribute_reward(["alice", "bob"], 100, weights=[1.0])

    def test_persistence(self, storage):
        svc = IncentiveService(storage)
        svc.register("alice", 100)
        svc.reward("alice", 50)
        # Load fresh instance
        svc2 = IncentiveService(storage)
        assert svc2.get_balance("alice") == 150
