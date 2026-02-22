"""
StorageService — SQLite-backed persistent state for the governance engine.

Provides schema creation, generic upsert/query helpers, and a thin ORM layer
using SQLAlchemy Core (no heavy ORM session required).  Designed for local-first,
offline-capable operation; swap the URL for PostgreSQL in a larger deployment.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class StorageService:
    """
    Thin persistence layer built on SQLAlchemy Core + SQLite.

    Parameters
    ----------
    db_url:
        SQLAlchemy database URL.  Defaults to an in-memory SQLite database
        (``sqlite:///:memory:``), which is ideal for tests and ephemeral nodes.
        Pass a file path such as ``sqlite:///governance.db`` for durable storage.
    """

    def __init__(self, db_url: str = "sqlite:///:memory:") -> None:
        # In-memory SQLite requires StaticPool so all connections share
        # the same in-process database; file-based SQLite uses the default pool.
        if db_url == "sqlite:///:memory:":
            self._engine: Engine = create_engine(
                db_url,
                echo=False,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            self._engine = create_engine(db_url, echo=False)
        self._meta = MetaData()
        self._define_schema()
        self._meta.create_all(self._engine)

    # ------------------------------------------------------------------
    # Schema definition
    # ------------------------------------------------------------------

    def _define_schema(self) -> None:
        self.dids = Table(
            "dids",
            self._meta,
            Column("did", String(128), primary_key=True),
            Column("owner", String(128), nullable=False),
            Column("created_at", DateTime, default=_utcnow),
        )

        self.credentials = Table(
            "credentials",
            self._meta,
            Column("id", String(64), primary_key=True),
            Column("credential_type", String(128), nullable=False),
            Column("issuer", String(128), nullable=False),
            Column("subject", String(128), nullable=False),
            Column("claims_json", Text, nullable=False),
            Column("signature", String(64), nullable=False),
            Column("issued_at", DateTime, default=_utcnow),
        )

        self.proposals = Table(
            "proposals",
            self._meta,
            Column("id", String(64), primary_key=True),
            Column("proposer", String(128), nullable=False),
            Column("description", Text, nullable=False),
            Column("status", String(32), nullable=False, default="open"),
            Column("created_at", DateTime, default=_utcnow),
        )

        self.votes = Table(
            "votes",
            self._meta,
            Column("proposal_id", String(64), nullable=False),
            Column("voter_did", String(128), nullable=False),
            Column("choice", String(32), nullable=False),
            Column("voted_at", DateTime, default=_utcnow),
        )

        self.chain_blocks = Table(
            "chain_blocks",
            self._meta,
            Column("index", Integer, primary_key=True, autoincrement=True),
            Column("prev_hash", String(64), nullable=False),
            Column("payload", Text, nullable=False),
            Column("block_hash", String(64), nullable=False),
            Column("created_at", DateTime, default=_utcnow),
        )

        self.reputation_scores = Table(
            "reputation_scores",
            self._meta,
            Column("node_id", String(128), primary_key=True),
            Column("score", Float, nullable=False, default=0.0),
            Column("updated_at", DateTime, default=_utcnow),
        )

        self.balances = Table(
            "balances",
            self._meta,
            Column("node_id", String(128), primary_key=True),
            Column("balance", Integer, nullable=False, default=0),
            Column("updated_at", DateTime, default=_utcnow),
        )

    # ------------------------------------------------------------------
    # Generic helpers
    # ------------------------------------------------------------------

    def execute(self, stmt: Any, params: dict | None = None) -> Any:
        """Execute a SQLAlchemy statement and return the result."""
        with self._engine.begin() as conn:
            return conn.execute(stmt, params or {})

    def fetch_one(self, stmt: Any) -> dict | None:
        with self._engine.connect() as conn:
            row = conn.execute(stmt).fetchone()
            return dict(row._mapping) if row else None

    def fetch_all(self, stmt: Any) -> list[dict]:
        with self._engine.connect() as conn:
            rows = conn.execute(stmt).fetchall()
            return [dict(r._mapping) for r in rows]

    # ------------------------------------------------------------------
    # DID helpers
    # ------------------------------------------------------------------

    def save_did(self, did: str, owner: str) -> None:
        with self._engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT OR REPLACE INTO dids (did, owner, created_at) "
                    "VALUES (:did, :owner, :created_at)"
                ),
                {"did": did, "owner": owner, "created_at": _utcnow()},
            )

    def get_did(self, did: str) -> dict | None:
        return self.fetch_one(self.dids.select().where(self.dids.c.did == did))

    # ------------------------------------------------------------------
    # Credential helpers
    # ------------------------------------------------------------------

    def save_credential(self, cred: dict) -> None:
        with self._engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT OR REPLACE INTO credentials "
                    "(id, credential_type, issuer, subject, claims_json, signature, issued_at) "
                    "VALUES (:id, :credential_type, :issuer, :subject, :claims_json, :signature, :issued_at)"
                ),
                {
                    "id": cred["id"],
                    "credential_type": cred["type"],
                    "issuer": cred["issuer"],
                    "subject": cred["subject"],
                    "claims_json": json.dumps(cred["claims"], sort_keys=True),
                    "signature": cred["signature"],
                    "issued_at": _utcnow(),
                },
            )

    def get_credential(self, cred_id: str) -> dict | None:
        row = self.fetch_one(
            self.credentials.select().where(self.credentials.c.id == cred_id)
        )
        if row:
            row["claims"] = json.loads(row.pop("claims_json"))
        return row

    # ------------------------------------------------------------------
    # Proposal helpers
    # ------------------------------------------------------------------

    def save_proposal(self, proposal: dict) -> None:
        with self._engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT OR REPLACE INTO proposals "
                    "(id, proposer, description, status, created_at) "
                    "VALUES (:id, :proposer, :description, :status, :created_at)"
                ),
                {
                    "id": proposal["id"],
                    "proposer": proposal["proposer"],
                    "description": proposal["description"],
                    "status": proposal["status"],
                    "created_at": _utcnow(),
                },
            )

    def get_proposal(self, proposal_id: str) -> dict | None:
        return self.fetch_one(
            self.proposals.select().where(self.proposals.c.id == proposal_id)
        )

    def list_proposals(self) -> list[dict]:
        return self.fetch_all(self.proposals.select())

    # ------------------------------------------------------------------
    # Vote helpers
    # ------------------------------------------------------------------

    def save_vote(self, proposal_id: str, voter_did: str, choice: str) -> None:
        # Upsert: remove existing vote from this voter then insert
        with self._engine.begin() as conn:
            conn.execute(
                text(
                    "DELETE FROM votes WHERE proposal_id = :pid AND voter_did = :vid"
                ),
                {"pid": proposal_id, "vid": voter_did},
            )
            conn.execute(
                text(
                    "INSERT INTO votes (proposal_id, voter_did, choice, voted_at) "
                    "VALUES (:pid, :vid, :choice, :voted_at)"
                ),
                {
                    "pid": proposal_id,
                    "vid": voter_did,
                    "choice": choice,
                    "voted_at": _utcnow(),
                },
            )

    def get_votes(self, proposal_id: str) -> list[dict]:
        return self.fetch_all(
            self.votes.select().where(self.votes.c.proposal_id == proposal_id)
        )

    # ------------------------------------------------------------------
    # Chain block helpers
    # ------------------------------------------------------------------

    def append_block(self, prev_hash: str, payload: str, block_hash: str) -> int:
        with self._engine.begin() as conn:
            result = conn.execute(
                text(
                    "INSERT INTO chain_blocks (prev_hash, payload, block_hash, created_at) "
                    "VALUES (:prev_hash, :payload, :block_hash, :created_at)"
                ),
                {
                    "prev_hash": prev_hash,
                    "payload": payload,
                    "block_hash": block_hash,
                    "created_at": _utcnow(),
                },
            )
            return result.lastrowid

    def get_chain(self) -> list[dict]:
        return self.fetch_all(self.chain_blocks.select().order_by(self.chain_blocks.c.index))

    def get_last_block_hash(self) -> str:
        blocks = self.get_chain()
        return blocks[-1]["block_hash"] if blocks else "0" * 16

    # ------------------------------------------------------------------
    # Reputation helpers
    # ------------------------------------------------------------------

    def save_reputation_score(self, node_id: str, score: float) -> None:
        with self._engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT OR REPLACE INTO reputation_scores (node_id, score, updated_at) "
                    "VALUES (:node_id, :score, :updated_at)"
                ),
                {"node_id": node_id, "score": score, "updated_at": _utcnow()},
            )

    def get_reputation_scores(self) -> dict[str, float]:
        rows = self.fetch_all(self.reputation_scores.select())
        return {r["node_id"]: r["score"] for r in rows}

    # ------------------------------------------------------------------
    # Balance helpers
    # ------------------------------------------------------------------

    def save_balance(self, node_id: str, balance: int) -> None:
        with self._engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT OR REPLACE INTO balances (node_id, balance, updated_at) "
                    "VALUES (:node_id, :balance, :updated_at)"
                ),
                {"node_id": node_id, "balance": balance, "updated_at": _utcnow()},
            )

    def get_balance(self, node_id: str) -> int:
        row = self.fetch_one(
            self.balances.select().where(self.balances.c.node_id == node_id)
        )
        return row["balance"] if row else 0

    def get_all_balances(self) -> dict[str, int]:
        rows = self.fetch_all(self.balances.select())
        return {r["node_id"]: r["balance"] for r in rows}
