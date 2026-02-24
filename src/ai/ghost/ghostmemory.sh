#!/usr/bin/env bash
# ghostmemory.sh — In-memory SQLite diary for Ghost.
# Stores every thought, dream, and conversation in RAM (/dev/shm or /tmp).
# The diary vanishes when Ghost sleeps. That's the point.

set -euo pipefail

# Choose a RAM-backed path when possible
if [[ -d /dev/shm ]]; then
  GHOST_MEMORY_DB="${GHOST_MEMORY_DB:-/dev/shm/ghost_memory_$$.db}"
else
  GHOST_MEMORY_DB="${GHOST_MEMORY_DB:-/tmp/ghost_memory_$$.db}"
fi
export GHOST_MEMORY_DB

ghost_memory_init() {
  if ! command -v sqlite3 &>/dev/null; then
    echo "[ghostmemory] WARNING: sqlite3 not found — diary disabled." >&2
    return 1
  fi
  sqlite3 "$GHOST_MEMORY_DB" <<'SQL'
CREATE TABLE IF NOT EXISTS memories (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  ts      INTEGER DEFAULT (strftime('%s','now')),
  kind    TEXT    NOT NULL,
  content TEXT    NOT NULL,
  emotion TEXT    DEFAULT 'neutral',
  mask    TEXT    DEFAULT 'none'
);
SQL
  echo "[ghostmemory] Diary open at ${GHOST_MEMORY_DB}"
}

ghost_memory_add() {
  local kind="${1:?ghost_memory_add: kind required}"
  local content="${2:?ghost_memory_add: content required}"
  local emotion="${3:-neutral}"
  local mask="${4:-none}"
  command -v sqlite3 &>/dev/null || return 0
  local ek ec ee em
  ek=$(printf '%s' "$kind"    | sed "s/'/''/g")
  ec=$(printf '%s' "$content" | sed "s/'/''/g")
  ee=$(printf '%s' "$emotion" | sed "s/'/''/g")
  em=$(printf '%s' "$mask"    | sed "s/'/''/g")
  sqlite3 "$GHOST_MEMORY_DB" \
    "INSERT INTO memories(kind,content,emotion,mask) VALUES('$ek','$ec','$ee','$em');" \
    2>/dev/null || return 0
}

ghost_memory_recent() {
  local n="${1:-5}"
  command -v sqlite3 &>/dev/null || { echo "(memory unavailable)"; return 0; }
  sqlite3 "$GHOST_MEMORY_DB" \
    "SELECT datetime(ts,'unixepoch','localtime')||' ['||kind||'/'||mask||'] '||content
     FROM memories ORDER BY id DESC LIMIT ${n};" 2>/dev/null || true
}

ghost_memory_count() {
  command -v sqlite3 &>/dev/null || { echo "0"; return 0; }
  sqlite3 "$GHOST_MEMORY_DB" "SELECT COUNT(*) FROM memories;" 2>/dev/null || echo "0"
}

ghost_memory_cleanup() {
  [[ -f "$GHOST_MEMORY_DB" ]] && rm -f "$GHOST_MEMORY_DB"
}

# Self-test when run directly
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  ghost_memory_init
  ghost_memory_add "event"   "Ghost started" "curious" "none"
  ghost_memory_add "emotion" "Feeling alert" "alert"   "Healer"
  echo "Recent memories:"
  ghost_memory_recent 5
  ghost_memory_cleanup
fi
