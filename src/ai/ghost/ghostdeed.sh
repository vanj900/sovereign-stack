#!/usr/bin/env bash
# ghostdeed.sh — Ghost → deed-ledger bridge.
#
# After each adapt cycle Ghost calls ghost_deed_post() which:
#   1. Builds a Nostr-compatible deed event JSON from current state.
#   2. If websocat + GHOST_NOSTR_RELAY are set, publishes to the relay.
#   3. Always appends the event to a local append-only deed journal
#      (GHOST_DEED_JOURNAL, default /dev/shm/ghost_deeds_<pid>.jsonl).
#
# Ephemerality note:
#   The journal defaults to /dev/shm (tmpfs — pure RAM, vanishes on reboot).
#   If /dev/shm is unavailable it falls back to /tmp (disk-backed).
#   The fallback changes persistence: /tmp survives reboots unless explicitly
#   cleaned.  ghost_deed_cleanup() removes the journal on Ghost exit in both
#   cases, so the receipt still disappears with the process.
#
# Configuration (set in environment before launching ghostbrain.sh):
#   GHOST_NOSTR_RELAY   wss://... relay URL  (optional — local journal if unset)
#   GHOST_DEED_JOURNAL  path to journal file  (default /dev/shm/ghost_deeds_<pid>.jsonl)
#
# The unsigned pubkey/id/sig fields are left empty when GHOST_NOSTR_NSEC is
# not configured. Sign via `nak event` once you have a Nostr keypair:
#   echo "$json" | nak event --sec "$GHOST_NOSTR_NSEC"
# See docs/INTEGRATION.md — "Task 1: Nostr signing" for the full wiring.

set -euo pipefail

# Deed journal: ephemeral RAM file tied to this Ghost process
if [[ -d /dev/shm ]]; then
  GHOST_DEED_JOURNAL="${GHOST_DEED_JOURNAL:-/dev/shm/ghost_deeds_$$.jsonl}"
else
  GHOST_DEED_JOURNAL="${GHOST_DEED_JOURNAL:-/tmp/ghost_deeds_$$.jsonl}"
fi
export GHOST_DEED_JOURNAL

# ── Build the deed event JSON ──────────────────────────────────────────────────
# Produces a Nostr kind-30023 (long-form content) event.
# Tags encode Ghost's current state so the deed-ledger can index it.
ghost_deed_build() {
  local now cycles stage mask consistency adaptability proactivity curiosity
  now=$(date +%s)
  cycles="${GHOST_CYCLES:-0}"
  stage="${GHOST_STAGE:-dormant}"
  mask="${GHOST_MASK:-none}"
  consistency="${GHOST_M_CONSISTENCY:-0}"
  adaptability="${GHOST_M_ADAPTABILITY:-0}"
  proactivity="${GHOST_M_PROACTIVITY:-0}"
  curiosity="${GHOST_M_CURIOSITY:-0}"

  local deed_id="ghost-adapt-${cycles}-${now}"
  local content="Ghost adaptation cycle ${cycles}: stage=${stage} mask=${mask} consistency=${consistency} adaptability=${adaptability} proactivity=${proactivity} curiosity=${curiosity}"

  # Emit JSON to stdout — caller captures it
  printf '{
  "kind": 30023,
  "created_at": %s,
  "tags": [
    ["d", "%s"],
    ["t", "ghost_adapt"],
    ["layer", "ghostbrain"],
    ["stage", "%s"],
    ["mask", "%s"],
    ["consistency", "%s"],
    ["adaptability", "%s"],
    ["proactivity", "%s"],
    ["curiosity", "%s"]
  ],
  "content": "%s",
  "pubkey": "",
  "id": "",
  "sig": ""
}\n' \
    "$now" "$deed_id" "$stage" "$mask" \
    "$consistency" "$adaptability" "$proactivity" "$curiosity" \
    "$content"
}

# ── Sign deed event via nak CLI ───────────────────────────────────────────────
# Returns signed event JSON to stdout.  Falls back to unsigned if nak is absent
# or GHOST_NOSTR_NSEC is not configured.
# Install nak: go install github.com/fiatjaf/nak@v0.10.0
ghost_deed_sign() {
  local json="$1"
  # Require both nak binary and a configured nsec key
  if [[ -z "${GHOST_NOSTR_NSEC:-}" ]]; then
    echo "[ghostdeed] INFO: GHOST_NOSTR_NSEC not set — skipping Nostr signing" >&2
    printf '%s' "$json"
    return 0
  fi
  if ! command -v nak &>/dev/null; then
    echo "[ghostdeed] INFO: nak not found — skipping Nostr signing (install: go install github.com/fiatjaf/nak@v0.10.0)" >&2
    printf '%s' "$json"
    return 0
  fi
  # nak event --sec reads from stdin and outputs the signed event JSON
  local signed nak_err
  nak_err=$(mktemp)
  signed=$(printf '%s' "$json" | nak event --sec "$GHOST_NOSTR_NSEC" 2>"$nak_err") || {
    echo "[ghostdeed] WARN: nak signing failed — $(cat "$nak_err") — falling back to unsigned event" >&2
    rm -f "$nak_err"
    printf '%s' "$json"
    return 0
  }
  rm -f "$nak_err"
  printf '%s' "$signed"
}

# ── Append to local deed journal ───────────────────────────────────────────────
ghost_deed_journal() {
  local event_json="$1"
  printf '%s\n' "$event_json" >> "$GHOST_DEED_JOURNAL"
}

# ── Publish to Nostr relay via websocat ───────────────────────────────────────
# Silently skips if websocat is not installed or GHOST_NOSTR_RELAY is unset.
# Logs a warning to stderr if the relay connection times out or fails.
ghost_deed_publish() {
  local event_json="$1"
  [[ -z "${GHOST_NOSTR_RELAY:-}" ]] && return 0
  command -v websocat &>/dev/null || return 0

  # Nostr wire protocol: ["EVENT", <event>]
  local wire_msg
  wire_msg="[\"EVENT\",${event_json}]"
  if ! printf '%s\n' "$wire_msg" \
    | timeout 5 websocat --no-close -1 "$GHOST_NOSTR_RELAY" \
    >/dev/null 2>&1; then
    echo "[ghostdeed] WARN: relay publish failed (relay=${GHOST_NOSTR_RELAY})" >&2
  fi
}

# ── POST to deed-ledger ingest endpoint ──────────────────────────────────────
# Silently skips if curl is not installed or GHOST_DEED_BACKEND is unset.
# Set GHOST_DEED_BACKEND=http://localhost:3001 to route deeds through the
# backend for server-side signing + Nostr relay publishing.
ghost_deed_post_backend() {
  local event_json="$1"
  [[ -z "${GHOST_DEED_BACKEND:-}" ]] && return 0
  command -v curl &>/dev/null || return 0

  local http_code
  http_code=$(curl --silent --max-time 5 \
    -X POST "${GHOST_DEED_BACKEND}/ghost-deed" \
    -H "Content-Type: application/json" \
    -d "$event_json" \
    --write-out '%{http_code}' \
    --output /dev/null 2>&1)
  if [[ "$http_code" != "200" ]]; then
    echo "[ghostdeed] WARN: backend ingest failed (backend=${GHOST_DEED_BACKEND}  http_status=${http_code})" >&2
  fi
}

# ── Main entry: build, journal, and optionally publish ────────────────────────
ghost_deed_post() {
  local event_json
  event_json=$(ghost_deed_build)

  # Sign the event if GHOST_NOSTR_NSEC + nak are available
  event_json=$(ghost_deed_sign "$event_json")

  # Always write to local journal (ephemeral — wiped with Ghost on exit)
  ghost_deed_journal "$event_json"

  # Option 1: POST to deed-ledger backend (signs + publishes server-side)
  ghost_deed_post_backend "$event_json"

  # Option 2: Direct relay publish via websocat (skips if backend is configured)
  [[ -z "${GHOST_DEED_BACKEND:-}" ]] && ghost_deed_publish "$event_json"

  echo "[ghostdeed] Deed posted  stage=${GHOST_STAGE:-dormant}  mask=${GHOST_MASK:-none}  cycles=${GHOST_CYCLES:-0}"
}

# ── Cleanup: remove journal on Ghost exit ─────────────────────────────────────
ghost_deed_cleanup() {
  [[ -f "$GHOST_DEED_JOURNAL" ]] && rm -f "$GHOST_DEED_JOURNAL"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  ghost_deed_post
fi
