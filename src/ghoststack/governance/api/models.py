"""Pydantic request/response models for the governance REST API."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# DID models
# ---------------------------------------------------------------------------

class CreateDIDRequest(BaseModel):
    owner: str = Field(..., description="Human-readable owner name for the DID")


class DIDResponse(BaseModel):
    did: str
    owner: str


class IssueCredentialRequest(BaseModel):
    issuer_did: str
    subject_did: str
    credential_type: str
    claims: dict


class CredentialResponse(BaseModel):
    id: str
    credential_type: str
    issuer: str
    subject: str
    claims: dict
    signature: str


class VerifyCredentialResponse(BaseModel):
    cred_id: str
    valid: bool


class SelectiveDisclosureRequest(BaseModel):
    fields: list[str]


class SelectiveDisclosureResponse(BaseModel):
    cred_id: str
    disclosed: dict


# ---------------------------------------------------------------------------
# Governance models
# ---------------------------------------------------------------------------

class CreateProposalRequest(BaseModel):
    proposer_did: str
    description: str = Field(..., min_length=1)


class ProposalResponse(BaseModel):
    id: str
    proposer: str
    description: str
    status: str


class VoteRequest(BaseModel):
    voter_did: str
    choice: str = Field(..., pattern="^(APPROVE|REJECT|ABSTAIN)$")


class TallyRequest(BaseModel):
    total_voters: Optional[int] = Field(None, ge=0)


class TallyResponse(BaseModel):
    proposal_id: str
    result: str
    approve: int
    reject: int
    abstain: int


class ChainBlockResponse(BaseModel):
    index: int
    prev_hash: str
    payload: str
    block_hash: str


# ---------------------------------------------------------------------------
# Reputation models
# ---------------------------------------------------------------------------

class AddEndorsementRequest(BaseModel):
    source: str
    target: str
    weight: float = Field(1.0, gt=0)


class ReputationScoresResponse(BaseModel):
    scores: dict[str, float]


# ---------------------------------------------------------------------------
# Incentive models
# ---------------------------------------------------------------------------

class RegisterNodeRequest(BaseModel):
    node_id: str
    initial_balance: int = Field(100, ge=0)


class RewardRequest(BaseModel):
    node_id: str
    amount: int
    reason: str = ""


class BalanceResponse(BaseModel):
    node_id: str
    balance: int


class AllBalancesResponse(BaseModel):
    balances: dict[str, int]
