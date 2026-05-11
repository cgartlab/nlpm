# The NL Artifact Ecosystem Gap

> **Stable reference.** Updated as the ecosystem shifts. Companion to the dated snapshot at `analysis/2026-05-11-why-obvious-bugs-persist.md` (the original research) and the scope-expansion plan at `analysis/scope-expansion-2026-05.md` (the response).
>
> **Last refreshed**: 2026-05-11.

## The gap, stated simply

The Claude Code plugin ecosystem has eight or more validators in active development. None of them, including Anthropic's official `plugin-validator` agent and the Linux Foundation's `skills-ref` reference library, systematically check **cross-component consistency** — the alignment between what a manifest declares and what exists on disk.

Every other major code ecosystem (TypeScript, Python, Rust, Ruby, Go) has at least one install-time or build-time gate that fails loudly on this class of inconsistency. The NL artifact ecosystem does not. As a result, high-reputation maintainers ship plugins where SKILL.md files exist on disk with valid frontmatter but are absent from the plugin manifest's `skills` array. Users installing the plugin get the registered subset; the rest are invisible.

NLPM's `/nlpm:check` is, by current research, the only validator that systematically catches this bug class.

## The validators that exist

### Official (Anthropic)

| Tool | What it covers | What it doesn't |
|---|---|---|
| `claude plugin validate` (built-in CLI) | Manifest JSON syntax + deprecation warnings | Manifest-vs-disk consistency, cross-references |
| `plugin-validator` agent (`anthropics/claude-code/plugins/plugin-dev/agents/`) | Per-component frontmatter; manifest fields; security (hardcoded creds, HTTPS); MCP config | **Manifest-vs-disk consistency** — explicitly absent from the documented checklist |

### Linux Foundation (Agentic AI Foundation)

| Tool | What it covers | What it doesn't |
|---|---|---|
| `agentskills` / `skills-ref` (CLI + Python + Rust crate) | Per-skill: frontmatter validity, `name == parent_dir`, naming conventions | Plugin-level concerns; the spec scope ends at the skill boundary |

### Third-party (varying adoption)

| Tool | Strengths | Coverage of manifest-vs-disk |
|---|---|---|
| `claude-plugin-validate` (Rust, situ2001) | Manifest JSON, frontmatter, hooks JSON; fast | **Not documented; minimal adoption (0 stars at time of survey)** |
| `agent-skill-linter` (William-Yeh) | Spec compliance, badges, LICENSE checks; auto-fix | **No** |
| `skill-check` (thedaviddias) | Structure, description quality, body limits, 0-100 scoring | **No** |
| `skill-validator` (agent-ecosystem) | **Pre-commit hooks for Claude/Copilot/etc.** Content density checks | **No** |
| `skill-md-validator` (louloulin) | Required YAML fields | **No** |
| `skill-linter` (majesticlabs-dev, RHEcosystemAppEng) | Marketplace gate logic | **No** |

### NLPM

| Tool | Coverage |
|---|---|
| `/nlpm:check` | Manifest-vs-disk, orphaned components, broken cross-references, `allowed-tools` vs call sites, terminology drift |
| `/nlpm:score` | 100-point quality scoring with per-rule penalties |
| `/nlpm:security-scan` | Executable surface scan (hooks, scripts, MCP, dependencies) |
| `/nlpm:fix` | Auto-fix mechanical issues |
| `/nlpm:test` | NL-TDD specs |

## Where the gap sits

The validators concentrate at the **single-artifact** boundary: does THIS SKILL.md have a valid `name`? does THIS plugin.json parse as JSON? At that layer, eight tools compete and any one of them catches what the others catch.

The validators avoid the **cross-artifact** boundary: does the array in plugin.json enumerate every SKILL.md on disk? Does every tool name in `allowed-tools` have a call site? Do cross-references resolve?

Cross-artifact validation requires reading two enumerations and diffing them. It's mechanically simple but architecturally different — a per-file linter can't do it without scanning the whole repo. That extra scope is, by hypothesis, why most validators stop at the file boundary.

## Why this class of bug ships in practice

From the NLPM audit corpus (199 repos audited, 36 case studies as of 2026-05-11):

| Repo | Stars | Manifest-vs-disk-class bug present | Existing local validator caught it? |
|---|---|---|---|
| safishamsi/graphify | 37k | Python SyntaxError in skill code block | No |
| kubesphere/kubesphere | 16k | 18 findings including duplicate sections, broken YAML | Partial (yaml-lint would have caught one) |
| tanweai/pua | 16k | TOCTOU race, path drift in protocol refs | No |
| agent-sh/agnix | 5k | Stale counts across sibling files | No |
| **mattpocock/skills** | **69k** | 4 unregistered SKILL.md files | **No — running the official Anthropic plugin-validator would pass** |

These are not sloppy maintainers. They are using the tools that exist for the layer those tools cover. The bugs ship because no tool catches the layer where they sit.

## Five compounding factors

1. **Right validator missing in canonical form.** Manifest-vs-disk isn't in the official Anthropic tool. Authors who reach for "the official validator" don't get this check.

2. **Discovery is broken.** Eight tools, no SEO winner, no GitHub Actions template that ships with `claude plugin init`. Authors don't know which tool to pick, so most pick none.

3. **The spec is young.** Anthropic published the Agent Skills spec on 2025-12-18. Within 48 hours, OpenAI/Microsoft/Google adopted. By March 2026, 32 tools supported it. Five months is not enough time for collective practice to crystallize.

4. **"Works on my machine" is the testing default.** Authors develop in their own `.claude/` directory; the runtime walks the filesystem and finds the skill. The bug only surfaces on fresh installs of the published manifest.

5. **No install-time loud failure.** `claude plugin install` succeeds with an incomplete manifest. Missing skills are silently invisible. There's no `ImportError`-equivalent that tells the author the package they just published is broken.

## What other ecosystems do

| Ecosystem | Forcing function preventing the equivalent bug |
|---|---|
| TypeScript / Node | `tsc --noEmit` runs in every project's CI; missing `exports` causes `Cannot find module` at runtime |
| Python | Missing `entry_points` causes `pkg_resources.DistributionNotFound`; `pip install` validates the manifest |
| Rust | `cargo build` cross-checks every `mod` declaration against `src/`; missing file = compile error |
| Ruby | `gem build` rejects gemspecs that reference missing files |
| Go | `go build` and `go vet` cross-check declared packages against disk |
| **Claude plugins** | None. Install succeeds with incomplete manifest. |

The shared pattern across the code ecosystems: **at least one install-time or build-time gate fails loudly on manifest-vs-disk inconsistency.** Plugin authoring doesn't yet have one.

## What "filling the gap" looks like

A complete solution would address each of the five factors:

1. **Provide the missing validator in canonical form** — `/nlpm:check` already does this; needs packaging for author-side use.
2. **Solve discovery** — a single canonical entry point (`claude plugin install` integration; widely-copied GHA template; clear positioning vs the other tools).
3. **Accept that the spec is young** — design for spec evolution; cite primary sources; build in drift detection (v0.7.31's docs-diff workflow is the prototype).
4. **Reduce the "works on my machine" gap** — pre-commit hooks that run on author's machine before the bad commit lands.
5. **Add a loud-failure path** — make NLPM's check fail loudly during pre-publish (CLI exit code, GHA failure, pre-commit rejection).

The scope expansion plan (`analysis/scope-expansion-2026-05.md`) addresses each of these.

## Risk: Anthropic adds the check

The largest single risk to NLPM's positioning in this niche is Anthropic adding manifest-vs-disk consistency to the official `plugin-validator` agent. Probability: moderate (Anthropic is actively maintaining the agent). Timeline: unknown.

Mitigations:
- **Be useful regardless.** NLPM's audit corpus + rule-health feedback loop is the differentiated asset, not just the check.
- **Cite NLPM as the originator.** If we're first to ship this check broadly, the case-study corpus becomes the evidence for *why* the check matters. Anthropic adopting it later validates the work; doesn't invalidate it.
- **Stay structurally distinct.** Auditor mode (third-party scanning + rule learning) is unique even if the local validator becomes a commodity.

## Sources

All URLs verified 2026-05-11:

- Anthropic plugin-validator agent: <https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/agents/plugin-validator.md>
- Claude Code plugins reference: <https://code.claude.com/docs/en/plugins-reference>
- Agent Skills specification (Linux Foundation): <https://agentskills.io/specification>
- skills-ref reference library: <https://github.com/agentskills/agentskills/tree/main/skills-ref>
- Third-party validators surveyed:
  - <https://github.com/situ2001/claude-plugin-validate>
  - <https://github.com/William-Yeh/agent-skill-linter>
  - <https://github.com/thedaviddias/skill-check>
  - <https://github.com/agent-ecosystem/skill-validator>
- NLPM audit corpus (this repo): 199 audited repos, 36 case studies, ~70% PR acceptance rate as of 2026-05-11
