"""
Layer 2: Governance & Trust
============================
Demonstrates decentralised identity, credential exchange, proposal/voting, and
reputation/incentive computation — all without an external network connection.

Components:
  - DIDService        : create DIDs, issue verifiable credentials, verify them
  - GovernanceService : create proposals, cast votes, tally, anchor to a hash chain
  - ReputationService : build a trust graph, compute PageRank-like scores
  - IncentiveService  : track balances and distribute rewards

Run:
    python 02_layer2_governance.py

Expected output (illustrative):
    [DID] created alice  → did:sov:alice
    [DID] created bob    → did:sov:bob
    [credential] alice  issued 'MeshMember' to bob
    [verify] credential for bob  valid=True
    [selective] disclosed fields: ['node_id', 'role']
    [governance] proposal P-1 created by alice  : "Increase cell bandwidth quota"
    [vote] alice  → APPROVE on P-1
    [vote] bob    → APPROVE on P-1
    [tally] P-1: approve=2 reject=0 → PASSED
    [chain] block 0: 0000000000000000 → <hash>
    [chain] block 1: <prev>          → <hash>
    [reputation] scores: alice=0.65 bob=0.35
    [incentive] alice balance: 110  bob balance: 105
"""

import hashlib
import json
import time
import uuid


# ---------------------------------------------------------------------------
# DIDService
# ---------------------------------------------------------------------------

class DIDService:
    """
    Minimal decentralised-identity service.

    In production this would use ed25519 key pairs and W3C DID documents.
    Here we represent DIDs as plain dicts so the example stays dependency-free.
    """

    def __init__(self):
        # did_id → {did, owner, created_at}
        self._registry: dict = {}
        # credential_id → credential dict
        self._credentials: dict = {}

    def create_did(self, owner: str) -> str:
        """Create a new DID for *owner* and register it."""
        did = f"did:sov:{owner}"
        self._registry[did] = {
            "did": did,
            "owner": owner,
            "created_at": int(time.time()),
        }
        print(f"[DID] created {owner:<6} → {did}")
        return did

    def issue_credential(
        self,
        issuer_did: str,
        subject_did: str,
        credential_type: str,
        claims: dict,
    ) -> str:
        """
        Issue a verifiable credential from *issuer_did* to *subject_did*.

        Returns a credential id that the subject can present later.
        """
        cred_id = str(uuid.uuid4())[:8]
        credential = {
            "id": cred_id,
            "type": credential_type,
            "issuer": issuer_did,
            "subject": subject_did,
            "claims": claims,
            "issued_at": int(time.time()),
            # Prototype signature: hash of the payload (replace with ed25519 in production)
            "signature": hashlib.sha256(
                json.dumps(claims, sort_keys=True).encode()
            ).hexdigest()[:16],
        }
        self._credentials[cred_id] = credential
        subject_owner = subject_did.split(":")[-1]
        print(
            f"[credential] {issuer_did.split(':')[-1]:<6} issued "
            f"'{credential_type}' to {subject_owner}"
        )
        return cred_id

    def verify_credential(self, cred_id: str) -> bool:
        """
        Verify that *cred_id* is present in the registry and its signature
        matches its claims payload.
        """
        cred = self._credentials.get(cred_id)
        if cred is None:
            return False
        expected_sig = hashlib.sha256(
            json.dumps(cred["claims"], sort_keys=True).encode()
        ).hexdigest()[:16]
        valid = cred["signature"] == expected_sig
        subject_owner = cred["subject"].split(":")[-1]
        print(f"[verify] credential for {subject_owner:<6} valid={valid}")
        return valid

    def selective_disclosure(self, cred_id: str, fields: list) -> dict:
        """Return only the requested *fields* from a credential's claims."""
        cred = self._credentials.get(cred_id, {})
        claims = cred.get("claims", {})
        disclosed = {k: claims[k] for k in fields if k in claims}
        print(f"[selective] disclosed fields: {list(disclosed.keys())}")
        return disclosed


# ---------------------------------------------------------------------------
# GovernanceService
# ---------------------------------------------------------------------------

class GovernanceService:
    """
    Lightweight proposal/voting engine with a simple append-only hash chain.

    The hash chain provides a tamper-evident audit trail (Integrity Chain).
    Each proposal decision is anchored as a new block.
    """

    def __init__(self):
        self._proposals: dict = {}
        self._votes: dict = {}    # proposal_id → {voter_did: choice}
        self._chain: list = []    # list of block dicts

    def create_proposal(self, proposer_did: str, description: str) -> str:
        """Create a new proposal and return its id."""
        prop_id = f"P-{len(self._proposals) + 1}"
        self._proposals[prop_id] = {
            "id": prop_id,
            "proposer": proposer_did,
            "description": description,
            "status": "open",
            "created_at": int(time.time()),
        }
        self._votes[prop_id] = {}
        proposer_owner = proposer_did.split(":")[-1]
        print(
            f"[governance] proposal {prop_id} created by {proposer_owner:<6}: "
            f"\"{description}\""
        )
        return prop_id

    def vote(self, prop_id: str, voter_did: str, choice: str) -> None:
        """Cast a vote ('APPROVE' or 'REJECT') on *prop_id*."""
        if prop_id not in self._proposals:
            raise KeyError(f"Unknown proposal: {prop_id}")
        voter_owner = voter_did.split(":")[-1]
        self._votes[prop_id][voter_did] = choice
        print(f"[vote] {voter_owner:<6} → {choice} on {prop_id}")

    def tally(self, prop_id: str) -> str:
        """
        Tally votes, update proposal status, and anchor the decision to the
        hash chain.

        Returns 'PASSED' or 'FAILED'.
        """
        votes = self._votes.get(prop_id, {})
        approve = sum(1 for v in votes.values() if v == "APPROVE")
        reject = sum(1 for v in votes.values() if v == "REJECT")
        result = "PASSED" if approve > reject else "FAILED"
        self._proposals[prop_id]["status"] = result
        print(f"[tally] {prop_id}: approve={approve} reject={reject} → {result}")
        self._anchor(prop_id, result)
        return result

    def _anchor(self, prop_id: str, result: str) -> None:
        """Append a new block to the hash chain for this decision."""
        prev_hash = self._chain[-1]["hash"] if self._chain else "0" * 16
        payload = json.dumps(
            {"prop_id": prop_id, "result": result, "ts": int(time.time())},
            sort_keys=True,
        )
        block_hash = hashlib.sha256(
            (prev_hash + payload).encode()
        ).hexdigest()[:16]
        block = {
            "index": len(self._chain),
            "prev_hash": prev_hash,
            "payload": payload,
            "hash": block_hash,
        }
        self._chain.append(block)
        print(
            f"[chain] block {block['index']}: {prev_hash} → {block_hash}"
        )


# ---------------------------------------------------------------------------
# ReputationService
# ---------------------------------------------------------------------------

class ReputationService:
    """
    Simple trust-graph with a PageRank-style iterative score computation.

    Nodes endorse each other; higher in-weight from high-reputation nodes
    means a higher final score.
    """

    def __init__(self, damping: float = 0.85, iterations: int = 20):
        self._damping = damping
        self._iterations = iterations
        self._nodes: set = set()
        self._edges: list = []    # (source, target, weight)

    def add_node(self, node_id: str) -> None:
        self._nodes.add(node_id)

    def add_endorsement(self, source: str, target: str, weight: float = 1.0) -> None:
        """Record that *source* endorses *target* with the given *weight*."""
        self._nodes.update([source, target])
        self._edges.append((source, target, weight))

    def compute_scores(self) -> dict:
        """Return a dict mapping node_id → reputation score (sums to 1.0)."""
        nodes = list(self._nodes)
        n = len(nodes)
        if n == 0:
            return {}

        # Build weighted adjacency
        out_weight: dict = {nd: 0.0 for nd in nodes}
        in_edges: dict = {nd: [] for nd in nodes}
        for src, tgt, w in self._edges:
            if src in out_weight:
                out_weight[src] += w
            if tgt in in_edges:
                in_edges[tgt].append((src, w))

        # Initialise scores uniformly
        scores = {nd: 1.0 / n for nd in nodes}

        for _ in range(self._iterations):
            new_scores: dict = {}
            for nd in nodes:
                rank_sum = sum(
                    scores[src] * w / out_weight[src]
                    for src, w in in_edges[nd]
                    if out_weight[src] > 0
                )
                new_scores[nd] = (1 - self._damping) / n + self._damping * rank_sum
            scores = new_scores

        # Normalise
        total = sum(scores.values()) or 1.0
        scores = {nd: round(v / total, 4) for nd, v in scores.items()}

        score_str = "  ".join(f"{nd}={v}" for nd, v in sorted(scores.items()))
        print(f"[reputation] scores: {score_str}")
        return scores


# ---------------------------------------------------------------------------
# IncentiveService
# ---------------------------------------------------------------------------

class IncentiveService:
    """
    Token-based incentive ledger.

    In a real deployment this would integrate with the Integrity Chain so that
    every reward is a cryptographically signed receipt.
    """

    def __init__(self):
        self._balances: dict = {}

    def register(self, node_id: str, initial_balance: int = 100) -> None:
        self._balances[node_id] = initial_balance

    def reward(self, node_id: str, amount: int, reason: str = "") -> None:
        """Credit *amount* tokens to *node_id*."""
        self._balances[node_id] = self._balances.get(node_id, 0) + amount
        note = f" ({reason})" if reason else ""
        print(f"[incentive] rewarded {node_id} +{amount} tokens{note}")

    def print_balances(self) -> None:
        for node_id, balance in sorted(self._balances.items()):
            print(f"[incentive] {node_id} balance: {balance}")


# ---------------------------------------------------------------------------
# Main demo
# ---------------------------------------------------------------------------

def main() -> None:
    did_svc = DIDService()
    gov_svc = GovernanceService()
    rep_svc = ReputationService()
    inc_svc = IncentiveService()

    # --- Identity ---
    alice_did = did_svc.create_did("alice")
    bob_did = did_svc.create_did("bob")

    # Alice issues a credential to Bob certifying his role
    cred_id = did_svc.issue_credential(
        issuer_did=alice_did,
        subject_did=bob_did,
        credential_type="MeshMember",
        claims={"node_id": "bob", "role": "relay", "cell": "cell-01"},
    )
    did_svc.verify_credential(cred_id)
    did_svc.selective_disclosure(cred_id, ["node_id", "role"])

    # --- Governance ---
    prop_id = gov_svc.create_proposal(alice_did, "Increase cell bandwidth quota")
    gov_svc.vote(prop_id, alice_did, "APPROVE")
    gov_svc.vote(prop_id, bob_did, "APPROVE")
    gov_svc.tally(prop_id)

    # --- Reputation ---
    rep_svc.add_node("alice")
    rep_svc.add_node("bob")
    rep_svc.add_endorsement("alice", "bob", weight=1.0)
    rep_svc.add_endorsement("bob", "alice", weight=0.5)
    rep_svc.compute_scores()

    # --- Incentives ---
    inc_svc.register("alice", initial_balance=100)
    inc_svc.register("bob", initial_balance=100)
    inc_svc.reward("alice", 10, "proposal creation")
    inc_svc.reward("bob", 5, "governance participation")
    inc_svc.print_balances()


if __name__ == "__main__":
    main()
