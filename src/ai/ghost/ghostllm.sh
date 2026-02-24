#!/usr/bin/env bash
# ghostllm.sh — Talks to Ollama. No API keys. No cloud. Pure local vibes.
# Requires: curl, jq (optional but recommended)

set -euo pipefail

GHOST_LLM_ENDPOINT="${GHOST_LLM_ENDPOINT:-http://localhost:11434/api/generate}"
GHOST_LLM_MODEL="${GHOST_LLM_MODEL:-llama3.2}"
GHOST_LLM_TIMEOUT="${GHOST_LLM_TIMEOUT:-30}"

ghost_llm_query() {
  local prompt="${1:?ghost_llm_query: prompt required}"
  local model="${2:-$GHOST_LLM_MODEL}"

  # Prefix prompt with current thermodynamic state
  local _temp="${GHOST_TEMPERATURE:-20}"
  local _ent_raw="${GHOST_ENTROPY:-0}"
  local _ent_disp
  printf -v _ent_disp "0.%02d" "$(( _ent_raw > 99 ? 99 : _ent_raw ))"
  prompt="You are operating at ${_temp}°C with entropy ${_ent_disp}. ${prompt}"

  # Build the JSON payload (prefer jq; fall back to sed-based escaping)
  local payload
  if command -v jq &>/dev/null; then
    payload=$(jq -nc \
      --arg m "$model" \
      --arg p "$prompt" \
      '{"model":$m,"prompt":$p,"stream":false}')
  else
    local ep em
    ep=$(printf '%s' "$prompt" | sed 's/\\/\\\\/g; s/"/\\"/g; s/	/\\t/g; s/$/\\n/' | tr -d '\n' | sed 's/\\n$//')
    em=$(printf '%s' "$model"  | sed 's/"/\\"/g')
    payload="{\"model\":\"${em}\",\"prompt\":\"${ep}\",\"stream\":false}"
  fi

  # Send to Ollama; return graceful placeholder if offline
  local raw
  raw=$(curl -s --fail --max-time "$GHOST_LLM_TIMEOUT" \
    -X POST "$GHOST_LLM_ENDPOINT" \
    -H "Content-Type: application/json" \
    -d "$payload" 2>/dev/null) || {
      echo "(ollama offline — dreaming alone)"
      return 0
    }

  # Pull out the .response field
  if command -v jq &>/dev/null; then
    printf '%s' "$raw" | jq -r '.response // "(no response)"'
  else
    printf '%s' "$raw" \
      | grep -o '"response":"[^"]*"' \
      | sed 's/"response":"//; s/"$//' \
      || echo "(parse error)"
  fi
}

# Run directly for a quick test
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  ghost_llm_query "${1:-Who are you, really?}"
fi
