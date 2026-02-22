"""
FastAPI REST API for the governance engine.

Endpoints are grouped by service:
  /did       — identity management
  /governance — proposals & voting
  /reputation — trust scores
  /incentive  — token balances
  /chain      — audit chain
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends, FastAPI, HTTPException

from .models import (
    AddEndorsementRequest,
    AllBalancesResponse,
    BalanceResponse,
    ChainBlockResponse,
    CreateDIDRequest,
    CreateProposalRequest,
    CredentialResponse,
    DIDResponse,
    IssueCredentialRequest,
    ProposalResponse,
    RegisterNodeRequest,
    ReputationScoresResponse,
    RewardRequest,
    SelectiveDisclosureRequest,
    SelectiveDisclosureResponse,
    TallyRequest,
    TallyResponse,
    VerifyCredentialResponse,
    VoteRequest,
)

if TYPE_CHECKING:
    from ..core.did_service import DIDService
    from ..core.governance_service import GovernanceService
    from ..core.incentive_service import IncentiveService
    from ..core.reputation_service import ReputationService

app = FastAPI(
    title="Sovereign Stack Governance Engine",
    description="Layer 2: Governance & Trust — decentralised identity, proposals, voting, reputation, and incentives.",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# Service registry (populated by main.py at startup)
# ---------------------------------------------------------------------------

_services: dict = {}


def get_did_service() -> "DIDService":
    svc = _services.get("did")
    if svc is None:
        raise HTTPException(status_code=503, detail="DIDService not initialised")
    return svc


def get_governance_service() -> "GovernanceService":
    svc = _services.get("governance")
    if svc is None:
        raise HTTPException(status_code=503, detail="GovernanceService not initialised")
    return svc


def get_reputation_service() -> "ReputationService":
    svc = _services.get("reputation")
    if svc is None:
        raise HTTPException(status_code=503, detail="ReputationService not initialised")
    return svc


def get_incentive_service() -> "IncentiveService":
    svc = _services.get("incentive")
    if svc is None:
        raise HTTPException(status_code=503, detail="IncentiveService not initialised")
    return svc


def register_services(
    did: "DIDService",
    governance: "GovernanceService",
    reputation: "ReputationService",
    incentive: "IncentiveService",
) -> None:
    """Inject service instances (called once at startup)."""
    _services["did"] = did
    _services["governance"] = governance
    _services["reputation"] = reputation
    _services["incentive"] = incentive


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# DID endpoints
# ---------------------------------------------------------------------------

@app.post("/did", response_model=DIDResponse, tags=["identity"])
def create_did(
    req: CreateDIDRequest,
    svc: "DIDService" = Depends(get_did_service),
) -> DIDResponse:
    did = svc.create_did(req.owner)
    return DIDResponse(did=did, owner=req.owner)


@app.post("/did/credential", response_model=CredentialResponse, tags=["identity"])
def issue_credential(
    req: IssueCredentialRequest,
    svc: "DIDService" = Depends(get_did_service),
) -> CredentialResponse:
    try:
        cred_id = svc.issue_credential(
            req.issuer_did, req.subject_did, req.credential_type, req.claims
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    cred = svc.get_credential(cred_id)
    return CredentialResponse(
        id=cred_id,
        credential_type=cred["type"],
        issuer=cred["issuer"],
        subject=cred["subject"],
        claims=cred["claims"],
        signature=cred["signature"],
    )


@app.get(
    "/did/credential/{cred_id}/verify",
    response_model=VerifyCredentialResponse,
    tags=["identity"],
)
def verify_credential(
    cred_id: str,
    svc: "DIDService" = Depends(get_did_service),
) -> VerifyCredentialResponse:
    valid = svc.verify_credential(cred_id)
    return VerifyCredentialResponse(cred_id=cred_id, valid=valid)


@app.post(
    "/did/credential/{cred_id}/disclose",
    response_model=SelectiveDisclosureResponse,
    tags=["identity"],
)
def selective_disclosure(
    cred_id: str,
    req: SelectiveDisclosureRequest,
    svc: "DIDService" = Depends(get_did_service),
) -> SelectiveDisclosureResponse:
    disclosed = svc.selective_disclosure(cred_id, req.fields)
    return SelectiveDisclosureResponse(cred_id=cred_id, disclosed=disclosed)


# ---------------------------------------------------------------------------
# Governance endpoints
# ---------------------------------------------------------------------------

@app.post(
    "/governance/proposals",
    response_model=ProposalResponse,
    tags=["governance"],
)
def create_proposal(
    req: CreateProposalRequest,
    svc: "GovernanceService" = Depends(get_governance_service),
) -> ProposalResponse:
    prop_id = svc.create_proposal(req.proposer_did, req.description)
    prop = svc.get_proposal(prop_id)
    return ProposalResponse(**prop)


@app.get(
    "/governance/proposals",
    response_model=list[ProposalResponse],
    tags=["governance"],
)
def list_proposals(
    svc: "GovernanceService" = Depends(get_governance_service),
) -> list[ProposalResponse]:
    return [ProposalResponse(**p) for p in svc.list_proposals()]


@app.get(
    "/governance/proposals/{prop_id}",
    response_model=ProposalResponse,
    tags=["governance"],
)
def get_proposal(
    prop_id: str,
    svc: "GovernanceService" = Depends(get_governance_service),
) -> ProposalResponse:
    prop = svc.get_proposal(prop_id)
    if prop is None:
        raise HTTPException(status_code=404, detail=f"Proposal {prop_id} not found")
    return ProposalResponse(**prop)


@app.post(
    "/governance/proposals/{prop_id}/vote",
    tags=["governance"],
)
def cast_vote(
    prop_id: str,
    req: VoteRequest,
    svc: "GovernanceService" = Depends(get_governance_service),
) -> dict:
    try:
        svc.vote(prop_id, req.voter_did, req.choice)
    except (KeyError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"proposal_id": prop_id, "voter_did": req.voter_did, "choice": req.choice}


@app.post(
    "/governance/proposals/{prop_id}/tally",
    response_model=TallyResponse,
    tags=["governance"],
)
def tally_proposal(
    prop_id: str,
    req: TallyRequest,
    svc: "GovernanceService" = Depends(get_governance_service),
) -> TallyResponse:
    try:
        result = svc.tally(prop_id, req.total_voters)
    except (KeyError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    votes = svc.get_votes(prop_id)
    return TallyResponse(
        proposal_id=prop_id,
        result=result,
        approve=sum(1 for v in votes.values() if v == "APPROVE"),
        reject=sum(1 for v in votes.values() if v == "REJECT"),
        abstain=sum(1 for v in votes.values() if v == "ABSTAIN"),
    )


# ---------------------------------------------------------------------------
# Chain endpoints
# ---------------------------------------------------------------------------

@app.get(
    "/chain",
    response_model=list[ChainBlockResponse],
    tags=["chain"],
)
def get_chain(
    svc: "GovernanceService" = Depends(get_governance_service),
) -> list[ChainBlockResponse]:
    blocks = svc.get_chain()
    return [
        ChainBlockResponse(
            index=b.get("index", i),
            prev_hash=b["prev_hash"],
            payload=b["payload"],
            block_hash=b["block_hash"],
        )
        for i, b in enumerate(blocks)
    ]


# ---------------------------------------------------------------------------
# Reputation endpoints
# ---------------------------------------------------------------------------

@app.post(
    "/reputation/endorse",
    tags=["reputation"],
)
def add_endorsement(
    req: AddEndorsementRequest,
    svc: "ReputationService" = Depends(get_reputation_service),
) -> dict:
    svc.add_endorsement(req.source, req.target, req.weight)
    return {"source": req.source, "target": req.target, "weight": req.weight}


@app.post(
    "/reputation/compute",
    response_model=ReputationScoresResponse,
    tags=["reputation"],
)
def compute_scores(
    svc: "ReputationService" = Depends(get_reputation_service),
) -> ReputationScoresResponse:
    scores = svc.compute_scores()
    return ReputationScoresResponse(scores=scores)


@app.get(
    "/reputation/scores",
    response_model=ReputationScoresResponse,
    tags=["reputation"],
)
def get_scores(
    svc: "ReputationService" = Depends(get_reputation_service),
) -> ReputationScoresResponse:
    return ReputationScoresResponse(scores=svc.get_scores())


# ---------------------------------------------------------------------------
# Incentive endpoints
# ---------------------------------------------------------------------------

@app.post("/incentive/register", response_model=BalanceResponse, tags=["incentive"])
def register_node(
    req: RegisterNodeRequest,
    svc: "IncentiveService" = Depends(get_incentive_service),
) -> BalanceResponse:
    svc.register(req.node_id, req.initial_balance)
    return BalanceResponse(node_id=req.node_id, balance=svc.get_balance(req.node_id))


@app.post("/incentive/reward", response_model=BalanceResponse, tags=["incentive"])
def reward_node(
    req: RewardRequest,
    svc: "IncentiveService" = Depends(get_incentive_service),
) -> BalanceResponse:
    new_balance = svc.reward(req.node_id, req.amount, req.reason)
    return BalanceResponse(node_id=req.node_id, balance=new_balance)


@app.get(
    "/incentive/balances",
    response_model=AllBalancesResponse,
    tags=["incentive"],
)
def get_all_balances(
    svc: "IncentiveService" = Depends(get_incentive_service),
) -> AllBalancesResponse:
    return AllBalancesResponse(balances=svc.get_all_balances())


@app.get(
    "/incentive/balances/{node_id}",
    response_model=BalanceResponse,
    tags=["incentive"],
)
def get_balance(
    node_id: str,
    svc: "IncentiveService" = Depends(get_incentive_service),
) -> BalanceResponse:
    return BalanceResponse(node_id=node_id, balance=svc.get_balance(node_id))
