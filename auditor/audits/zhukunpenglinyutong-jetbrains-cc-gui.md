# NLPM Audit: zhukunpenglinyutong/jetbrains-cc-gui
**Date**: 2026-05-11  |  **Artifacts**: 1  |  **Strategy**: single
**NL Score**: 96/100
**Security**: CLEAR
**Bugs**: 1  |  **Quality Issues**: 3  |  **Security Findings**: 4

## NL Score Summary
| File | Type | Score | Top Issue |
|------|------|-------|-----------|
| `.agents/skills/vercel-react-best-practices/SKILL.md` | skill | 96 | Vague trigger language ("optimal", "performance improvements"); broken `AGENTS.md` reference |

## Security Scan
| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Medium | 2 |
| Low | 2 |

### Execution Surface Inventory
| Surface | Files |
|---------|-------|
| Hooks | 0 |
| Scripts (JS/MJS) | 65 (ai-bridge/*.js, webview/scripts/*.mjs, src/main/resources/libs/*.js) |
| MCP configs | 0 |
| Package manifests | 2 (webview/package.json, ai-bridge/package.json) |

### Security Findings
| # | Severity | File | Line | Pattern | Description |
|---|----------|------|------|---------|-------------|
| 1 | ~~Critical~~ (FP) | `ai-bridge/config/api-config.test.js` | 21, 48, 97 | eval-with-variables | `execFileSync` passes `--eval` with a template-literal `script` variable. Pre-scan flagged as CRITICAL; manual review finds this is a false positive — the script is built entirely from hardcoded logic and a `path.resolve()` result wrapped in `JSON.stringify()`; no user input reaches the eval'd string. |
| 2 | Medium | `ai-bridge/services/claude/mcp-status/stdio-tools-getter.js` | 95 | spawn-shell-true | `spawn()` called with `shell: true` on Windows for npm/npx commands. Args originate from user-configured MCP server settings; shell injection is possible if a malicious MCP config is loaded. |
| 3 | Medium | `ai-bridge/services/claude/mcp-status/stdio-verifier.js` | 87 | spawn-shell-true | Same pattern as finding #2 in the verifier counterpart. |
| 4 | Low | `webview/package.json` | — | unpinned-semver | All devDependencies use `^` semver ranges (e.g., `vite: "^7.2.4"`, `react: "^19.2.0"`). Minor upgrades can silently introduce breaking changes or vulnerabilities. |
| 5 | Low | `ai-bridge/package.json` | — | unpinned-semver | Production dependency `sql.js: "^1.12.0"` uses a `^` range; exact pinning is preferable for a production database-access library. |

## Bugs (PR-worthy)
| # | File | Issue | Impact |
|---|------|-------|--------|
| 1 | `.agents/skills/vercel-react-best-practices/SKILL.md` | Line 149 references `AGENTS.md` as the full compiled document, but that file does not exist in the skill directory | Readers who follow the "Full Compiled Document" instruction get a 404; the complete compiled guide is unavailable |

## Security Fixes (PR-worthy, Medium/Low only)
| # | File | Issue | Suggested Fix |
|---|------|-------|---------------|
| 1 | `ai-bridge/services/claude/mcp-status/stdio-tools-getter.js` | `shell: true` passed to `spawn()` with user-supplied args from MCP config | Validate/sanitize args before spawn, or replace with `execFile` (no shell) and handle `.cmd`/`.bat` path translation separately |
| 2 | `ai-bridge/services/claude/mcp-status/stdio-verifier.js` | Same `shell: true` pattern as finding #1 | Same fix as above |
| 3 | `webview/package.json` | Unpinned `^` devDependency versions | Pin exact versions or enforce lockfile integrity (`--frozen-lockfile`) in CI |
| 4 | `ai-bridge/package.json` | Production `sql.js` uses `^1.12.0` range | Pin to `"sql.js": "1.12.0"` |

## Quality Issues (informational)
| # | File | Issue | Penalty |
|---|------|-------|---------|
| 1 | `.agents/skills/vercel-react-best-practices/SKILL.md` | "optimal performance patterns" in description uses vague trigger language — "optimal" is undefined | -2 |
| 2 | `.agents/skills/vercel-react-best-practices/SKILL.md` | "performance improvements" in the trigger list is a vague category with no boundary | -2 |
| 3 | `.agents/skills/vercel-react-best-practices/metadata.json` | `abstract` field says "40+ rules" but SKILL.md header states "70 rules across 8 categories" — stale count | informational |

## Cross-Component
The only NL artifact is a standalone SKILL file. Cross-component concerns are limited to the broken `AGENTS.md` reference (filed as Bug #1) and the rule-count mismatch between `metadata.json` and `SKILL.md`. No orphaned components, no command↔agent wiring to verify.

The `rules/` subdirectory is fully populated (all 70 rule files referenced in the Quick Reference section are present), so the per-rule cross-references in the SKILL body are intact.

## Recommendation
CLEAR — submit PRs for Bug #1 (create or link `AGENTS.md`) and the Medium/Low security fixes. No Critical or High security findings were confirmed after manual review; the pre-scan's single Critical match is a false positive in a test harness.
