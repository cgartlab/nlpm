<!--
Auto-prepared disclosure body for vercel-labs/agent-browser.
The audit workflow's GITHUB_TOKEN cannot file issues on third-party
repos, so this body sits here pending manual filing:

  gh issue create --repo vercel-labs/agent-browser \
    --title 'Security findings in executable artifacts' \
    --body-file auditor/disclosures-pending/vercel-labs-agent-browser.md

After filing, record the URL with:
  jq '.repos["vercel-labs/agent-browser"] += {disclosure_url: "<URL>", disclosure_filed_at: "<ISO8601>", disclosure_filed_by: "manual"}' \
    auditor/registry/repos.json > /tmp/r.json && mv /tmp/r.json auditor/registry/repos.json
-->

## Security Findings in Executable Artifacts

While auditing NL programming artifacts in this repository, our scanner detected potential security issues in executable files.

### Findings

| # | Severity | File | Line | Pattern | Description |
|---|----------|------|------|---------|-------------|
| 1 | HIGH | package.json | 25 | SEC-postinstall-script | `postinstall` lifecycle hook auto-runs `node scripts/postinstall.js` on every `npm install`; script downloads native binary over network and rewrites global bin entries |
| 2 | HIGH | scripts/postinstall.js | 258 | SEC-file-write-outside-repo | `symlinkSync` replaces the `agent-browser` symlink in npm global bin dir (`$npm_prefix/bin/`), a system PATH directory outside the repo |
| 3 | HIGH | scripts/postinstall.js | 301 | SEC-file-write-outside-repo | `writeFileSync` overwrites `.cmd` and `.ps1` shims in the Windows global npm prefix dir outside the package |

### About This Report

These findings come from [NLPM](https://github.com/xiaolai/nlpm-for-claude)'s security scanner, which checks executable surfaces (hooks, scripts, MCP configs, dependencies) against known-dangerous patterns.

We may be wrong — false positives happen. If any finding is intentional or already mitigated, please close this issue. If a finding is genuine and you'd like a fix PR, let us know.

Full audit report: https://github.com/xiaolai/nlpm-for-claude/blob/main/auditor/audits/vercel-labs-agent-browser.md
