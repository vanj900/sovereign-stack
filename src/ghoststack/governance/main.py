"""
Governance Engine entry point.

Usage
-----
Run the REST API server:
    python -m ghoststack.governance.main
    cd src && python -m ghoststack.governance.main

Run a quick self-test (no server):
    cd src && python -m ghoststack.governance.main --demo
    python -m ghoststack.governance.main --demo  (from src/ directory)
"""

from __future__ import annotations

import logging
import os
import sys

import click

# ---------------------------------------------------------------------------
# Path bootstrap — resolve the `src/` directory so `ghoststack` is importable
# when this module is executed directly (e.g. `python main.py`) or via pytest.
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_src = os.path.normpath(os.path.join(_here, "..", ".."))
if _src not in sys.path:
    sys.path.insert(0, _src)

from ghoststack.governance.config import (  # noqa: E402
    API_HOST,
    API_PORT,
    DATABASE_URL,
    INITIAL_BALANCE,
    LOG_LEVEL,
    QUORUM,
    REPUTATION_DAMPING,
    REPUTATION_DECAY_HALF_LIFE_DAYS,
    REPUTATION_ITERATIONS,
)
from ghoststack.governance.core.did_service import DIDService  # noqa: E402
from ghoststack.governance.core.governance_service import GovernanceService  # noqa: E402
from ghoststack.governance.core.incentive_service import IncentiveService  # noqa: E402
from ghoststack.governance.core.reputation_service import ReputationService  # noqa: E402
from ghoststack.governance.core.storage_service import StorageService  # noqa: E402

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def build_services(db_url: str = DATABASE_URL):
    """Construct and return all service instances sharing one storage backend."""
    storage = StorageService(db_url)
    did = DIDService(storage)
    governance = GovernanceService(storage, quorum=QUORUM)
    reputation = ReputationService(
        storage,
        damping=REPUTATION_DAMPING,
        iterations=REPUTATION_ITERATIONS,
        decay_half_life_days=REPUTATION_DECAY_HALF_LIFE_DAYS,
    )
    incentive = IncentiveService(storage)
    return storage, did, governance, reputation, incentive


def run_demo() -> None:
    """
    Run a self-contained governance workflow demo using an in-memory database.

    This proves the engine works end-to-end without any network access.
    """
    print("=" * 60)
    print("  Sovereign Stack Governance Engine — Demo")
    print("=" * 60)

    _, did_svc, gov_svc, rep_svc, inc_svc = build_services("sqlite:///:memory:")

    # --- Identity ---
    print("\n--- Identity ---")
    alice_did = did_svc.create_did("alice")
    bob_did = did_svc.create_did("bob")
    carol_did = did_svc.create_did("carol")
    print(f"  Alice:  {alice_did}")
    print(f"  Bob:    {bob_did}")
    print(f"  Carol:  {carol_did}")

    cred_id = did_svc.issue_credential(
        alice_did,
        bob_did,
        "MeshMember",
        {"node_id": "bob", "role": "relay", "cell": "cell-01"},
    )
    valid = did_svc.verify_credential(cred_id)
    disclosed = did_svc.selective_disclosure(cred_id, ["node_id", "role"])
    print(f"  Credential valid: {valid}")
    print(f"  Disclosed fields: {disclosed}")

    # --- Governance ---
    print("\n--- Governance ---")
    prop_id = gov_svc.create_proposal(alice_did, "Increase cell bandwidth quota")
    gov_svc.vote(prop_id, alice_did, "APPROVE")
    gov_svc.vote(prop_id, bob_did, "APPROVE")
    gov_svc.vote(prop_id, carol_did, "REJECT")
    result = gov_svc.tally(prop_id)
    print(f"  Proposal {prop_id}: {result}")

    prop2 = gov_svc.create_proposal(bob_did, "Enable mesh encryption layer")
    gov_svc.vote(prop2, alice_did, "APPROVE")
    gov_svc.vote(prop2, bob_did, "APPROVE")
    gov_svc.vote(prop2, carol_did, "APPROVE")
    result2 = gov_svc.tally(prop2)
    print(f"  Proposal {prop2}: {result2}")

    # --- Reputation ---
    print("\n--- Reputation ---")
    rep_svc.add_node("alice")
    rep_svc.add_node("bob")
    rep_svc.add_node("carol")
    rep_svc.add_endorsement("alice", "bob", weight=1.0)
    rep_svc.add_endorsement("alice", "carol", weight=0.8)
    rep_svc.add_endorsement("bob", "alice", weight=0.5)
    rep_svc.add_endorsement("carol", "bob", weight=0.3)
    scores = rep_svc.compute_scores()
    for node, score in sorted(scores.items(), key=lambda x: -x[1]):
        print(f"  {node}: {score:.4f}")

    # --- Incentives ---
    print("\n--- Incentives ---")
    inc_svc.register("alice", INITIAL_BALANCE)
    inc_svc.register("bob", INITIAL_BALANCE)
    inc_svc.register("carol", INITIAL_BALANCE)
    inc_svc.reward("alice", 10, "proposal creation")
    inc_svc.reward("bob", 5, "governance participation")
    inc_svc.reward("carol", 5, "governance participation")
    for node_id, bal in sorted(inc_svc.get_all_balances().items()):
        print(f"  {node_id}: {bal} tokens")

    # --- Chain ---
    print("\n--- Audit Chain ---")
    chain = gov_svc.get_chain()
    for block in chain:
        print(
            f"  block {block.get('index', '?'):>2}: {block['prev_hash'][:8]}… "
            f"→ {block['block_hash'][:8]}…"
        )

    print("\n✅  Governance engine demo completed successfully.\n")


@click.command()
@click.option(
    "--host", default=API_HOST, show_default=True, envvar="GOV_API_HOST",
    help="Host to bind the API server"
)
@click.option(
    "--port", default=API_PORT, show_default=True, envvar="GOV_API_PORT", type=int,
    help="Port for the API server"
)
@click.option(
    "--db", default=DATABASE_URL, show_default=True, envvar="GOV_DATABASE_URL",
    help="SQLAlchemy database URL"
)
@click.option(
    "--demo", is_flag=True, default=False,
    help="Run a local demo without starting the API server"
)
def main(host: str, port: int, db: str, demo: bool) -> None:
    """Start the Sovereign Stack Governance Engine REST API."""
    if demo:
        run_demo()
        return

    try:
        import uvicorn
    except ImportError:
        logger.error("uvicorn is not installed. Run: pip install uvicorn")
        sys.exit(1)

    from ghoststack.governance.api.rest_api import app, register_services

    _, did, governance, reputation, incentive = build_services(db)
    register_services(did, governance, reputation, incentive)

    logger.info("Starting Governance Engine on %s:%d (db=%s)", host, port, db)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
