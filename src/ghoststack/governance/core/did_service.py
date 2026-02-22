"""
DIDService — Decentralised identity management.

Creates DIDs for nodes/agents, issues verifiable credentials, verifies them,
and supports selective disclosure.  Uses SHA-256 for prototype signatures;
a production deployment should use ed25519 key pairs and W3C DID documents.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .storage_service import StorageService


class DIDService:
    """
    Minimal decentralised-identity service backed by :class:`StorageService`.

    Parameters
    ----------
    storage:
        Shared storage instance.  If *None* an in-memory-only mode is used
        (state is not persisted across restarts).
    """

    def __init__(self, storage: "StorageService | None" = None) -> None:
        self._storage = storage
        # In-memory caches (always populated; storage is the durable layer)
        self._registry: dict = {}
        self._credentials: dict = {}

        if storage is not None:
            self._load_from_storage()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load_from_storage(self) -> None:
        """Hydrate caches from the database on startup."""
        storage = self._storage
        assert storage is not None
        for row in storage.fetch_all(storage.dids.select()):
            self._registry[row["did"]] = row
        for row in storage.fetch_all(storage.credentials.select()):
            row["claims"] = json.loads(row.pop("claims_json", "{}"))
            row["type"] = row.pop("credential_type", "")
            self._credentials[row["id"]] = row

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_did(self, owner: str) -> str:
        """
        Create and register a new DID for *owner*.

        Returns the DID string (``did:sov:<owner>``).
        """
        did = f"did:sov:{owner}"
        record = {"did": did, "owner": owner}
        self._registry[did] = record
        if self._storage:
            self._storage.save_did(did, owner)
        return did

    def get_did(self, owner: str) -> str | None:
        """Return the DID for *owner* if it exists, else *None*."""
        did = f"did:sov:{owner}"
        return did if did in self._registry else None

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
        if issuer_did not in self._registry:
            raise ValueError(f"Issuer DID not registered: {issuer_did}")
        if subject_did not in self._registry:
            raise ValueError(f"Subject DID not registered: {subject_did}")

        cred_id = str(uuid.uuid4())
        signature = _sign(claims)
        credential = {
            "id": cred_id,
            "type": credential_type,
            "issuer": issuer_did,
            "subject": subject_did,
            "claims": claims,
            "signature": signature,
        }
        self._credentials[cred_id] = credential
        if self._storage:
            self._storage.save_credential(credential)
        return cred_id

    def verify_credential(self, cred_id: str) -> bool:
        """
        Verify that *cred_id* is registered and its signature matches its claims.

        Returns *True* if valid, *False* otherwise.
        """
        cred = self._get_credential(cred_id)
        if cred is None:
            return False
        return cred.get("signature") == _sign(cred.get("claims", {}))

    def selective_disclosure(self, cred_id: str, fields: list[str]) -> dict:
        """Return only the requested *fields* from a credential's claims."""
        cred = self._get_credential(cred_id) or {}
        claims = cred.get("claims", {})
        return {k: claims[k] for k in fields if k in claims}

    def get_credential(self, cred_id: str) -> dict | None:
        """Return the full credential dict or *None* if not found."""
        return self._get_credential(cred_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_credential(self, cred_id: str) -> dict | None:
        if cred_id in self._credentials:
            return self._credentials[cred_id]
        if self._storage:
            row = self._storage.get_credential(cred_id)
            if row:
                row["type"] = row.pop("credential_type", row.get("type", ""))
                self._credentials[cred_id] = row
                return row
        return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sign(claims: dict) -> str:
    """Prototype signature: SHA-256 of sorted JSON claims."""
    return hashlib.sha256(
        json.dumps(claims, sort_keys=True).encode()
    ).hexdigest()
