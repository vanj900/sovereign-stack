#!/usr/bin/env bash
# setup_dual.sh — bootstrap Ghost Dual on this machine.
# Creates /dev/shm/ghost_dual/, checks Ollama, sets permissions.
# Run once before ghost_dual_daemon.py.

set -euo pipefail

GHOST_DIR="$(cd "$(dirname "$0")" && pwd)"
SHM_ROOT="/dev/shm/ghost_dual"

echo "=== Ghost Dual Setup ==="
echo "Working dir: $GHOST_DIR"

# ── 1. /dev/shm check ────────────────────────────────────────────────────────
if ! mountpoint -q /dev/shm 2>/dev/null && [ ! -d /dev/shm ]; then
    echo "[ERROR] /dev/shm not found — this system cannot run Ghost Dual."
    exit 1
fi

mkdir -p "$SHM_ROOT"
chmod 700 "$SHM_ROOT"
echo "[ok] $SHM_ROOT created (tmpfs — state dies on reboot)"

# ── 2. Python ≥3.11 ──────────────────────────────────────────────────────────
PYTHON="${PYTHON:-python3}"
PY_VER=$("$PYTHON" -c "import sys; print(sys.version_info >= (3,11))" 2>/dev/null || echo "False")
if [ "$PY_VER" != "True" ]; then
    echo "[WARN] Python 3.11+ recommended (got $("$PYTHON" --version 2>&1))"
fi
echo "[ok] Python: $("$PYTHON" --version)"

# ── 3. Ollama ─────────────────────────────────────────────────────────────────
OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
if curl -sf "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
    echo "[ok] Ollama is running at $OLLAMA_URL"
else
    echo "[WARN] Ollama not reachable at $OLLAMA_URL"
    echo "       Start with: ollama serve"
    echo "       Fast model: ollama pull phi3:mini"
    echo "       Slow model: ollama pull llama3.2:3b"
fi

# ── 4. Models present? ────────────────────────────────────────────────────────
FAST_MODEL="${GHOST_FAST_MODEL:-phi3:mini}"
SLOW_MODEL="${GHOST_SLOW_MODEL:-llama3.2:3b}"
for MODEL in "$FAST_MODEL" "$SLOW_MODEL"; do
    if curl -sf "$OLLAMA_URL/api/tags" 2>/dev/null | grep -q "\"$MODEL\""; then
        echo "[ok] model $MODEL found"
    else
        echo "[WARN] model '$MODEL' not found — run: ollama pull $MODEL"
    fi
done

# ── 5. thermodynamic_agency reachable ────────────────────────────────────────
THERMO_PATH="$GHOST_DIR/../../ai/thermo-ai/src"
if [ -d "$THERMO_PATH/thermodynamic_agency" ]; then
    echo "[ok] thermodynamic_agency package found at $THERMO_PATH"
else
    echo "[WARN] thermodynamic_agency not found at $THERMO_PATH"
    echo "       Ensure src/ai/thermo-ai/src is in PYTHONPATH or install the package."
fi

# ── 6. chmod ──────────────────────────────────────────────────────────────────
chmod +x "$GHOST_DIR/ghost_dual_daemon.py" \
         "$GHOST_DIR/fast_model.py"        \
         "$GHOST_DIR/slow_model.py"        \
         "$GHOST_DIR/mindseed.py"          \
         2>/dev/null || true

echo ""
echo "=== Setup complete ==="
echo ""
echo "Run commands:"
echo "  cd $GHOST_DIR"
echo "  python ghost_dual_daemon.py                        # fresh spawn"
echo "  python ghost_dual_daemon.py --seed /tmp/mindseed.json  # resume from MindSeed"
echo ""
echo "Export MindSeed manually: python -c \""
echo "  import sys; sys.path.insert(0,'$GHOST_DIR'); \\"
echo "  from mindseed import export_mindseed; print('use daemon x command')\""
echo ""
echo "Human veto: type 'v' then Enter at the ghost> prompt."
echo "Fork a new cell: copy /tmp/mindseed_<ts>.json, Ctrl-C old ghost, spawn new with --seed."
