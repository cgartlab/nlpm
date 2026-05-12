#!/bin/bash
# Validate feedback/log.json integrity before it's used for any decision.
# Catches corruption, hallucinated stats, and drift from reality.

LOG="auditor/feedback/log.json"

if [ ! -f "$LOG" ]; then
  echo "WARN: No feedback log found"
  exit 0
fi

ERRORS=0

# Check 1: Valid JSON
if ! jq empty "$LOG" 2>/dev/null; then
  echo "ERROR: feedback/log.json is not valid JSON"
  exit 1
fi

# Check 2: Required structure
for key in events rule_stats metadata; do
  if ! jq -e ".$key" "$LOG" >/dev/null 2>&1; then
    echo "ERROR: missing required key '$key'"
    ERRORS=$((ERRORS + 1))
  fi
done

# Check 3: Rule stats reference real rules. Accepted namespaces:
#   R01-R50    — primary numeric rules (from skills/nlpm/rules/)
#   BUG-*      — bug-class findings (manifest-vs-disk, frontmatter, etc.)
#   SEC-*      — security-pattern findings (curl-pipe-sh, eval-from-input)
#   CC-*       — cross-component consistency findings
# rule-health.py emits all four namespaces; the validator must accept all four.
# Numeric R-rules are strictly R01-R50 (no R00, no R51+) to prevent typos
# that would create silent untracked rules.
INVALID_RULES=$(jq -r '.rule_stats | keys[]' "$LOG" 2>/dev/null \
  | grep -vE '^(R(0[1-9]|[1-4][0-9]|50)|BUG-[a-z0-9-]+|SEC-[a-z0-9-]+|CC-[a-z0-9-]+)$' \
  || true)
if [ -n "$INVALID_RULES" ]; then
  echo "ERROR: feedback log references invalid rules: $INVALID_RULES"
  ERRORS=$((ERRORS + 1))
fi

# Check 4: Counts are non-negative integers
NEGATIVE=$(jq '[.rule_stats[].total_hits, .metadata.total_prs_submitted, .metadata.total_prs_merged, .metadata.total_prs_rejected] | map(select(. < 0)) | length' "$LOG" 2>/dev/null || echo 0)
if [ "$NEGATIVE" -gt 0 ]; then
  echo "ERROR: negative counts in feedback log"
  ERRORS=$((ERRORS + 1))
fi

# Check 5: merged + rejected <= submitted
SUBMITTED=$(jq '.metadata.total_prs_submitted // 0' "$LOG")
MERGED=$(jq '.metadata.total_prs_merged // 0' "$LOG")
REJECTED=$(jq '.metadata.total_prs_rejected // 0' "$LOG")
if [ $((MERGED + REJECTED)) -gt "$SUBMITTED" ]; then
  echo "ERROR: merged ($MERGED) + rejected ($REJECTED) > submitted ($SUBMITTED)"
  ERRORS=$((ERRORS + 1))
fi

if [ "$ERRORS" -gt 0 ]; then
  echo "FAILED: $ERRORS validation error(s)"
  exit 1
fi

echo "Feedback log valid: $SUBMITTED submitted, $MERGED merged, $REJECTED rejected"
exit 0
