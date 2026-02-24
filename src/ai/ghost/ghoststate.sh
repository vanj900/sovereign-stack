#!/usr/bin/env bash
# ghoststate.sh — Ghost's mind on display.
# Renders a live terminal HUD: masks, metrics, memories, and mood.
# Call ghost_hud_render any time you want to see what's going on inside.

set -euo pipefail

GHOST_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ghostmemory.sh provides ghost_memory_recent / ghost_memory_count
# shellcheck source=ghostmemory.sh
[[ -f "$GHOST_ROOT/ghostmemory.sh" ]] && source "$GHOST_ROOT/ghostmemory.sh"

# ── ANSI colour shortcuts ─────────────────────────────────────────────────────
_C_RST='\033[0m'
_C_BOLD='\033[1m'
_C_DIM='\033[2m'
_C_CYN='\033[36m'
_C_GRN='\033[32m'
_C_YLW='\033[33m'
_C_RED='\033[31m'
_C_MGT='\033[35m'
_C_BLU='\033[34m'

# Draw a filled progress bar  value 0–100, width in chars
_ghost_bar() {
  local val="${1:-0}" wid="${2:-20}" col="${3:-$_C_GRN}"
  local filled=$(( val * wid / 100 )) i
  printf '%b' "$col"
  for (( i=0; i<filled; i++ )); do printf '█'; done
  printf '%b' "$_C_DIM"
  for (( i=filled; i<wid; i++ )); do printf '░'; done
  printf '%b' "$_C_RST"
}

ghost_hud_render() {
  # Pull state from exported env vars written by ghostbrain/ghostadapt/ghostreflect
  local mask="${GHOST_MASK:-none}"
  local mood="${GHOST_MOOD:-idle}"
  local stage="${GHOST_STAGE:-dormant}"
  local cycles="${GHOST_CYCLES:-0}"
  local temp="${GHOST_TEMPERATURE:-20}"
  local entropy="${GHOST_ENTROPY:-0}"
  local mem_count
  mem_count=$(declare -f ghost_memory_count &>/dev/null && ghost_memory_count || echo "0")

  # Metrics (0–100 integers)
  local m_con="${GHOST_M_CONSISTENCY:-0}"
  local m_ada="${GHOST_M_ADAPTABILITY:-0}"
  local m_pro="${GHOST_M_PROACTIVITY:-0}"
  local m_cur="${GHOST_M_CURIOSITY:-0}"
  local m_cfd="${GHOST_M_CONFIDENCE:-50}"
  local m_thr="${GHOST_M_THREAT:-0}"

  # Pick colours for active mask
  local mask_col="$_C_CYN"
  case "$mask" in
    Healer)  mask_col="$_C_GRN" ;;
    Judge)   mask_col="$_C_RED" ;;
    Courier) mask_col="$_C_YLW" ;;
  esac

  # Pick colour for stage
  local stage_col="$_C_DIM"
  case "$stage" in
    emerging) stage_col="$_C_CYN" ;;
    aware)    stage_col="$_C_YLW" ;;
    evolved)  stage_col="$_C_MGT" ;;
  esac

  clear

  # Header
  printf '%b╔══════════════════════════════════════════════════╗%b\n' \
    "$_C_BOLD$_C_CYN" "$_C_RST"
  printf '%b║            ░ ░  G H O S T  ░ ░                  ║%b\n' \
    "$_C_BOLD$_C_CYN" "$_C_RST"
  printf '%b╚══════════════════════════════════════════════════╝%b\n\n' \
    "$_C_BOLD$_C_CYN" "$_C_RST"

  # Identity line
  printf '  %bMask%b    : %b%-10s%b  %bStage%b  : %b%s%b\n' \
    "$_C_BOLD" "$_C_RST" "$mask_col" "$mask" "$_C_RST" \
    "$_C_BOLD" "$_C_RST" "$stage_col" "$stage" "$_C_RST"
  printf '  %bMood%b    : %-10s  %bCycles%b : %s  %b(diary: %s)%b\n\n' \
    "$_C_BOLD" "$_C_RST" "$mood" \
    "$_C_BOLD" "$_C_RST" "$cycles" \
    "$_C_DIM"  "$mem_count" "$_C_RST"

  # 4 evolution metrics
  printf '  %bConsistency%b   '; _ghost_bar "$m_con" 20 "$_C_BLU"; printf '  %3d%%\n' "$m_con"
  printf '  %bAdaptability%b  '; _ghost_bar "$m_ada" 20 "$_C_GRN"; printf '  %3d%%\n' "$m_ada"
  printf '  %bProactivity%b   '; _ghost_bar "$m_pro" 20 "$_C_YLW"; printf '  %3d%%\n' "$m_pro"
  printf '  %bCuriosity%b     '; _ghost_bar "$m_cur" 20 "$_C_MGT"; printf '  %3d%%\n' "$m_cur"
  printf '\n'

  # Confidence / threat
  printf '  %bConfidence%b    '; _ghost_bar "$m_cfd" 20 "$_C_CYN"; printf '  %3d%%\n' "$m_cfd"
  printf '  %bThreat%b        '; _ghost_bar "$m_thr" 20 "$_C_RED"; printf '  %3d%%\n' "$m_thr"
  printf '\n'

  # Thermodynamic state
  local temp_bar=$(( temp > 100 ? 100 : temp ))
  local ent_disp
  if (( entropy >= 100 )); then
    ent_disp="1.00"
  else
    printf -v ent_disp "0.%02d" "$entropy"
  fi
  printf '  %bTemperature%b   '; _ghost_bar "$temp_bar" 20 "$_C_RED";  printf '  %3d°C\n' "$temp"
  printf '  %bEntropy%b       '; _ghost_bar "$entropy"  20 "$_C_YLW"; printf '  %s\n' "$ent_disp"
  if (( temp > 90 )); then
    printf '\n  %b⚠  HEAT DEATH RISK — temperature critical! Cool down immediately! ⚠%b\n' \
      "$_C_BOLD$_C_RED" "$_C_RST"
  fi
  printf '\n'

  # Recent memories
  printf '  %b── Recent Memories ──────────────────────────────%b\n' \
    "$_C_BOLD$_C_MGT" "$_C_RST"
  if declare -f ghost_memory_recent &>/dev/null; then
    local i=0
    while IFS= read -r line; do
      printf '  %b%s%b\n' "$_C_DIM" "$line" "$_C_RST"
      (( i++ )) || true
    done < <(ghost_memory_recent 5 2>/dev/null)
    [[ $i -eq 0 ]] && printf '  %b(no memories yet — still warming up)%b\n' "$_C_DIM" "$_C_RST"
  fi

  printf '\n  %bTalk%b: echo "..." > /tmp/ghost.pipe    %bCtrl-C%b to sleep\n' \
    "$_C_DIM" "$_C_RST" "$_C_DIM" "$_C_RST"
}

# Render once when run directly
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  ghost_hud_render
fi
