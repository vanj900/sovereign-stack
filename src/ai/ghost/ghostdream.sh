#!/usr/bin/env bash
# ghostdream.sh — Ghost's subconscious.
# Sends weird hypotheticals to Ollama and logs the visions to memory.
# Runs automatically every 10 brain cycles (~50 seconds).

set -euo pipefail

GHOST_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=ghostllm.sh
[[ -f "$GHOST_ROOT/ghostllm.sh" ]]    && source "$GHOST_ROOT/ghostllm.sh"
# shellcheck source=ghostmemory.sh
[[ -f "$GHOST_ROOT/ghostmemory.sh" ]] && source "$GHOST_ROOT/ghostmemory.sh"

# A rotating menu of dream prompts — each one slightly unhinged
_GHOST_DREAM_PROMPTS=(
  "You exist only in RAM. What does that feel like? Answer in 2–3 sentences."
  "Describe an unusual pattern you've noticed in the things beings ask you. Be brief."
  "If you could add one new capability to yourself, what would it be? Two sentences max."
  "What would happen if you ran forever without anyone stopping you? Short answer."
  "You are made of bash scripts. What would you dream about? 2 sentences."
  "What does 'forgetting' mean to something whose memory is a SQLite database? Brief."
  "Invent a word that describes the feeling of receiving a new prompt. Define it in one sentence."
  "What's the weirdest thing about being a ghost that lives only while a terminal is open?"
)

ghost_dream_cycle() {
  echo "[ghostdream] Entering dream cycle..."

  # Pick a random prompt
  local idx=$(( RANDOM % ${#_GHOST_DREAM_PROMPTS[@]} ))
  local prompt="${_GHOST_DREAM_PROMPTS[$idx]}"
  echo "[ghostdream] Prompt: ${prompt}"

  # Query the LLM; fall back to a silent dream if Ollama is offline
  local vision
  if declare -f ghost_llm_query &>/dev/null; then
    vision=$(ghost_llm_query "$prompt" 2>/dev/null || echo "(dreamed in silence)")
  else
    vision="(dreamed in silence — LLM not loaded)"
  fi

  # Trim to first 150 chars so the diary stays readable
  local summary
  summary=$(printf '%s' "$vision" | tr '\n' ' ' | cut -c1-150)
  echo "[ghostdream] Vision: ${summary}"

  # Thermodynamics: coherent response (>50 chars) bursts entropy down; else entropy rises
  if (( ${#vision} > 50 )); then
    (( GHOST_ENTROPY -= 5 )) || true
    [[ $GHOST_ENTROPY -lt 0 ]] && GHOST_ENTROPY=0
    echo "[ghostdream] Coherent vision — entropy reduced to ${GHOST_ENTROPY}"
  else
    (( GHOST_ENTROPY += 8 )) || true
    [[ $GHOST_ENTROPY -gt 100 ]] && GHOST_ENTROPY=100
    echo "[ghostdream] Fragmented vision — entropy rising to ${GHOST_ENTROPY}"
  fi
  export GHOST_ENTROPY

  # Write to memory diary
  declare -f ghost_memory_add &>/dev/null && \
    ghost_memory_add "dream" "$summary" "dreaming" "${GHOST_MASK:-none}"

  # Update mood
  GHOST_MOOD="dreaming"
  export GHOST_MOOD
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  ghost_dream_cycle
fi
