<!--
Auto-prepared disclosure body for shareAI-lab/learn-claude-code.
The audit workflow's GITHUB_TOKEN cannot file issues on third-party
repos, so this body sits here pending manual filing:

  gh issue create --repo shareAI-lab/learn-claude-code \
    --title 'Security findings in executable artifacts' \
    --body-file auditor/disclosures-pending/shareAI-lab-learn-claude-code.md

After filing, record the URL with:
  jq '.repos["shareAI-lab/learn-claude-code"] += {disclosure_url: "<URL>", disclosure_filed_at: "<ISO8601>", disclosure_filed_by: "manual"}' \
    auditor/registry/repos.json > /tmp/r.json && mv /tmp/r.json auditor/registry/repos.json
-->

## Security Findings in Executable Artifacts

While auditing NL programming artifacts in this repository, our scanner detected potential security issues in executable files.

### Findings

| # | Severity | File | Line | Pattern | Description |
|---|----------|------|------|---------|-------------|
| 1 | High | agents/s01_agent_loop.py | 70 | SEC-shell-true | `subprocess.run(command, shell=True)` passes LLM-generated command strings directly to the shell. Pattern is architectural and present in all 13 agent files (s01–s12, s_full) and 2 reference scripts. |
| 2 | High | agents/s01_agent_loop.py | 66 | SEC-shell-true | Blocklist-only mitigation (`["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]`) is trivially bypassed: `rm -rf / ` (trailing space), `sudo sh`, `rm -rf /*`, bypassed `> /dev/sda` variants, etc. Provides false sense of security. |

### About This Report

These findings come from [NLPM](https://github.com/xiaolai/nlpm-for-claude)'s security scanner, which checks executable surfaces (hooks, scripts, MCP configs, dependencies) against known-dangerous patterns.

We may be wrong — false positives happen. If any finding is intentional or already mitigated, please close this issue. If a finding is genuine and you'd like a fix PR, let us know.

Full audit report: https://github.com/xiaolai/nlpm-for-claude/blob/main/auditor/audits/shareAI-lab-learn-claude-code.md
