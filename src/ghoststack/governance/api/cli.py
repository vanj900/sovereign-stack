"""
CLI interface for the governance engine.

Usage
-----
python -m ghoststack.governance.api.cli --help

Or, if installed as a package:
    gov --help
"""

from __future__ import annotations

import json
import os
import sys

import click

# Path bootstrap — ensure `src/` is importable when run directly
_here = os.path.dirname(os.path.abspath(__file__))
_src = os.path.normpath(os.path.join(_here, "..", "..", ".."))
if _src not in sys.path:
    sys.path.insert(0, _src)

from ghoststack.governance.config import DATABASE_URL, QUORUM  # noqa: E402
from ghoststack.governance.core.did_service import DIDService  # noqa: E402
from ghoststack.governance.core.governance_service import GovernanceService  # noqa: E402
from ghoststack.governance.core.incentive_service import IncentiveService  # noqa: E402
from ghoststack.governance.core.reputation_service import ReputationService  # noqa: E402
from ghoststack.governance.core.storage_service import StorageService  # noqa: E402


def _make_services(db_url: str) -> tuple:
    storage = StorageService(db_url)
    did = DIDService(storage)
    gov = GovernanceService(storage, quorum=QUORUM)
    rep = ReputationService(storage)
    inc = IncentiveService(storage)
    return storage, did, gov, rep, inc


@click.group()
@click.option(
    "--db",
    default=DATABASE_URL,
    envvar="GOV_DATABASE_URL",
    show_default=True,
    help="SQLAlchemy database URL",
)
@click.pass_context
def cli(ctx: click.Context, db: str) -> None:
    """Sovereign Stack Governance Engine CLI."""
    ctx.ensure_object(dict)
    ctx.obj["db"] = db


# ---------------------------------------------------------------------------
# DID commands
# ---------------------------------------------------------------------------

@cli.group()
def did() -> None:
    """Decentralised identity management."""


@did.command("create")
@click.argument("owner")
@click.pass_context
def did_create(ctx: click.Context, owner: str) -> None:
    """Create a DID for OWNER."""
    _, svc, _, _, _ = _make_services(ctx.obj["db"])
    did_str = svc.create_did(owner)
    click.echo(f"Created DID: {did_str}")


@did.command("issue-credential")
@click.argument("issuer_did")
@click.argument("subject_did")
@click.argument("credential_type")
@click.argument("claims_json")
@click.pass_context
def did_issue(
    ctx: click.Context,
    issuer_did: str,
    subject_did: str,
    credential_type: str,
    claims_json: str,
) -> None:
    """Issue a credential from ISSUER_DID to SUBJECT_DID of CREDENTIAL_TYPE with CLAIMS_JSON."""
    try:
        claims = json.loads(claims_json)
    except json.JSONDecodeError as exc:
        click.echo(f"Error: invalid claims JSON: {exc}", err=True)
        sys.exit(1)
    _, svc, _, _, _ = _make_services(ctx.obj["db"])
    try:
        cred_id = svc.issue_credential(issuer_did, subject_did, credential_type, claims)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    click.echo(f"Issued credential: {cred_id}")


@did.command("verify")
@click.argument("cred_id")
@click.pass_context
def did_verify(ctx: click.Context, cred_id: str) -> None:
    """Verify credential CRED_ID."""
    _, svc, _, _, _ = _make_services(ctx.obj["db"])
    valid = svc.verify_credential(cred_id)
    click.echo(f"Credential {cred_id} valid={valid}")


# ---------------------------------------------------------------------------
# Governance commands
# ---------------------------------------------------------------------------

@cli.group()
def gov() -> None:
    """Proposals and voting."""


@gov.command("propose")
@click.argument("proposer_did")
@click.argument("description")
@click.pass_context
def gov_propose(ctx: click.Context, proposer_did: str, description: str) -> None:
    """Create a new governance proposal."""
    _, _, svc, _, _ = _make_services(ctx.obj["db"])
    prop_id = svc.create_proposal(proposer_did, description)
    click.echo(f"Proposal created: {prop_id}")


@gov.command("vote")
@click.argument("prop_id")
@click.argument("voter_did")
@click.argument("choice", type=click.Choice(["APPROVE", "REJECT", "ABSTAIN"]))
@click.pass_context
def gov_vote(ctx: click.Context, prop_id: str, voter_did: str, choice: str) -> None:
    """Cast a vote on PROP_ID."""
    _, _, svc, _, _ = _make_services(ctx.obj["db"])
    try:
        svc.vote(prop_id, voter_did, choice)
    except (KeyError, ValueError, RuntimeError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    click.echo(f"Vote recorded: {voter_did} → {choice} on {prop_id}")


@gov.command("tally")
@click.argument("prop_id")
@click.option("--total-voters", default=None, type=int, help="Total eligible voter count")
@click.pass_context
def gov_tally(ctx: click.Context, prop_id: str, total_voters: int | None) -> None:
    """Tally votes for PROP_ID."""
    _, _, svc, _, _ = _make_services(ctx.obj["db"])
    try:
        result = svc.tally(prop_id, total_voters)
    except (KeyError, RuntimeError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    click.echo(f"Tally result for {prop_id}: {result}")


@gov.command("list")
@click.pass_context
def gov_list(ctx: click.Context) -> None:
    """List all proposals."""
    _, _, svc, _, _ = _make_services(ctx.obj["db"])
    proposals = svc.list_proposals()
    if not proposals:
        click.echo("No proposals found.")
        return
    for p in proposals:
        click.echo(f"  {p['id']} [{p['status']}] {p['description']}")


# ---------------------------------------------------------------------------
# Reputation commands
# ---------------------------------------------------------------------------

@cli.group()
def rep() -> None:
    """Reputation & trust scoring."""


@rep.command("endorse")
@click.argument("source")
@click.argument("target")
@click.option("--weight", default=1.0, show_default=True, type=float)
@click.pass_context
def rep_endorse(ctx: click.Context, source: str, target: str, weight: float) -> None:
    """Record that SOURCE endorses TARGET."""
    _, _, _, svc, _ = _make_services(ctx.obj["db"])
    svc.add_endorsement(source, target, weight)
    click.echo(f"Endorsement recorded: {source} → {target} (weight={weight})")


@rep.command("scores")
@click.pass_context
def rep_scores(ctx: click.Context) -> None:
    """Compute and display reputation scores."""
    _, _, _, svc, _ = _make_services(ctx.obj["db"])
    scores = svc.compute_scores()
    if not scores:
        click.echo("No reputation data yet.")
        return
    for node, score in sorted(scores.items(), key=lambda x: -x[1]):
        click.echo(f"  {node}: {score:.4f}")


# ---------------------------------------------------------------------------
# Incentive commands
# ---------------------------------------------------------------------------

@cli.group()
def incentive() -> None:
    """Token balance management."""


@incentive.command("register")
@click.argument("node_id")
@click.option("--balance", default=100, show_default=True, type=int)
@click.pass_context
def inc_register(ctx: click.Context, node_id: str, balance: int) -> None:
    """Register NODE_ID with an initial token balance."""
    _, _, _, _, svc = _make_services(ctx.obj["db"])
    svc.register(node_id, balance)
    click.echo(f"Registered {node_id} with balance={svc.get_balance(node_id)}")


@incentive.command("reward")
@click.argument("node_id")
@click.argument("amount", type=int)
@click.option("--reason", default="", help="Human-readable reason")
@click.pass_context
def inc_reward(ctx: click.Context, node_id: str, amount: int, reason: str) -> None:
    """Award AMOUNT tokens to NODE_ID."""
    _, _, _, _, svc = _make_services(ctx.obj["db"])
    new_bal = svc.reward(node_id, amount, reason)
    click.echo(f"Rewarded {node_id} +{amount} tokens → balance={new_bal}")


@incentive.command("balances")
@click.pass_context
def inc_balances(ctx: click.Context) -> None:
    """Display all token balances."""
    _, _, _, _, svc = _make_services(ctx.obj["db"])
    balances = svc.get_all_balances()
    if not balances:
        click.echo("No balances recorded.")
        return
    for node_id, bal in sorted(balances.items()):
        click.echo(f"  {node_id}: {bal}")


if __name__ == "__main__":
    cli()
