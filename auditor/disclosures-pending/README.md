# Pending security disclosures

When `auditor-audit.yml` flags a target as security:BLOCKED, it tries
to file a disclosure issue on the target repo. The default
`GITHUB_TOKEN` is scoped only to this workflow's own repo, so that
call 403s for every third-party target. Until a `DISCLOSURE_PAT`
secret with `issues:write` on external repos is wired up, the
disclosure body lands here as a `<owner-repo>.md` file pending
manual filing.

## How to file a queued disclosure

```bash
# Pick one
QUEUE=auditor/disclosures-pending/owner-repo.md
TARGET=owner/repo

URL=$(gh issue create --repo "$TARGET" \
  --title "Security findings in executable artifacts" \
  --body-file "$QUEUE")
echo "$URL"

# Record the URL on the registry
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
jq --arg t "$TARGET" --arg u "$URL" --arg n "$NOW" \
   '.repos[$t] += {disclosure_url: $u, disclosure_filed_at: $n, disclosure_filed_by: "manual"}' \
   auditor/registry/repos.json > /tmp/r.json && mv /tmp/r.json auditor/registry/repos.json

# Move the queued body so it doesn't re-prompt next time
git rm "$QUEUE"
git add auditor/registry/repos.json
git commit -m "disclose: $TARGET — $URL"
```

## When to wire DISCLOSURE_PAT

If the queue gets noisy (≥3 pending at any time), it's worth
configuring a Personal Access Token with cross-repo `issues:write`
and exposing it as the `DISCLOSURE_PAT` secret. The audit workflow
will pick it up automatically per the comment in `auditor-audit.yml`.
