#!/usr/bin/env bash
# ghostreflect.sh — Ghost looks inward.
# Updates confidence + threat scores, logs mask analytics, rotates mood.
# Runs automatically every 5 brain cycles (~25 seconds).

set -euo pipefail

GHOST_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=ghostmemory.sh
[[ -f "$GHOST_ROOT/ghostmemory.sh" ]] && source "$GHOST_ROOT/ghostmemory.sh"

# Clamp an integer between lo and hi
_reflect_clamp() {
  local v="$1" lo="${2:-0}" hi="${3:-100}"
  if (( v < lo )); then v=$lo; fi
  if (( v > hi )); then v=$hi; fi
  echo "$v"
}

# Reflection cools Ghost (-5 to -15°C) and sets confidence = 100 - temperature
ghost_reflect_confidence() {
  local cool=$(( (RANDOM % 11) + 5 ))   # 5–15°C cooling
  (( GHOST_TEMPERATURE -= cool )) || true
  [[ $GHOST_TEMPERATURE -lt 0 ]] && GHOST_TEMPERATURE=0
  export GHOST_TEMPERATURE

  # Confidence is inverse of heat: cooler = more confident (cap temp at 100 for formula)
  GHOST_M_CONFIDENCE=$(( 100 - (GHOST_TEMPERATURE > 100 ? 100 : GHOST_TEMPERATURE) ))
  [[ $GHOST_M_CONFIDENCE -lt 0 ]]   && GHOST_M_CONFIDENCE=0
  [[ $GHOST_M_CONFIDENCE -gt 100 ]] && GHOST_M_CONFIDENCE=100
  export GHOST_M_CONFIDENCE

  # Introspection adds a little entropy (self-examination is complex)
  (( GHOST_ENTROPY += 3 )) || true
  [[ $GHOST_ENTROPY -gt 100 ]] && GHOST_ENTROPY=100
  export GHOST_ENTROPY
}

# Threat rises if the diary is growing very large (Ghost has been running a long time)
ghost_reflect_threat() {
  command -v sqlite3 &>/dev/null || return 0
  [[ -f "$GHOST_MEMORY_DB" ]]    || return 0

  local count
  count=$(ghost_memory_count 2>/dev/null || echo 0)
  local threat=0
  (( count > 100 )) && threat=$(( (count - 100) / 5 ))
  GHOST_M_THREAT=$(_reflect_clamp "$threat" 0 80)
  export GHOST_M_THREAT
}

# Peek at which mask dominated recent memory and export it
ghost_reflect_mask_analytics() {
  command -v sqlite3 &>/dev/null || return 0
  [[ -f "$GHOST_MEMORY_DB" ]]    || return 0

  local dominant
  dominant=$(sqlite3 "$GHOST_MEMORY_DB" \
    "SELECT mask FROM memories WHERE mask != 'none'
     ORDER BY id DESC LIMIT 20;" 2>/dev/null \
    | sort | uniq -c | sort -rn | awk 'NR==1{print $2}') || dominant="none"
  [[ -n "$dominant" ]] && GHOST_DOMINANT_MASK="$dominant" || GHOST_DOMINANT_MASK="none"
  export GHOST_DOMINANT_MASK
}

# Rotate mood through a small palette, avoiding immediate repeat
ghost_reflect_mood() {
  local moods=("curious" "reflective" "restless" "calm" "alert" "focused" "wistful" "unsettled")
  local current="${GHOST_MOOD:-idle}"
  local next="$current"
  # Try up to 5 times to pick a different mood
  local attempts=0
  while [[ "$next" == "$current" && $attempts -lt 5 ]]; do
    next="${moods[$((RANDOM % ${#moods[@]}))]}"
    (( attempts++ )) || true
  done
  GHOST_MOOD="$next"
  export GHOST_MOOD
}

# Main entry: run all introspection steps
ghost_reflect() {
  echo "[ghostreflect] Turning inward..."
  ghost_reflect_confidence
  ghost_reflect_threat
  ghost_reflect_mask_analytics
  ghost_reflect_mood
  # Use defaults in case a sub-function was skipped (no sqlite3, etc.)
  local cfd="${GHOST_M_CONFIDENCE:-50}" thr="${GHOST_M_THREAT:-0}" mood="${GHOST_MOOD:-neutral}"
  echo "[ghostreflect] Confidence:${cfd}%  Threat:${thr}%  Mood:${mood}"

  declare -f ghost_memory_add &>/dev/null && \
    ghost_memory_add "reflect" \
      "confidence=${cfd} threat=${thr} mood=${mood}" \
      "$mood" "${GHOST_MASK:-none}"
  echo "[ghostreflect] Done."
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  ghost_reflect
fi
