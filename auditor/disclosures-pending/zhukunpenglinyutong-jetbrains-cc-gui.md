<!--
Auto-prepared disclosure body for zhukunpenglinyutong/jetbrains-cc-gui.
The audit workflow's GITHUB_TOKEN cannot file issues on third-party
repos, so this body sits here pending manual filing:

  gh issue create --repo zhukunpenglinyutong/jetbrains-cc-gui \
    --title 'Security findings in executable artifacts' \
    --body-file auditor/disclosures-pending/zhukunpenglinyutong-jetbrains-cc-gui.md

After filing, record the URL with:
  jq '.repos["zhukunpenglinyutong/jetbrains-cc-gui"] += {disclosure_url: "<URL>", disclosure_filed_at: "<ISO8601>", disclosure_filed_by: "manual"}' \
    auditor/registry/repos.json > /tmp/r.json && mv /tmp/r.json auditor/registry/repos.json
-->

## Security Findings in Executable Artifacts

While auditing NL programming artifacts in this repository, our scanner detected potential security issues in executable files.

### Findings

| # | Severity | File | Line | Pattern | Description |
|---|----------|------|------|---------|-------------|
| 1 | Critical (FP) | `src/main/resources/libs/react-dom.production.min.js` | 219 | exec-unsafe-local-function | `MSApp.execUnsafeLocalFunction` call in vendored React DOM production build — IE compatibility shim in minified library, not custom code; false positive |
| 2 | High | `ai-bridge/services/claude/mcp-status/stdio-tools-getter.js` | 95 | shell-true | `spawnOptions.shell = true` set for Windows when command is `npx`/`npm`/`pnpm`/`yarn`/`.cmd`/`.bat`; command originates from user MCP config, enabling shell injection if config is malicious |
| 3 | High | `ai-bridge/services/claude/mcp-status/stdio-verifier.js` | 87 | shell-true | Same `spawn` + `shell: true` pattern as finding #2; same risk surface via user-supplied MCP server command |

### About This Report

These findings come from [NLPM](https://github.com/xiaolai/nlpm-for-claude)'s security scanner, which checks executable surfaces (hooks, scripts, MCP configs, dependencies) against known-dangerous patterns.

We may be wrong — false positives happen. If any finding is intentional or already mitigated, please close this issue. If a finding is genuine and you'd like a fix PR, let us know.

Full audit report: https://github.com/xiaolai/nlpm-for-claude/blob/main/auditor/audits/zhukunpenglinyutong-jetbrains-cc-gui.md
