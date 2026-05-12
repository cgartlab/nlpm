#!/usr/bin/env bash
# Atomic registry write with JSON validation.
#
# Call sites first run `jq ... > /tmp/reg.json` to produce the next state,
# then invoke this helper to validate-and-rename. If /tmp/reg.json fails
# to parse, the move is refused and the script exits non-zero so the
# caller's step fails loudly — preserving the original registry on disk.
#
# Why: on 2026-04-28 a registry corruption surfaced (Extra data after
# top-level close) that required manual repair. The corruption was
# already on disk by the time anyone noticed. Validating before rename
# turns silent-write-corruption into immediate-step-failure.
#
# Usage:
#   jq <filter> auditor/registry/repos.json > /tmp/reg.json && \
#     bash auditor/scripts/atomic-registry-write.sh
#
# Env (optional):
#   REG_TMP   override the staging path (default /tmp/reg.json)
#   REG_DEST  override the destination (default auditor/registry/repos.json)

set -euo pipefail

REG_TMP="${REG_TMP:-/tmp/reg.json}"
REG_DEST="${REG_DEST:-auditor/registry/repos.json}"

if [ ! -f "$REG_TMP" ]; then
  echo "ERROR: $REG_TMP not found — caller did not stage a write" >&2
  exit 1
fi

if ! python3 -m json.tool "$REG_TMP" > /dev/null 2>&1; then
  echo "ERROR: $REG_TMP is not valid JSON; refusing to overwrite $REG_DEST" >&2
  echo "       (the prior registry on disk is preserved)" >&2
  exit 1
fi

# `mv` across filesystems isn't atomic — on Linux runners /tmp is often
# tmpfs while the repo is ext4. Stage the rename inside the destination
# directory so the kernel does a same-filesystem rename(2), which IS
# atomic. Without this, a crash mid-mv could leave the registry as a
# partial copy.
REG_DEST_DIR=$(dirname "$REG_DEST")
mkdir -p "$REG_DEST_DIR"
STAGED_IN_DEST=$(mktemp "$REG_DEST_DIR/.repos.json.XXXXXX")
trap 'rm -f "$STAGED_IN_DEST"' EXIT
cp "$REG_TMP" "$STAGED_IN_DEST"
mv "$STAGED_IN_DEST" "$REG_DEST"
trap - EXIT
rm -f "$REG_TMP"
