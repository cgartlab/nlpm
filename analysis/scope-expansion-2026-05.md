# NLPM Scope Expansion Plan

> **Status**: proposal as of 2026-05-11.
> **Premise**: `analysis/ecosystem-gap.md` — NLPM uniquely covers manifest-vs-disk consistency. Make that uniqueness usable.
> **Non-goal**: a tiered probe ("ship Phase 1, see if it sticks"). This plan is the full target state, sequenced.

---

## 1. Frame: who NLPM serves, today and going forward

NLPM currently serves **two audiences** with full machinery:

| Audience | Mode | Surface |
|---|---|---|
| **Researchers / rule authors** (us) | Auditor mode | GHA workflows, rule-health, case studies, suppressions |
| **In-tree consumers** (this repo, the marketplace siblings) | Local slash commands | `/nlpm:ls`, `/nlpm:score`, `/nlpm:check`, `/nlpm:fix`, `/nlpm:test`, `/nlpm:security-scan` |

It is **not yet** built for the audience the research points to: **plugin/skill authors elsewhere** who want to ship clean artifacts. The slash commands work for them in theory, but the *path from "I'm authoring a plugin" to "NLPM is part of my workflow"* is undocumented, undistributed, and has no native integration with the author's actual lifecycle (commit, push, publish, maintain).

The expansion is structural: add a third audience and the supporting surface — without compromising the other two.

### The three audiences after expansion

| # | Audience | What they want | What they don't want |
|---|---|---|---|
| 1 | **Plugin/skill author** (new) | "Tell me before I push that my plugin is broken" | A research tool; opaque scoring; lectures |
| 2 | **Marketplace curator / consumer** | "Is this plugin safe and complete?" | Manual repo-by-repo inspection |
| 3 | **Researcher / rule author** (us) | "Which rules survive contact with reality?" | Tooling that drifts from how the ecosystem actually authors |

The three reinforce each other: more authors using NLPM means cleaner artifacts in the corpus, which means clearer rule signal, which means better defaults for the next author. The auditor mode keeps running; the corpus stays the differentiator.

---

## 2. Audience 1 — plugin/skill author

This is the new surface. Six integration points form the author's lifecycle. Each one needs a first-class NLPM answer.

### 2.1 Scaffolding (new plugin, new component)

**Goal**: prevent the manifest-vs-disk bug class **at creation**, not at audit.

The bug exists because creating a SKILL.md file is decoupled from registering it in `plugin.json`. Make them one operation.

Deliverables:
- `/nlpm:new` — orchestrator that asks "skill | command | agent | hook" and dispatches
- `/nlpm:new-skill <name>` — creates `skills/<name>/SKILL.md` with valid frontmatter AND atomically updates `plugin.json` skills array
- `/nlpm:new-command <name>` — same pattern for commands
- `/nlpm:new-agent <name>` — same pattern for agents
- All four refuse to run unless the target path is unambiguous (canonical layout detected, or `plugin.json` already present)
- Templates live at `templates/skill-skeleton.md`, `templates/command-skeleton.md`, `templates/agent-skeleton.md` — minimum-viable artifacts that already pass `/nlpm:score` at ≥85

Definition of done:
- Running `/nlpm:new-skill foo` in an empty plugin directory produces a plugin that passes `/nlpm:check` AND `/nlpm:score ≥85` without further edits.

### 2.2 Editing (in-IDE feedback)

**Goal**: surface the most actionable findings while the author is editing, not after they push.

Two delivery channels, ordered by reach:

1. **Hook-driven advisory** (already exists; expand). The current `scripts/check-artifact.sh` PostToolUse hook classifies a written file and emits an advisory. Expand it to also run a fast subset of `/nlpm:check` on the *plugin manifest* whenever any artifact is written. Findings stream as additionalContext.
2. **No LSP, no MCP server.** Both add maintenance surface for marginal benefit when the hook path already exists. Document the hook + slash-command flow as the canonical author UX; revisit if multiple authors ask for it.

Deliverables:
- Hook expansion: when SKILL.md / agent / command is written, run a 1-second manifest-diff and emit either "registered ✓" or "not in plugin.json — run `/nlpm:new-skill` next time, or add manually"
- Document the hook UX clearly in `docs/for-authors/editing.md`

### 2.3 Committing (pre-commit)

**Goal**: the bad commit doesn't land. This is the "loud failure" that the ecosystem currently lacks.

Deliverables:
- `templates/pre-commit-nlpm.sh` — a copy-pasteable hook that runs `/nlpm:check` on the repo and fails (exit 1) on confidence-high findings
- `templates/pre-commit-config.yaml` — drop-in for `pre-commit` framework users
- README section in this repo + `docs/for-authors/pre-commit.md` showing installation in 3 lines

The hook script does NOT shell out to Claude Code. It runs a standalone Python script (`bin/nlpm-check`) that implements the manifest-vs-disk diff directly. The slash command goes through the agent; the standalone binary is the same logic without the agent, suitable for CI. Both produce identical output.

Definition of done:
- `bin/nlpm-check` is a pure-Python script (no external deps) that runs `<2s` on a 50-file plugin
- Exit code 0 (pass) / 1 (high-confidence findings) / 2 (errors) — scriptable
- The pre-commit hook template installs with `curl -sSL .../install-pre-commit.sh | sh` (linked from README; not auto-piped — authors paste it themselves)

### 2.4 Pushing (GitHub Actions on PR)

**Goal**: the same loud failure runs on every PR, regardless of whether the author installed the pre-commit hook.

Deliverables:
- `.github/workflows/nlpm-check.yml` template at `templates/workflows/nlpm-check.yml`
- One-line annotation in the workflow showing how to opt into auto-fix PRs (`/nlpm:fix` style) for mechanical findings
- README example: copy this file into your plugin repo, commit, done

Definition of done:
- The template uses no secrets; no GITHUB_TOKEN write scope unless auto-fix is enabled
- Runs on `pull_request` and `push` to default branch
- Produces a GHA annotation on each finding (file + line + rule number + fix suggestion)

### 2.5 Publishing (pre-marketplace gate)

**Goal**: don't publish a plugin that fails `/nlpm:check`.

This is `bin/nlpm-check --strict` — same binary, stricter exit policy (any finding of any confidence fails). Authors invoke from their `npm publish` / release-please / manual-publish script.

Deliverables:
- Document `bin/nlpm-check --strict` in `docs/for-authors/publishing.md`
- A "publish checklist" template (markdown checkbox list) authors can copy into their release process

Definition of done:
- A maintainer can wire `bin/nlpm-check --strict` into their release process in <5 minutes from cold start
- Failure output is human-readable, not JSONL

### 2.6 Maintenance (recurring validation)

**Goal**: catch drift over time. Spec changes; an author's plugin that passed in March may fail in June because the spec extended.

Deliverables:
- `.github/workflows/nlpm-weekly.yml` template — scheduled cron, opens an issue if `/nlpm:check` flags new findings vs. the last green run
- Document in `docs/for-authors/maintenance.md`

This piggybacks on NLPM's existing `auditor-docs-diff.yml` infrastructure — the author opts into the same spec-drift surface NLPM uses internally.

Definition of done:
- An author opts in by committing the workflow; nothing else
- The workflow's issue body cites the specific spec URL that changed (using NLPM's `docs-citations.json` if available)

### 2.7 Diagnostics (when something breaks)

**Goal**: an author hitting a runtime issue can run one command and get a triage report.

Deliverables:
- `/nlpm:diagnose` — runs `/nlpm:ls` + `/nlpm:check` + `/nlpm:security-scan` and produces a single combined report with explicit "this is what's broken, in priority order"
- `bin/nlpm-diagnose` — standalone variant for non-Claude-Code users

This is the entry point a frustrated author runs. Make it work cold.

---

## 3. Audience 2 — marketplace curators / consumers

Curators run NLPM against repos they don't own to decide what to feature. Consumers run it against a plugin before installing.

### 3.1 The "Validated by NLPM" badge

Not a vanity label. A SHA-stamped attestation that a specific commit of a specific plugin passed `/nlpm:check`, with a link to the report.

Deliverables:
- `nlpm-check --emit-attestation` produces a JSON file with: repo SHA, NLPM version, score, finding count, signature (in-toto-compatible if straightforward; otherwise just SHA256 of the report)
- `templates/workflows/nlpm-attest.yml` — publishes the attestation to GitHub Pages on the plugin's own repo
- README badge spec: `![Validated by NLPM](https://img.shields.io/badge/dynamic/json?...)` that reads the latest attestation

Definition of done:
- A plugin can display the badge on its README; clicking it shows the latest passing attestation
- A consumer can verify the badge isn't fake by checking the attestation against the SHA in the badge URL

### 3.2 Read-only consumer tool

A consumer who finds an unfamiliar plugin can run `/nlpm:assess <github-url>` and get the same audit report NLPM produces internally — without contributing PRs.

Deliverables:
- `/nlpm:assess <repo-url-or-path>` — the read-only variant of the audit workflow
- Output: score, top 5 findings, security flag, manifest-vs-disk diff if any
- Documented in `docs/for-consumers.md`

This already exists in pieces (the audit workflow logic). Package it as a user-invocable command.

---

## 4. Audience 3 — researchers / rule authors (us)

This is where NLPM started, and where it continues. The expansion **must not** compromise this surface.

What stays the same:
- All auditor workflows (`.github/workflows/auditor-*.yml`)
- The append-only logs (`findings.jsonl`, `disagreements.jsonl`, `events.jsonl`)
- The rule-health query
- The human-gated rule-refinement PR flow
- All `/nlpm:*` slash commands

What changes:
- The corpus grows richer. Author-side adoption produces a cleaner baseline against which auditor findings become more meaningful.
- The case-study writer gets a new genre: not "NLPM caught a bug in repo X" but "repo Y adopted NLPM and avoided the bug class entirely." Different evidence, same loop.
- Suppressions become a more interesting dataset: authors using NLPM will configure rule overrides, and the suppression scanner already surfaces those.

---

## 5. Packaging strategy

The expansion changes NLPM from "a Claude Code plugin" to "a Claude Code plugin **and** a standalone toolkit." Two artifacts, one repo.

### 5.1 The slash commands stay

The plugin form (slash commands, agents, skills) is the right surface for **in-Claude-Code authoring**. It stays.

### 5.2 The standalone binary is new

`bin/nlpm-check`, `bin/nlpm-diagnose`, `bin/nlpm-attest` are pure Python (Python 3.11+ since it's already on every developer machine and on every GHA Ubuntu runner). No external deps; stdlib only. Distributed as a single-file script + a `setup.py` for pip install.

Why a binary and not a slash command for CI:
- Slash commands require Claude Code installed; CI runners don't have it
- Pre-commit hooks need synchronous exit codes; agents are async
- A standalone binary is auditable (one Python file) and the manifest-vs-disk check itself is mechanical, not LLM-mediated

### 5.3 The agent stays for the heavyweight work

The `scorer` and `checker` agents continue to be the right tool for full 100-point scoring and judgment-required findings. The binary handles the deterministic subset (manifest-vs-disk, frontmatter validation, missing-required-field detection); the agent handles the rest.

Split rule:
- **Mechanical → binary.** Manifest diff, JSON syntax, frontmatter parse, naming convention, file existence.
- **Judgment → agent.** Description quality, vague-quantifier flags, instruction clarity, semantic consistency.

Both surfaces share the same rule numbers (R01-R50). The binary implements a subset; the agent covers the full set.

---

## 6. Ecosystem positioning

The research surfaced eight other validators. NLPM's positioning needs to be explicit, not implicit. The README and `docs/positioning.md` answer three questions:

| Question | Answer |
|---|---|
| "Why not just use the official Anthropic plugin-validator?" | "It doesn't check manifest-vs-disk consistency. Run both; we don't compete." |
| "Why not use the Linux Foundation skills-ref?" | "Use it for skill-level frontmatter; use NLPM for plugin-level cross-component consistency. Different scopes." |
| "Why not use one of the third-party validators?" | "Use them if they fit your need. NLPM's differentiator is the cross-component diff and the audit corpus." |

The positioning is **complementary, not competitive**. NLPM runs *alongside* the official validator. The README explicitly recommends running both. This matters: if Anthropic ships manifest-vs-disk in `plugin-validator` later, NLPM's positioning shifts to "the corpus and the rule-evolution loop," which is the actual differentiator long-term.

---

## 7. Discovery strategy

A tool that no one finds is a tool that no one uses. Three channels, ranked:

### 7.1 GHA template (highest leverage)

Authors copy GHA workflows from other plugins' repos. If 5-10 NLPM case-study repos commit `.github/workflows/nlpm-check.yml`, the workflow propagates by imitation. Cost: zero per propagation.

Action: when NLPM ships a case-study PR going forward, include the NLPM GHA workflow alongside the fix. Maintainers can take or leave it; if they take it, future authors looking at the repo see it.

### 7.2 README badge

Same propagation mechanism. A badge on a high-star repo's README is seen by every visitor.

Action: offer the badge as part of the case-study PR. Documented, opt-in.

### 7.3 Linked from the docs-citation index

The `auditor/docs-citations.json` file lists every primary source NLPM cites. The reverse — being cited from those sources — is harder, but worth a shot.

Action: file PRs against the Anthropic plugin docs and the Linux Foundation skills repo recommending NLPM for cross-component validation. Maintainer-judgment-dependent; low cost to try.

What we explicitly do NOT do:
- No paid promotion. No Twitter/X campaign. No "growth hacks." The case-study PR is the marketing.
- No `npm publish` of an unrelated tool to grab the namespace.
- No SEO blogspam. The `analysis/` directory and case studies are the corpus that ranks naturally.

---

## 8. Spec-drift contract

The Agent Skills spec is six months old. It will evolve. NLPM's promise is to track the evolution without surprising users.

The contract (already 80% implemented via v0.7.31):
- Every rule that cites a spec URL is registered in `auditor/docs-citations.json`
- The weekly `auditor-docs-diff.yml` workflow hashes the URLs and opens an issue on diff
- A quarterly `auditor-rule-review.yml` workflow forces human-review of all rules
- Rule changes ship via PR; the rule-refinement workflow opens the PR but never merges

What's missing:
- A public commitment in the README: "NLPM's rules are versioned. Breaking rule changes ship in minor versions (0.X.0 → 0.(X+1).0); fixes ship as patches."
- A `CHANGELOG.md` at the repo root with a clear rule-change column

Deliverables:
- README: explicit spec-drift contract section
- CHANGELOG: rule changes called out per release
- Migration guide template: when a rule changes, the changelog entry includes "to migrate, run `/nlpm:fix` against your repo"

---

## 9. Maintenance burden — what NOT to build

To be comprehensive about scope, name what's excluded.

| Excluded | Reason |
|---|---|
| LSP server | Marginal benefit over the hook + slash-command UX; high maintenance cost; no author has requested it |
| Web playground / hosted scoring | Drives traffic but not adoption; pre-commit + GHA is the right surface for action |
| VS Code extension | Same as LSP — the hook already covers the editing path |
| Standalone language port (Rust, Go) | Python script is portable enough; multi-language ports fragment effort |
| Marketplace clone / "NLPM-blessed" registry | Conflicts with audience 2 positioning; the badge is enough |
| Custom CI provider (drone, circle) | GHA covers 90% of plugin repos; document GHA, link to community contributions for the rest |

These exclusions are durable. The plan is to revisit them only if multiple specific authors request a specific item, with a stated use case.

---

## 10. Metrics — what "expansion worked" means

The metrics are real-world adoption, not vanity. Cadence: snapshot quarterly.

| Metric | Source | Success threshold (12-month) |
|---|---|---|
| External plugins committing `.github/workflows/nlpm-check.yml` | GitHub code search | 25+ |
| External plugins with NLPM badge in README | GitHub code search | 10+ |
| External plugins running pre-commit hook (detected via .pre-commit-config.yaml) | GitHub code search | 15+ |
| `bin/nlpm-check` invocations per week (if telemetry is added — currently NOT planned) | n/a | n/a |
| Audit-corpus repos that already pass `/nlpm:check` clean on first scan | NLPM's own registry | 20% of new discoveries |
| Rule-health: rules with ≥10 verified findings (mature signal) | `rule-health.py` | 15+ rules |
| Case studies where the repo's author actively adopted NLPM after the PR | manual review | 5+ |

What's NOT in the metrics:
- GitHub stars on this repo
- Discord/community count
- "Reach" or "impressions"
- Number of slash-command invocations in this repo

These are noise. The 6 metrics above are causal evidence that the expansion served the audience.

---

## 11. Sequencing

The plan is comprehensive. Execution is sequenced to deliver useful intermediate states.

**Sequencing principles**:
1. Foundations first — anything that depends on the standalone binary needs the binary before it can ship.
2. One audience at a time — fully serve audience 1 (authors) before adding curator/consumer surface for audience 2.
3. Each step ships independently usable; no "you need step 7 to use step 3" coupling.

**Sequence**:

| Order | Deliverable | Depends on |
|---|---|---|
| 1 | `bin/nlpm-check` standalone binary (manifest-vs-disk + frontmatter) | nothing |
| 2 | Pre-commit hook template + install doc | step 1 |
| 3 | GHA workflow template (`nlpm-check.yml`) | step 1 |
| 4 | `/nlpm:new-skill`, `/nlpm:new-command`, `/nlpm:new-agent` scaffolders | nothing (slash commands only) |
| 5 | Hook expansion (manifest diff on every artifact write) | step 1 |
| 6 | Author docs (`docs/for-authors/{editing,pre-commit,push,publishing,maintenance,diagnostics}.md`) | steps 1-5 |
| 7 | `/nlpm:diagnose` orchestrator | nothing |
| 8 | "Validated by NLPM" attestation + badge | step 1 |
| 9 | `/nlpm:assess <url>` consumer tool | nothing (refactor of existing audit logic) |
| 10 | Weekly drift workflow template | step 1 |
| 11 | README rewrite with ecosystem positioning | steps 1-10 |
| 12 | Spec-drift contract section + CHANGELOG.md | nothing |
| 13 | Case-study PR template that includes the GHA workflow + badge | step 8 |

Each step is 0.5-2 days of work. Total: ~3 weeks of focused work to reach the full target state.

**Versioning**:
- Steps 1-3 ship as **v0.8.0** — minor bump marks the scope expansion start
- Step 4-7 ship as **v0.8.x** patches
- Steps 8-13 ship as **v0.9.0** — minor bump marks the curator surface + ecosystem positioning
- The auditor mode continues operating throughout; no auditor work is paused for this

---

## 12. Risks, named

1. **Anthropic adds the check to `plugin-validator`.** Already discussed in `ecosystem-gap.md`. The differentiator becomes the corpus, not the check. Mitigation: ship now, while we're first; cite NLPM in the case studies.

2. **The standalone binary diverges from the agent rubric.** Two implementations of "what NLPM checks." Mitigation: a single rule registry (the existing `nlpm:scoring` skill) is read by both; the binary implements the deterministic subset and explicitly delegates the rest with "run `/nlpm:score` for full analysis."

3. **Author adoption is slower than expected.** Possible. Mitigation: the case-study PR is the marketing; if 12 months produce 25 GHA workflows committed externally, that's success. If 5, we revisit.

4. **Maintenance burden grows.** Three artifacts (slash commands, agent, binary) to keep in sync. Mitigation: shared rule registry; CI test that runs the binary against this repo's own artifacts; weekly drift check.

5. **Scope creep within "for authors."** The natural next ask is "also add ___." Mitigation: section §9 ("what NOT to build") is the durable answer. Revisit only with a concrete author + use case.

---

## 13. The decision the user makes now

Three options:

1. **Approve the plan as written.** Start step 1 (`bin/nlpm-check`) immediately. Ship intermediate state at each step boundary.
2. **Approve with edits.** Identify which sections to cut/expand before execution.
3. **Reject and re-plan.** If the framing or scope is wrong, restart the strategy doc.

The plan above is sized at ~3 weeks of focused work to reach steady state. It is comprehensive — it covers all six lifecycle phases for audience 1, the curator surface for audience 2, the corpus continuity for audience 3, packaging, positioning, discovery, spec drift, exclusions, metrics, and sequencing — as the user explicitly requested.
