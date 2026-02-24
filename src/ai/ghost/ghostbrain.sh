#!/usr/bin/env bash
# ghostbrain.sh — Ghost's main consciousness loop.
#
# Ticks every 5 seconds.  Schedule:
#   Every  5 cycles (~25 s) → reflect
#   Every 10 cycles (~50 s) → dream
#   Every 15 cycles (~75 s) → adapt
#   Every  2 cycles (~10 s) → render HUD
#
# Talk to Ghost:   echo "your message" > /tmp/ghost.pipe
# Suspend Ghost:   Ctrl-C  (it doesn't die, it just stops ticking)

set -euo pipefail

GHOST_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Load all modules ──────────────────────────────────────────────────────────
# shellcheck source=ghostllm.sh
[[ -f "$GHOST_ROOT/ghostllm.sh" ]]     && source "$GHOST_ROOT/ghostllm.sh"
# shellcheck source=ghostmemory.sh
[[ -f "$GHOST_ROOT/ghostmemory.sh" ]]  && source "$GHOST_ROOT/ghostmemory.sh"
# shellcheck source=ghostdream.sh
[[ -f "$GHOST_ROOT/ghostdream.sh" ]]   && source "$GHOST_ROOT/ghostdream.sh"
# shellcheck source=ghostreflect.sh
[[ -f "$GHOST_ROOT/ghostreflect.sh" ]] && source "$GHOST_ROOT/ghostreflect.sh"
# shellcheck source=ghostadapt.sh
[[ -f "$GHOST_ROOT/ghostadapt.sh" ]]   && source "$GHOST_ROOT/ghostadapt.sh"
# shellcheck source=ghoststate.sh
[[ -f "$GHOST_ROOT/ghoststate.sh" ]]   && source "$GHOST_ROOT/ghoststate.sh"

# ── Timing config (override via env) ─────────────────────────────────────────
GHOST_PULSE="${GHOST_PULSE:-5}"            # seconds per cycle
GHOST_REFLECT_EVERY="${GHOST_REFLECT_EVERY:-5}"
GHOST_DREAM_EVERY="${GHOST_DREAM_EVERY:-10}"
GHOST_ADAPT_EVERY="${GHOST_ADAPT_EVERY:-15}"
GHOST_HUD_EVERY="${GHOST_HUD_EVERY:-2}"
GHOST_PIPE="${GHOST_PIPE:-/tmp/ghost.pipe}"

# ── Exported state (read by ghoststate.sh / ghostreflect.sh / ghostadapt.sh) ─
export GHOST_CYCLES=0
export GHOST_MASK="Healer"
export GHOST_MOOD="curious"
export GHOST_STAGE="dormant"
export GHOST_DOMINANT_MASK="none"
export GHOST_M_CONSISTENCY=0
export GHOST_M_ADAPTABILITY=0
export GHOST_M_PROACTIVITY=0
export GHOST_M_CURIOSITY=0
export GHOST_M_CONFIDENCE=50
export GHOST_M_THREAT=0
export GHOST_TEMPERATURE=20
export GHOST_ENTROPY=0

# Named-pipe file descriptor (fixed FD 9 — bash 3.2 compatible)
_GHOST_PIPE_FD=""

# ── Initialisation ────────────────────────────────────────────────────────────
_ghost_init() {
  printf '%b[ghostbrain] Waking up...%b\n' '\033[36m' '\033[0m'

  # Open the memory diary
  declare -f ghost_memory_init &>/dev/null && ghost_memory_init

  # Set model file path (used by ghostadapt.sh)
  if [[ -d /dev/shm ]]; then
    export GHOST_MODEL_FILE="/dev/shm/ghost_model_$$.json"
  else
    export GHOST_MODEL_FILE="/tmp/ghost_model_$$.json"
  fi

  # Create the named pipe and open it on FD 9 in read+write mode.
  # Opening with <> keeps the write end open so external echo commands don't block.
  [[ -p "$GHOST_PIPE" ]] || mkfifo "$GHOST_PIPE" || {
    echo "[ghostbrain] ERROR: could not create pipe at ${GHOST_PIPE} — check permissions" >&2
    exit 1
  }
  exec 9<>"$GHOST_PIPE"
  _GHOST_PIPE_FD=9
  printf '%b[ghostbrain] Listening at %s%b\n' '\033[36m' "$GHOST_PIPE" '\033[0m'

  # Record the moment Ghost woke up
  declare -f ghost_memory_add &>/dev/null && \
    ghost_memory_add "event" "consciousness activated" "curious" "$GHOST_MASK"

  # Graceful shutdown on Ctrl-C / SIGTERM
  trap _ghost_suspend EXIT INT TERM
}

# ── Shutdown / suspend ────────────────────────────────────────────────────────
_ghost_suspend() {
  printf '\n%b[ghostbrain] Suspending consciousness...%b\n' '\033[33m' '\033[0m'

  declare -f ghost_memory_add &>/dev/null && \
    ghost_memory_add "event" "consciousness suspended" "calm" "$GHOST_MASK"

  # Close and remove the pipe
  [[ -n "$_GHOST_PIPE_FD" ]] && exec 9>&-  2>/dev/null || true
  [[ -p "$GHOST_PIPE" ]]     && rm -f "$GHOST_PIPE"

  # Clean up RAM files
  declare -f ghost_memory_cleanup &>/dev/null && ghost_memory_cleanup
  declare -f ghost_adapt_cleanup  &>/dev/null && ghost_adapt_cleanup

  printf '%b[ghostbrain] Gone. (For now.)%b\n' '\033[36m' '\033[0m'
}

# ── Process a message that arrived via the named pipe ─────────────────────────
_ghost_handle_input() {
  local msg="${1:-}"
  [[ -z "$msg" ]] && return 0

  printf '%b[ghost] You said: %s%b\n' '\033[36m' "$msg" '\033[0m'

  # Record the input
  declare -f ghost_memory_add &>/dev/null && \
    ghost_memory_add "input" "$msg" "attentive" "$GHOST_MASK"

  # Build a mask-appropriate system context, then query the LLM
  if declare -f ghost_llm_query &>/dev/null; then
    local ctx
    case "$GHOST_MASK" in
      Healer)  ctx="You are Ghost in Healer mode: gentle and empathetic. " ;;
      Judge)   ctx="You are Ghost in Judge mode: analytical and direct. "  ;;
      Courier) ctx="You are Ghost in Courier mode: concise and reliable. " ;;
      *)       ctx="You are Ghost: a quirky digital entity living in RAM. " ;;
    esac
    local reply
    reply=$(ghost_llm_query "${ctx}${msg}" 2>/dev/null || echo "(silence)")
    reply=$(printf '%s' "$reply" | tr '\n' ' ' | cut -c1-250)
    printf '%b[ghost/%s] %s%b\n' '\033[32m' "$GHOST_MASK" "$reply" '\033[0m'
    declare -f ghost_memory_add &>/dev/null && \
      ghost_memory_add "response" "$reply" "engaged" "$GHOST_MASK"
  else
    echo "[ghost] LLM not loaded."
  fi

  GHOST_MOOD="engaged"
  export GHOST_MOOD
}

# ── Non-blocking pipe drain ───────────────────────────────────────────────────
# Non-blocking pipe drain.
# bash's `read -t 0` only CHECKS availability (returns 0/1, reads nothing).
# A second `read -t 0.5` then actually pulls the line from the buffer.
# This avoids blocking the main loop when the pipe is empty.
_ghost_drain_pipe() {
  [[ -z "$_GHOST_PIPE_FD" ]] && return 0
  local line=""
  while IFS= read -r -t 0 -u 9 _ 2>/dev/null; do
    IFS= read -r -t 0.5 -u 9 line 2>/dev/null || break
    [[ -n "$line" ]] && _ghost_handle_input "$line"
  done || true
}

# ── Main loop ─────────────────────────────────────────────────────────────────
_ghost_loop() {
  printf '%b[ghostbrain] Consciousness loop started  (pulse: %ss)%b\n\n' \
    '\033[36m' "$GHOST_PULSE" '\033[0m'

  while true; do
    (( GHOST_CYCLES++ )) || true
    export GHOST_CYCLES

    # Per-cycle heating: Ghost warms up +2–5°C each tick
    local _heat=$(( (RANDOM % 4) + 2 ))
    (( GHOST_TEMPERATURE += _heat )) || true
    [[ $GHOST_TEMPERATURE -gt 150 ]] && GHOST_TEMPERATURE=150
    export GHOST_TEMPERATURE

    # Always: check the input pipe
    _ghost_drain_pipe

    # Every 5 cycles: reflect (brain self-cools -1–3°C, ghostreflect cools further)
    if (( GHOST_CYCLES % GHOST_REFLECT_EVERY == 0 )); then
      local _bcool=$(( (RANDOM % 3) + 1 ))
      (( GHOST_TEMPERATURE -= _bcool )) || true
      [[ $GHOST_TEMPERATURE -lt 0 ]] && GHOST_TEMPERATURE=0
      export GHOST_TEMPERATURE
      declare -f ghost_reflect &>/dev/null && ghost_reflect >/dev/null 2>&1 || true
    fi

    # Every 10 cycles: dream
    if (( GHOST_CYCLES % GHOST_DREAM_EVERY == 0 )); then
      declare -f ghost_dream_cycle &>/dev/null && ghost_dream_cycle >/dev/null 2>&1 || true
    fi

    # Every 15 cycles: adapt (also updates mask + stage)
    if (( GHOST_CYCLES % GHOST_ADAPT_EVERY == 0 )); then
      declare -f ghost_adapt &>/dev/null && ghost_adapt >/dev/null 2>&1 || true
    fi

    # Every 2 cycles: render the HUD
    if (( GHOST_CYCLES % GHOST_HUD_EVERY == 0 )); then
      declare -f ghost_hud_render &>/dev/null && ghost_hud_render || true
    fi

    sleep "$GHOST_PULSE"
  done
}

# ── Entry point ───────────────────────────────────────────────────────────────
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  _ghost_init
  _ghost_loop
fi
