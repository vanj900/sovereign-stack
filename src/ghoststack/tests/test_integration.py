"""
Integration tests for the Sovereign Stack Governance Engine.

Tests the full multi-agent governance workflow end-to-end, including:
- REST API via httpx TestClient
- Multi-agent consensus scenarios
- Persistence (state survives service restarts)
- Edge cases (quorum failures, invalid inputs, etc.)

Run with:
    pytest src/ghoststack/tests/test_integration.py -v
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from ghoststack.governance.api.rest_api import app, register_services
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
    return StorageService("sqlite:///:memory:")


@pytest.fixture()
def services(storage):
    did = DIDService(storage)
    gov = GovernanceService(storage, quorum=0.5)
    rep = ReputationService(storage, decay_half_life_days=None)
    inc = IncentiveService(storage)
    register_services(did, gov, rep, inc)
    return did, gov, rep, inc


@pytest.fixture()
def client(services):
    return TestClient(app)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# Full multi-agent governance workflow
# ---------------------------------------------------------------------------

class TestMultiAgentGovernanceWorkflow:
    """
    Simulate a small cell (Alice, Bob, Carol) running a full governance cycle.
    """

    def test_full_workflow(self, client):
        # 1. Create DIDs for all agents
        alice = client.post("/did", json={"owner": "alice"}).json()["did"]
        bob = client.post("/did", json={"owner": "bob"}).json()["did"]
        carol = client.post("/did", json={"owner": "carol"}).json()["did"]
        assert alice == "did:sov:alice"
        assert bob == "did:sov:bob"
        assert carol == "did:sov:carol"

        # 2. Alice issues a credential to Bob
        cred_resp = client.post(
            "/did/credential",
            json={
                "issuer_did": alice,
                "subject_did": bob,
                "credential_type": "MeshMember",
                "claims": {"node_id": "bob", "role": "relay", "cell": "cell-01"},
            },
        )
        assert cred_resp.status_code == 200
        cred_id = cred_resp.json()["id"]

        # 3. Verify the credential
        verify_resp = client.get(f"/did/credential/{cred_id}/verify")
        assert verify_resp.status_code == 200
        assert verify_resp.json()["valid"] is True

        # 4. Selective disclosure
        disclose_resp = client.post(
            f"/did/credential/{cred_id}/disclose",
            json={"fields": ["node_id", "role"]},
        )
        assert disclose_resp.status_code == 200
        disclosed = disclose_resp.json()["disclosed"]
        assert "node_id" in disclosed
        assert "role" in disclosed
        assert "cell" not in disclosed

        # 5. Create a governance proposal
        prop_resp = client.post(
            "/governance/proposals",
            json={"proposer_did": alice, "description": "Increase cell bandwidth quota"},
        )
        assert prop_resp.status_code == 200
        prop_id = prop_resp.json()["id"]
        assert prop_resp.json()["status"] == "open"

        # 6. All agents vote
        for did_str, choice in [(alice, "APPROVE"), (bob, "APPROVE"), (carol, "REJECT")]:
            vote_resp = client.post(
                f"/governance/proposals/{prop_id}/vote",
                json={"voter_did": did_str, "choice": choice},
            )
            assert vote_resp.status_code == 200

        # 7. Tally the votes
        tally_resp = client.post(
            f"/governance/proposals/{prop_id}/tally", json={}
        )
        assert tally_resp.status_code == 200
        tally = tally_resp.json()
        assert tally["result"] == "PASSED"
        assert tally["approve"] == 2
        assert tally["reject"] == 1

        # 8. Verify proposal is now closed
        get_resp = client.get(f"/governance/proposals/{prop_id}")
        assert get_resp.json()["status"] == "PASSED"

        # 9. Audit chain should have one block
        chain_resp = client.get("/chain")
        assert chain_resp.status_code == 200
        chain = chain_resp.json()
        assert len(chain) >= 1
        # Chain integrity: each block's prev_hash matches the previous block's hash
        for i in range(1, len(chain)):
            assert chain[i]["prev_hash"] == chain[i - 1]["block_hash"]

        # 10. Add reputation endorsements
        client.post("/reputation/endorse", json={"source": "alice", "target": "bob", "weight": 1.0})
        client.post("/reputation/endorse", json={"source": "bob", "target": "alice", "weight": 0.5})
        scores_resp = client.post("/reputation/compute")
        assert scores_resp.status_code == 200
        scores = scores_resp.json()["scores"]
        assert "alice" in scores
        assert "bob" in scores
        # Scores sum to ~1
        assert abs(sum(scores.values()) - 1.0) < 0.01

        # 11. Register incentive accounts and reward participation
        for node in ["alice", "bob", "carol"]:
            client.post("/incentive/register", json={"node_id": node, "initial_balance": 100})
        client.post("/incentive/reward", json={"node_id": "alice", "amount": 10, "reason": "proposal"})
        client.post("/incentive/reward", json={"node_id": "bob", "amount": 5, "reason": "voting"})

        balances_resp = client.get("/incentive/balances")
        assert balances_resp.status_code == 200
        balances = balances_resp.json()["balances"]
        assert balances["alice"] == 110
        assert balances["bob"] == 105
        assert balances["carol"] == 100


# ---------------------------------------------------------------------------
# API error handling tests
# ---------------------------------------------------------------------------

class TestAPIErrorHandling:
    def test_create_proposal_empty_description(self, client):
        resp = client.post(
            "/governance/proposals",
            json={"proposer_did": "did:sov:alice", "description": ""},
        )
        assert resp.status_code == 422  # Pydantic validation error

    def test_vote_on_nonexistent_proposal(self, client):
        resp = client.post(
            "/governance/proposals/P-999/vote",
            json={"voter_did": "did:sov:alice", "choice": "APPROVE"},
        )
        assert resp.status_code == 400

    def test_vote_invalid_choice(self, client):
        # Create proposal first
        client.post("/did", json={"owner": "alice"})
        client.post(
            "/governance/proposals",
            json={"proposer_did": "did:sov:alice", "description": "Test"},
        )
        resp = client.post(
            "/governance/proposals/P-1/vote",
            json={"voter_did": "did:sov:alice", "choice": "MAYBE"},
        )
        assert resp.status_code == 422  # Pydantic validation

    def test_tally_nonexistent_proposal(self, client):
        resp = client.post(
            "/governance/proposals/P-999/tally", json={}
        )
        assert resp.status_code == 400

    def test_verify_nonexistent_credential(self, client):
        resp = client.get("/did/credential/nonexistent/verify")
        assert resp.status_code == 200
        assert resp.json()["valid"] is False

    def test_issue_credential_bad_issuer(self, client):
        client.post("/did", json={"owner": "bob"})
        resp = client.post(
            "/did/credential",
            json={
                "issuer_did": "did:sov:nobody",
                "subject_did": "did:sov:bob",
                "credential_type": "T",
                "claims": {},
            },
        )
        assert resp.status_code == 400

    def test_get_proposal_not_found(self, client):
        resp = client.get("/governance/proposals/P-999")
        assert resp.status_code == 404

    def test_list_proposals_empty(self, client):
        resp = client.get("/governance/proposals")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_individual_balance(self, client):
        client.post("/incentive/register", json={"node_id": "alice", "initial_balance": 50})
        resp = client.get("/incentive/balances/alice")
        assert resp.status_code == 200
        assert resp.json()["balance"] == 50

    def test_get_scores_before_compute(self, client):
        resp = client.get("/reputation/scores")
        assert resp.status_code == 200
        assert resp.json()["scores"] == {}


# ---------------------------------------------------------------------------
# Quorum enforcement integration test
# ---------------------------------------------------------------------------

class TestQuorumEnforcement:
    def test_no_quorum_result(self, storage):
        gov = GovernanceService(storage, quorum=0.66)
        prop_id = gov.create_proposal("did:sov:alice", "High quorum proposal")
        gov.vote(prop_id, "did:sov:alice", "APPROVE")
        # 1 of 4 voters → 25% < 66% quorum
        result = gov.tally(prop_id, total_voters=4)
        assert result == "NO_QUORUM"

    def test_quorum_exactly_met(self, storage):
        gov = GovernanceService(storage, quorum=0.5)
        prop_id = gov.create_proposal("did:sov:alice", "Test")
        gov.vote(prop_id, "did:sov:alice", "APPROVE")
        gov.vote(prop_id, "did:sov:bob", "APPROVE")
        # 2 of 4 voters → 50% = 50% quorum (met)
        result = gov.tally(prop_id, total_voters=4)
        assert result == "PASSED"


# ---------------------------------------------------------------------------
# Persistence integration test
# ---------------------------------------------------------------------------

class TestPersistence:
    def test_state_survives_service_restart(self, storage):
        """Services should restore state from the database on creation."""
        # Session 1: create data
        did1 = DIDService(storage)
        did1.create_did("alice")
        did1.create_did("bob")
        gov1 = GovernanceService(storage)
        prop_id = gov1.create_proposal("did:sov:alice", "Persistent proposal")
        gov1.vote(prop_id, "did:sov:alice", "APPROVE")
        gov1.vote(prop_id, "did:sov:bob", "APPROVE")
        gov1.tally(prop_id)

        inc1 = IncentiveService(storage)
        inc1.register("alice", 100)
        inc1.reward("alice", 25)

        # Session 2: new instances from same storage
        did2 = DIDService(storage)
        assert did2.get_did("alice") == "did:sov:alice"

        gov2 = GovernanceService(storage)
        prop = gov2.get_proposal(prop_id)
        assert prop is not None
        assert prop["status"] == "PASSED"

        inc2 = IncentiveService(storage)
        assert inc2.get_balance("alice") == 125

    def test_chain_persists_across_restarts(self, storage):
        gov1 = GovernanceService(storage)
        p = gov1.create_proposal("did:sov:alice", "Test")
        gov1.vote(p, "did:sov:alice", "APPROVE")
        gov1.tally(p)

        gov2 = GovernanceService(storage)
        chain = gov2.get_chain()
        assert len(chain) == 1


# ---------------------------------------------------------------------------
# Demo smoke test
# ---------------------------------------------------------------------------

class TestDemo:
    def test_demo_runs_without_error(self):
        """Run the demo function and verify it completes without exceptions."""
        from ghoststack.governance.main import run_demo
        run_demo()  # Should not raise
