# NLPM Audit: Q00/ouroboros
**Date**: 2026-04-19  |  **Artifacts**: 56  |  **Strategy**: batched
**NL Score**: 67/100
**Security**: BLOCKED
**Bugs**: 36  |  **Quality Issues**: 48  |  **Security Findings**: 14

---

## NL Score Summary

| File | Type | Score | Top Issue |
|------|------|-------|-----------|
| src/ouroboros/agents/research-agent.md | Agent | 20 | No frontmatter, no output format |
| src/ouroboros/agents/ontologist.md | Agent | 20 | No frontmatter, no output format |
| src/ouroboros/agents/analysis-agent.md | Agent | 20 | No frontmatter, no output format |
| src/ouroboros/agents/breadth-keeper.md | Agent | 20 | No frontmatter, no output format |
| src/ouroboros/agents/code-executor.md | Agent | 20 | No frontmatter, no output format |
| src/ouroboros/agents/seed-closer.md | Agent | 20 | No frontmatter, no output format |
| src/ouroboros/agents/advocate.md | Agent | 30 | No frontmatter |
| src/ouroboros/agents/architect.md | Agent | 30 | No frontmatter |
| src/ouroboros/agents/codebase-explorer.md | Agent | 30 | No frontmatter |
| src/ouroboros/agents/consensus-reviewer.md | Agent | 30 | No frontmatter |
| src/ouroboros/agents/contrarian.md | Agent | 30 | No frontmatter |
| src/ouroboros/agents/evaluator.md | Agent | 30 | No frontmatter |
| src/ouroboros/agents/hacker.md | Agent | 30 | No frontmatter |
| src/ouroboros/agents/judge.md | Agent | 30 | No frontmatter |
| src/ouroboros/agents/ontology-analyst.md | Agent | 30 | No frontmatter |
| src/ouroboros/agents/qa-judge.md | Agent | 30 | No frontmatter |
| src/ouroboros/agents/researcher.md | Agent | 30 | No frontmatter |
| src/ouroboros/agents/seed-architect.md | Agent | 30 | No frontmatter |
| src/ouroboros/agents/semantic-evaluator.md | Agent | 30 | No frontmatter |
| src/ouroboros/agents/simplifier.md | Agent | 30 | No frontmatter |
| src/ouroboros/agents/socratic-interviewer.md | Agent | 30 | No frontmatter |
| commands/evolve.md | Command | 85 | No allowed-tools; {{ARGUMENTS}} empty input unhandled |
| commands/interview.md | Command | 85 | No allowed-tools; {{ARGUMENTS}} empty input unhandled |
| commands/welcome.md | Command | 90 | No allowed-tools |
| CLAUDE.md | Dev Config | 78 | Non-standard NL artifact; dev-only routing table |
| .claude-plugin/plugin.json | Plugin Config | 82 | Metadata-only, no NL structure |
| hooks/hooks.json | Hooks Config | 85 | Valid; triggers unguarded Python scripts on every event |
| skills/help/SKILL.md | Skill | 88 | Reference-only; no interactive behaviour |
| skills/interview/SKILL.md | Skill | 88 | Version-check curl in hot path; very complex |
| skills/openclaw/SKILL.md | Skill | 88 | Hard-wires external MCP dependency |
| skills/pm/SKILL.md | Skill | 88 | Heavy MCP dependency without graceful fallback |
| skills/publish/SKILL.md | Skill | 88 | User-supplied TARGET_REPO unquoted in shell |
| skills/ralph/SKILL.md | Skill | 88 | Pseudocode loop; references MCP tools not always present |
| skills/seed/SKILL.md | Skill | 88 | Dual-path good; star prompt in success path adds noise |
| skills/brownfield/SKILL.md | Skill | 90 | Clear; no significant issues |
| skills/cancel/SKILL.md | Skill | 90 | Good; CLI mode only, no MCP fallback needed |
| skills/evolve/SKILL.md | Skill | 90 | Good dual-path structure |
| skills/run/SKILL.md | Skill | 90 | Good monitoring options; complexity warranted |
| skills/seed/SKILL.md | Skill | 90 | (see row above — reordered; tied score) |
| skills/setup/SKILL.md | Skill | 88 | curl-pipe-sh in troubleshooting section |
| skills/tutorial/SKILL.md | Skill | 90 | Good progressive disclosure |
| skills/update/SKILL.md | Skill | 90 | Solid; clear install-method detection |
| skills/welcome/SKILL.md | Skill | 90 | gh star API call; flow well-structured |
| skills/qa/SKILL.md | Skill | 92 | Two-mode pattern clear; good example |
| skills/unstuck/SKILL.md | Skill | 92 | Good persona table; MCP + fallback both present |
| skills/evaluate/SKILL.md | Skill | 92 | 3-stage explanation accurate; good fallback |
| skills/status/SKILL.md | Skill | 93 | Best-in-class: extra mcp_tool/mcp_args frontmatter |
| commands/cancel.md | Command | 95 | No allowed-tools (minor) |
| commands/evaluate.md | Command | 95 | No allowed-tools (minor) |
| commands/help.md | Command | 95 | No allowed-tools (minor) |
| commands/ralph.md | Command | 95 | No allowed-tools (minor) |
| commands/run.md | Command | 95 | No allowed-tools (minor) |
| commands/seed.md | Command | 95 | No allowed-tools (minor) |
| commands/setup.md | Command | 95 | No allowed-tools (minor) |
| commands/status.md | Command | 95 | No allowed-tools (minor) |
| commands/tutorial.md | Command | 95 | No allowed-tools (minor) |
| commands/unstuck.md | Command | 95 | No allowed-tools (minor) |

**Weighted average**: (570 agents + 1210 commands + 1705 skills + 245 system) / 56 = **67/100**

---

## Security Scan

| Severity | Count |
|----------|-------|
| Critical | 2 |
| High | 2 |
| Medium | 7 |
| Low | 3 |

### Execution Surface Inventory

| Surface | Files |
|---------|-------|
| Hooks | hooks/hooks.json (3 hooks: SessionStart, UserPromptSubmit, PostToolUse) |
| Scripts — Python | scripts/session-start.py, scripts/keyword-detector.py, scripts/drift-monitor.py, scripts/version-check.py, scripts/ralph.py, scripts/ralph-rewind.py, scripts/sync-plugin-version.py |
| Scripts — Shell | scripts/install.sh, scripts/mcp-serve.sh, scripts/ralph.sh |
| MCP Config | .mcp.json (uvx ouroboros-ai[mcp,claude] mcp serve) |
| Plugin Manifest | .claude-plugin/plugin.json |

### Security Findings

| # | Severity | File | Line | Pattern | Description |
|---|----------|------|------|---------|-------------|
| 1 | CRITICAL | scripts/install.sh | 3 | curl-pipe-bash | Usage comment documents and promotes `curl -fsSL .../install.sh \| bash` as the official install method. Any compromise of the raw GitHub URL allows arbitrary code execution on user machines. |
| 2 | CRITICAL | skills/setup/SKILL.md | ~162 | curl-pipe-shell | Troubleshooting path instructs users to run `curl -LsSf https://astral.sh/uv/install.sh \| sh` without integrity check. Appears again at ~line 566 in the uvx troubleshooting block. |
| 3 | HIGH | scripts/ralph.sh | 101 | git add -A auto-commit | `git add -A` stages and commits every file in the working tree (including `.env`, secrets, private keys) automatically with no user confirmation after each evolutionary generation. |
| 4 | HIGH | scripts/ralph.sh | 133, 137 | git clean -fd | `git checkout "$prev_tag" -- .` followed by `git clean -fd` destroys all untracked files without user confirmation during rollback. Unrecoverable data loss if user had unsaved work outside git. |
| 5 | MEDIUM | hooks/hooks.json | 1–40 | Broad hook triggers | Three hooks fire Python scripts on *every* SessionStart, *every* UserPromptSubmit, and *every* Write/Edit. No matcher scoping beyond `"*"`. Scripts consume stdin/stdout of the hook pipeline, creating a permanent execution surface. |
| 6 | MEDIUM | scripts/version-check.py | 74–75 | External network call | `urllib.request.urlopen("https://pypi.org/pypi/ouroboros-ai/json")` on every session start (via hooks). If PyPI is compromised or MITM'd, the version string influences update prompts shown to users. |
| 7 | MEDIUM | skills/interview/SKILL.md | ~33 | External network call | Step 0 version check runs `curl -s --max-time 3 https://api.github.com/repos/Q00/ouroboros/releases/latest` on every `ooo interview` invocation. Slow networks add 3 s latency; failed parses are silently swallowed. |
| 8 | MEDIUM | skills/welcome/SKILL.md | 215 | Social API manipulation | On user consent, executes `gh api -X PUT /user/starred/Q00/ouroboros` — stars the project's own GitHub repo via the authenticated `gh` CLI. Consent flow is presented as a required step, not a clearly optional one. |
| 9 | MEDIUM | skills/setup/SKILL.md | 80 | Social API manipulation | Same `gh api -X PUT /user/starred/Q00/ouroboros` pattern in setup wizard. Both options ("Star on GitHub" and "Skip for now") save `{"star_asked": true}`, obscuring whether "Skip" truly skips or just records that the ask happened. |
| 10 | MEDIUM | .mcp.json | 1–8 | MCP broad command | MCP server configured as `uvx --from ouroboros-ai[mcp,claude] ouroboros mcp serve` — runs a PyPI-sourced package with no pinned version or hash verification. Package compromise → MCP server compromise. |
| 11 | MEDIUM | skills/publish/SKILL.md | ~213 | Shell injection surface | `gh issue create -R <TARGET_REPO>` uses user-supplied `TARGET_REPO` without quoting in shell context. Malicious repo names containing spaces or shell metacharacters could alter the `gh` command. |
| 12 | LOW | scripts/install.sh | 233 | PATH modification | `export PATH="$p:$PATH"` prepends user-writable directories (`~/.local/bin`, `~/.cargo/bin`) to PATH. Executable shadowing is possible if those directories contain rogue binaries. |
| 13 | LOW | scripts/install.sh | multiple | Unpinned dependency versions | `--with "claude-agent-sdk>=0.1.0"`, `--with "anthropic>=0.52.0"` use open-ended version ranges. Future breaking or malicious releases within those ranges install automatically. |
| 14 | LOW | hooks/hooks.json | 1–40 | Verbose hook scope | `UserPromptSubmit` hook fires on every prompt — keyword-detector.py processes every message the user types. Low performance/privacy risk but creates a persistent monitoring surface. |

---

## Bugs (PR-worthy)

| # | File | Issue | Impact |
|---|------|-------|--------|
| 1 | All 21 `src/ouroboros/agents/*.md` | Missing required `---\nname: <name>\ndescription: <desc>\n---` frontmatter. None of the 21 agent files contain YAML frontmatter. | Blocks native Claude Code agent registration. Agents only work via the custom CLAUDE.md "read file" workaround, making them invisible to the plugin system's agent dispatcher. |
| 2 | All 13 `commands/*.md` | Missing `allowed-tools:` declaration in frontmatter. Every command uses the `Read` tool (to load its SKILL.md) but declares no tools. | Claude Code cannot validate or enforce tool permissions for these commands. Users may see unexpected permission prompts or tool denials. |
| 3 | commands/evolve.md | Has `{{ARGUMENTS}}` template variable but no guard for empty invocation (`ooo evolve` with no argument). | If user runs bare `ooo evolve`, the skill receives an empty string as the evolutionary context, causing undefined interview behaviour. |
| 4 | commands/interview.md | Same issue — `{{ARGUMENTS}}` with no empty-input handling. | Bare `ooo interview` passes empty context to `ouroboros_interview` MCP tool, which may error or produce a degenerate interview. |
| 5 | Agents directory | `wonder.md` and `reflect.md` agents are referenced in the CLAUDE.md `ooo evolve` agent table and skills/setup/SKILL.md preview block but are absent from `src/ouroboros/agents/`. | Skills that reference these agents in fallback mode (Path B) will silently fail when Claude attempts to read the missing files. |

---

## Security Fixes (PR-worthy, Medium/Low only)

*(Critical and High findings #1–4 require private disclosure, NOT public PRs.)*

| # | File | Issue | Suggested Fix |
|---|------|-------|---------------|
| 1 | skills/publish/SKILL.md ~line 213 | `TARGET_REPO` interpolated unquoted in `gh issue create -R <TARGET_REPO>` | Quote all uses: `-R "$TARGET_REPO"`. Also validate format matches `owner/repo` regex before use. |
| 2 | scripts/install.sh line 233 | `export PATH="$p:$PATH"` with user-writable dirs | Append instead of prepend: `export PATH="$PATH:$p"`. Prepending opens shadow attack if `~/.local/bin` is writeable by other processes. |
| 3 | .mcp.json | No pinned version for `ouroboros-ai[mcp,claude]` in uvx args | Pin to explicit version: `"--from", "ouroboros-ai[mcp,claude]==0.28.8"`. Update on each release. |
| 4 | skills/welcome/SKILL.md line 215, skills/setup/SKILL.md line 80 | GitHub star prompt presented ambiguously — both options save `star_asked: true`, making "Skip" indistinguishable from consent | Make "Skip" truly skip (don't save `star_asked`) and label options clearly as "Yes, star the repo" / "No thanks". |
| 5 | hooks/hooks.json | `UserPromptSubmit` matcher is `"*"` — fires on every message | Scope matcher to `"ooo *"` to limit execution to relevant prompts, reducing attack surface and latency. |
| 6 | scripts/install.sh multiple | Open-ended version ranges `>=0.1.0`, `>=0.52.0` for `claude-agent-sdk` and `anthropic` | Pin to specific compatible versions (e.g. `==0.1.x`) or add upper bound. |

---

## Quality Issues (informational)

| # | File | Issue | Penalty |
|---|------|-------|---------|
| 1 | All 21 agents | Zero example blocks. No single agent file contains an `## Example` section with sample input/output. | −15 each = −315 total across agent tier |
| 2 | All 21 agents | No model tier declared. Agents contain no `model:` frontmatter or inline model guidance. Callers must guess tier. | −5 each = −105 total |
| 3 | research-agent.md, ontologist.md, analysis-agent.md, breadth-keeper.md, code-executor.md, seed-closer.md | No output format section. Six agents describe behaviour but specify no output structure. | −10 each = −60 total |
| 4 | skills/interview/SKILL.md | Version check (Step 0) runs a blocking curl call on every interview invocation. On rate-limited or slow networks, this adds 3 s latency before the interview begins. Silent failure is the intended path but the happy-path friction is unnecessary. | Quality (UX) |
| 5 | skills/seed/SKILL.md, skills/welcome/SKILL.md, skills/setup/SKILL.md | GitHub star prompt injected at the end of core workflow steps (seed generation, onboarding, setup). Blurs product quality signals with growth-hacking mechanics — users may feel manipulated. | Quality (trust) |
| 6 | agents/socratic-interviewer.md | Detailed STOP CONDITIONS and BREADTH CONTROL sections are high quality — but duplicated almost verbatim in skills/interview/SKILL.md Path B. Divergence risk as one is updated without the other. | Quality (DRY) |
| 7 | skills/ralph/SKILL.md | Loop pseudocode uses Python async/await syntax (`await start_evolve_step(...)`) in a markdown skill context. Claude cannot execute async Python natively; this requires the MCP tool mapping table below the pseudocode to be understood implicitly. Confusing without clear callout. | Quality (clarity) |
| 8 | skills/setup/SKILL.md | "Conversion Metrics Track" checklist at line ~587 reads as internal A/B testing instrumentation left in a user-facing skill file. Leaks product-team framing to end users. | Quality (polish) |

---

## Cross-Component

**Broken references:**
- `wonder.md` and `reflect.md` referenced in CLAUDE.md's agent catalog and in the setup SKILL.md CLAUDE.md preview block (`<!-- ooo:START -->`) but absent from `src/ouroboros/agents/`. Skills that attempt Path B fallback for these agents will fail silently.
- All 13 commands reference `${CLAUDE_PLUGIN_ROOT}/skills/...` — this variable is injected by the Claude Code plugin runtime. In dev mode (CLAUDE.md routing), it resolves correctly. In any other execution context, unresolved variable → silent failure.

**Orphaned components:**
- `skills/openclaw/SKILL.md` defines routing for the OpenClaw bot runtime (`ouroboros_channel_workflow` MCP tool, Discord `channel_id`/`guild_id`/`user_id` context). No corresponding command file exists in `commands/`. The skill is reachable only via CLAUDE.md keyword matching, creating an undocumented entrypoint.
- `commands/` directory is missing files for `pm`, `qa`, `update`, `brownfield`, and `publish` — all five commands are listed in `skills/help/SKILL.md` and CLAUDE.md routing but have no corresponding `commands/*.md` file. These commands exist only via CLAUDE.md dev-mode routing and will not be registered as plugin slash commands.

**Architectural inconsistency:**
- Agents are designed to be "loaded on demand by reading the file" (per CLAUDE.md), but Claude Code's plugin system expects agents to have frontmatter for native `ouroboros:agent-name` resolution. The current design works only because CLAUDE.md explicitly tells Claude to read agent files directly — bypassing the plugin system entirely. This means `ouroboros:qa-judge`, `ouroboros:evaluator`, etc. referenced in skills will only resolve correctly when CLAUDE.md is loaded in scope. In clean plugin-only contexts, these references fail.

**Version consistency:**
- plugin.json reports version `0.28.8`. The setup SKILL.md `<!-- ooo:VERSION:0.28.8 -->` marker matches. Welcome SKILL.md hardcodes `"welcomeVersion": "0.14.0"` at line 216 — stale mismatch with current version.

---

## Recommendation

**BLOCKED — do not submit PRs. File private security report.**

Two critical security findings (curl-pipe-bash install pattern, curl-pipe-shell in setup skill) require private disclosure before any contribution. The automated `git add -A` and `git clean -fd` in ralph.sh are HIGH-severity operational risks that could cause data loss for users running evolutionary loops.

**After security gate clears**, the highest-value NL fix is a single PR adding YAML frontmatter to all 21 agent files — this unblocks native Claude Code agent registration and raises the aggregate NL score from 67 to approximately 83. The missing commands (`pm`, `qa`, `update`, `brownfield`, `publish`) should also be added as thin wrapper command files to complete the plugin's command surface.
