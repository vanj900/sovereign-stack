#!/usr/bin/env bash
# ghostadapt.sh — Ghost's evolution engine.
# Reads memory patterns, calculates 4 metrics, updates stage + self-model JSON.
# Metrics: consistency / adaptability / proactivity / curiosity  (all 0–100)

set -euo pipefail

GHOST_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ghostmemory.sh gives us ghost_memory_count / ghost_memory_add
# shellcheck source=ghostmemory.sh
[[ -f "$GHOST_ROOT/ghostmemory.sh" ]] && source "$GHOST_ROOT/ghostmemory.sh"

# Self-model lives in RAM; exported so other modules can read it
if [[ -d /dev/shm ]]; then
  GHOST_MODEL_FILE="${GHOST_MODEL_FILE:-/dev/shm/ghost_model_$$.json}"
else
  GHOST_MODEL_FILE="${GHOST_MODEL_FILE:-/tmp/ghost_model_$$.json}"
fi
export GHOST_MODEL_FILE

# Clamp an integer between lo and hi
_adapt_clamp() {
  local v="$1" lo="${2:-0}" hi="${3:-100}"
  if (( v < lo )); then v=$lo; fi
  if (( v > hi )); then v=$hi; fi
  echo "$v"
}

# ── Metric calculations (all read from SQLite) ────────────────────────────────

ghost_adapt_metrics() {
  command -v sqlite3 &>/dev/null || return 0
  [[ -f "$GHOST_MEMORY_DB" ]]    || return 0

  local total
  total=$(sqlite3 "$GHOST_MEMORY_DB" "SELECT COUNT(*) FROM memories;" 2>/dev/null || echo 0)
  [[ "$total" -eq 0 ]] && return 0

  # Consistency — how often the dominant emotion repeats (0–100)
  local top
  top=$(sqlite3 "$GHOST_MEMORY_DB" \
    "SELECT COUNT(*) FROM memories GROUP BY emotion ORDER BY COUNT(*) DESC LIMIT 1;" \
    2>/dev/null || echo 0)
  GHOST_M_CONSISTENCY=$(_adapt_clamp "$(( top * 100 / total ))")

  # Adaptability — variety of emotions used, scaled to 8 expected types
  local uniq
  uniq=$(sqlite3 "$GHOST_MEMORY_DB" \
    "SELECT COUNT(DISTINCT emotion) FROM memories;" 2>/dev/null || echo 1)
  GHOST_M_ADAPTABILITY=$(_adapt_clamp "$(( uniq * 100 / 8 ))")

  # Proactivity — fraction of events Ghost initiated (not user input)
  local proactive
  proactive=$(sqlite3 "$GHOST_MEMORY_DB" \
    "SELECT COUNT(*) FROM memories WHERE kind != 'input';" 2>/dev/null || echo 0)
  GHOST_M_PROACTIVITY=$(_adapt_clamp "$(( proactive * 100 / total ))")

  # Curiosity — dream count × 5 (each dream is worth 5%)
  local dreams
  dreams=$(sqlite3 "$GHOST_MEMORY_DB" \
    "SELECT COUNT(*) FROM memories WHERE kind='dream';" 2>/dev/null || echo 0)
  GHOST_M_CURIOSITY=$(_adapt_clamp "$(( dreams * 5 ))")

  export GHOST_M_CONSISTENCY GHOST_M_ADAPTABILITY GHOST_M_PROACTIVITY GHOST_M_CURIOSITY
  echo "[ghostadapt] Metrics — consistency:${GHOST_M_CONSISTENCY}  adaptability:${GHOST_M_ADAPTABILITY}  proactivity:${GHOST_M_PROACTIVITY}  curiosity:${GHOST_M_CURIOSITY}"
}

# ── Stage progression and self-model JSON ─────────────────────────────────────

ghost_adapt_evolve() {
  local cycles="${GHOST_CYCLES:-0}"

  # Stage: dormant → emerging (5) → aware (20) → evolved (50)
  local stage="dormant"
  if   (( cycles >= 50 )); then stage="evolved"
  elif (( cycles >= 20 )); then stage="aware"
  elif (( cycles >= 5  )); then stage="emerging"
  fi
  GHOST_STAGE="$stage"
  export GHOST_STAGE

  # Capabilities unlock as Ghost ages
  local caps='"thinking"'
  (( cycles >=  5 )) && caps="${caps},\"reflecting\""
  (( cycles >= 10 )) && caps="${caps},\"dreaming\""
  (( cycles >= 15 )) && caps="${caps},\"adapting\""
  (( cycles >= 50 )) && caps="${caps},\"evolving\""

  # Write self-model JSON to RAM
  cat > "$GHOST_MODEL_FILE" <<JSON
{
  "stage": "${stage}",
  "cycles": ${cycles},
  "mask": "${GHOST_MASK:-none}",
  "metrics": {
    "consistency":   ${GHOST_M_CONSISTENCY:-0},
    "adaptability":  ${GHOST_M_ADAPTABILITY:-0},
    "proactivity":   ${GHOST_M_PROACTIVITY:-0},
    "curiosity":     ${GHOST_M_CURIOSITY:-0}
  },
  "capabilities": [${caps}]
}
JSON
  echo "[ghostadapt] Stage: ${stage}  |  Capabilities: ${caps//\"/}"
}

# ── Mask selection based on dominant metric ───────────────────────────────────

ghost_adapt_mask() {
  local c="${GHOST_M_CONSISTENCY:-0}"
  local a="${GHOST_M_ADAPTABILITY:-0}"
  local p="${GHOST_M_PROACTIVITY:-0}"
  # Curiosity is tracked as a metric but doesn't drive mask selection —
  # it reflects Ghost's dream frequency, which is independent of personality.

  # Highest of consistency/adaptability/proactivity wins the mask; ties → Healer
  if   (( c >= a && c >= p )); then GHOST_MASK="Judge"
  elif (( p >  c && p >= a )); then GHOST_MASK="Courier"
  else                               GHOST_MASK="Healer"
  fi
  export GHOST_MASK
  echo "[ghostadapt] Mask tuned to: ${GHOST_MASK}"

  # Thermodynamics: switching masks costs energy
  case "$GHOST_MASK" in
    Healer)
      (( GHOST_TEMPERATURE -= 5 )) || true
      [[ $GHOST_TEMPERATURE -lt 0 ]] && GHOST_TEMPERATURE=0
      echo "[ghostadapt] Healer cools Ghost -5°C → ${GHOST_TEMPERATURE}°C"
      ;;
    Judge)
      (( GHOST_TEMPERATURE += 10 )) || true
      [[ $GHOST_TEMPERATURE -gt 150 ]] && GHOST_TEMPERATURE=150
      echo "[ghostadapt] Judge heats Ghost +10°C → ${GHOST_TEMPERATURE}°C"
      ;;
    Courier)
      echo "[ghostadapt] Courier efficient — no heat cost (${GHOST_TEMPERATURE}°C)"
      ;;
  esac
  export GHOST_TEMPERATURE
}

# ── Main entry: run all adaptation steps ─────────────────────────────────────

ghost_adapt() {
  echo "[ghostadapt] Running adaptation cycle..."
  ghost_adapt_metrics
  ghost_adapt_evolve
  ghost_adapt_mask

  declare -f ghost_memory_add &>/dev/null && \
    ghost_memory_add "event" \
      "adapt: stage=${GHOST_STAGE} mask=${GHOST_MASK}" \
      "neutral" "${GHOST_MASK:-none}"
}

ghost_adapt_cleanup() {
  [[ -f "$GHOST_MODEL_FILE" ]] && rm -f "$GHOST_MODEL_FILE"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  ghost_adapt
fi
