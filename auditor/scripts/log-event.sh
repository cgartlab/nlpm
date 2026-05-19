#!/bin/bash
# Append a structured JSON event to auditor/logs/events.jsonl
# Usage: source scripts/log-event.sh
#        log_event "discover" "search_complete" '{"candidates": 42, "new": 15}'
#        log_event "audit" "score_computed" '{"repo": "owner/name", "score": 74}'

log_event() {
  local workflow="$1"
  local event="$2"
  local data="$3"
  local timestamp
  timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local run_id="${GITHUB_RUN_ID:-local}"
  local run_num="${GITHUB_RUN_NUMBER:-0}"

  # Pipe data as stdin to jq — avoids all shell quoting issues with --argjson
  local json_data="${data}"
  [ -z "$json_data" ] && json_data='{}'

  # Ensure log dir exists before either jq attempt — prevents BOTH writes
  # from failing because the directory is missing on a fresh checkout.
  if ! mkdir -p auditor/logs 2>/dev/null; then
    echo "log-event: ERROR — could not create auditor/logs (event lost: $workflow/$event)" >&2
    return 1
  fi
  if ! command -v jq >/dev/null 2>&1; then
    echo "log-event: ERROR — jq not on PATH (event lost: $workflow/$event)" >&2
    return 1
  fi

  if printf '%s' "$json_data" | jq -c \
    --arg ts "$timestamp" \
    --arg wf "$workflow" \
    --arg ev "$event" \
    --arg rid "$run_id" \
    --arg rn "${run_num:-0}" \
    '{timestamp: $ts, workflow: $wf, event: $ev, run_id: $rid, run_number: ($rn | tonumber? // 0), data: .}' \
    >> auditor/logs/events.jsonl 2>/dev/null
  then
    echo "[$workflow] $event: $data"
    return 0
  fi

  # Fallback: data wasn't valid JSON, wrap as string
  if jq -cn \
    --arg ts "$timestamp" \
    --arg wf "$workflow" \
    --arg ev "$event" \
    --arg rid "$run_id" \
    --arg rn "${run_num:-0}" \
    --arg d "$json_data" \
    '{timestamp: $ts, workflow: $wf, event: $ev, run_id: $rid, run_number: ($rn | tonumber? // 0), data: {raw: $d}}' \
    >> auditor/logs/events.jsonl
  then
    echo "[$workflow] $event: $data (data raw-wrapped)"
    return 0
  fi

  echo "log-event: ERROR — both jq writes failed (event lost: $workflow/$event)" >&2
  return 1
}

# Commit log entries (call at end of workflow)
commit_logs() {
  git config user.name "nlpm-auditor[bot]"
  git config user.email "nlpm-auditor[bot]@users.noreply.github.com"
  git add auditor/logs/events.jsonl
  git diff --cached --quiet || {
    git commit -m "log: $(date +%Y-%m-%d) $1"
    git push
  }
}
