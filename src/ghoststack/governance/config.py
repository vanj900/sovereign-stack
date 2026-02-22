"""
Configuration management for the governance engine.

Settings can be provided via environment variables or a .env file.
All variables are prefixed with ``GOV_``.
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

#: SQLAlchemy database URL.  Defaults to a local SQLite file.
DATABASE_URL: str = os.environ.get(
    "GOV_DATABASE_URL", "sqlite:///governance.db"
)

# ---------------------------------------------------------------------------
# API server
# ---------------------------------------------------------------------------

#: Host to bind the REST API server.
API_HOST: str = os.environ.get("GOV_API_HOST", "0.0.0.0")

#: Port for the REST API server.
API_PORT: int = int(os.environ.get("GOV_API_PORT", "8000"))

# ---------------------------------------------------------------------------
# Governance parameters
# ---------------------------------------------------------------------------

#: Minimum fraction of eligible voters required for a quorum.
QUORUM: float = float(os.environ.get("GOV_QUORUM", "0.5"))

# ---------------------------------------------------------------------------
# Reputation parameters
# ---------------------------------------------------------------------------

#: PageRank damping factor.
REPUTATION_DAMPING: float = float(os.environ.get("GOV_REPUTATION_DAMPING", "0.85"))

#: Number of PageRank iterations.
REPUTATION_ITERATIONS: int = int(os.environ.get("GOV_REPUTATION_ITERATIONS", "20"))

#: Half-life for reputation decay in days (set to 0 to disable).
REPUTATION_DECAY_HALF_LIFE_DAYS: float | None = (
    float(os.environ.get("GOV_REPUTATION_DECAY_HALF_LIFE_DAYS", "30"))
    or None
)

# ---------------------------------------------------------------------------
# Incentive parameters
# ---------------------------------------------------------------------------

#: Default initial token balance for new nodes.
INITIAL_BALANCE: int = int(os.environ.get("GOV_INITIAL_BALANCE", "100"))

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

#: Logging level (DEBUG / INFO / WARNING / ERROR).
LOG_LEVEL: str = os.environ.get("GOV_LOG_LEVEL", "INFO").upper()
