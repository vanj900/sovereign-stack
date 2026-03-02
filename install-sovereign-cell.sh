#!/usr/bin/env bash
# install-sovereign-cell.sh
# One-command Termux install for a Sovereign Cell node.
# Runs on any Android phone with Termux installed (https://termux.dev).
#
# Usage:
#   bash install-sovereign-cell.sh
#
# What this does:
#   1. Installs Python and git via pkg (Termux package manager)
#   2. Clones the sovereign-stack repo if not already present
#   3. Installs Python dependencies
#   4. Starts a 3-node simulation to verify the install
#
# Axioms: Flow Over Containment | Sovereignty via Forkability | Truth by Receipts

set -e

REPO_URL="https://github.com/vanj900/sovereign-stack.git"
REPO_DIR="sovereign-stack"

# ── helpers ──────────────────────────────────────────────────────────────────

info()  { printf '\033[0;34m[info]\033[0m  %s\n' "$*"; }
ok()    { printf '\033[0;32m[ ok ]\033[0m  %s\n' "$*"; }
warn()  { printf '\033[0;33m[warn]\033[0m  %s\n' "$*"; }
die()   { printf '\033[0;31m[fail]\033[0m  %s\n' "$*" >&2; exit 1; }

# ── detect environment ────────────────────────────────────────────────────────

if [ -d "/data/data/com.termux" ] || [ -n "$TERMUX_VERSION" ]; then
    ENV="termux"
else
    ENV="posix"
fi

info "Detected environment: $ENV"

# ── step 1: install system dependencies ──────────────────────────────────────

if [ "$ENV" = "termux" ]; then
    info "Updating Termux packages..."
    pkg update -y 2>/dev/null || warn "pkg update encountered non-fatal errors"
    info "Installing python and git..."
    pkg install python git -y || die "Failed to install packages via pkg"
else
    # Desktop / CI fallback — check that python3 and git exist
    command -v python3 >/dev/null 2>&1 || die "python3 not found. Install Python 3.8+ first."
    command -v git    >/dev/null 2>&1 || die "git not found. Install git first."
    info "python3 and git found."
fi

ok "System dependencies ready."

# ── step 2: clone or update repo ──────────────────────────────────────────────

if [ -d "$REPO_DIR/.git" ]; then
    info "Repository already present — pulling latest changes..."
    git -C "$REPO_DIR" pull --ff-only || warn "Pull failed (offline?). Using existing checkout."
else
    info "Cloning sovereign-stack..."
    git clone "$REPO_URL" "$REPO_DIR" || die "Failed to clone repository."
fi

ok "Repository ready at ./$REPO_DIR"

cd "$REPO_DIR"

# ── step 3: install Python dependencies ──────────────────────────────────────

PYTHON="${PYTHON:-python3}"
# Termux ships 'python' pointing to python3
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python

REQUIREMENTS="src/mesh/shadow-net/bridge/requirements.txt"

if [ -f "$REQUIREMENTS" ]; then
    info "Installing Python dependencies from $REQUIREMENTS..."
    "$PYTHON" -m pip install --quiet --upgrade pip
    "$PYTHON" -m pip install --quiet -r "$REQUIREMENTS" || die "pip install failed."
else
    info "No requirements.txt found at $REQUIREMENTS — skipping pip install."
fi

ok "Python dependencies installed."

# ── step 4: run 3-node smoke test ─────────────────────────────────────────────

DEMO="src/mesh/shadow-net/bridge/demo.py"

if [ -f "$DEMO" ]; then
    info "Running 3-node governance simulation..."
    "$PYTHON" "$DEMO" && ok "3-node simulation passed." || die "Simulation failed — check output above."
else
    warn "demo.py not found at $DEMO — skipping smoke test."
fi

# ── done ──────────────────────────────────────────────────────────────────────

cat <<'EOF'

╔══════════════════════════════════════════════════════════╗
║         Sovereign Cell — install complete ✅             ║
╠══════════════════════════════════════════════════════════╣
║  Next steps:                                            ║
║                                                          ║
║  1. Start the governance CLI:                            ║
║     python src/mesh/shadow-net/bridge/cli.py start       ║
║                                                          ║
║  2. Send a proposal:                                     ║
║     python src/mesh/shadow-net/bridge/cli.py send \      ║
║       "Should we add energy tracking next?"              ║
║                                                          ║
║  3. Invite a second node (share your invite link).       ║
║                                                          ║
║  4. Read the phone guide:                                ║
║     docs/PHONE-QUICKSTART.md                             ║
║                                                          ║
║  Flow over containment. Fork or die trying.              ║
╚══════════════════════════════════════════════════════════╝
EOF
