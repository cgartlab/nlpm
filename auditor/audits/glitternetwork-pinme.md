# NLPM Audit: glitternetwork/pinme
**Date**: 2026-04-06  |  **Artifacts**: 6  |  **Strategy**: single
**NL Score**: 98/100
**Security**: CLEAR
**Bugs**: 0  |  **Quality Issues**: 5  |  **Security Findings**: 2

## NL Score Summary
| File | Type | Score | Top Issue |
|------|------|-------|-----------|
| skills/pinme-share/SKILL.md | skill | 94 | 3 vague quantifiers ("valuable", "useful", "appropriate") |
| skills/pinme/SKILL.md | skill | 96 | 2 vague quantifiers ("when needed", "clear need") |
| CLAUDE.md | project-context | 100 | — |
| skills/pinme-auth/SKILL.md | skill | 100 | — |
| skills/pinme-email/SKILL.md | skill | 100 | — |
| skills/pinme-llm/SKILL.md | skill | 100 | — |

Weighted average: (94 + 96 + 100 + 100 + 100 + 100) / 6 = **98/100**

## Security Scan
| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Medium | 2 |
| Low | 0 |

### Execution Surface Inventory
| Surface | Files |
|---------|-------|
| Build scripts (root) | build.js, rollup.config.js |
| Package manifest | package.json |
| Hooks | none |
| MCP configs | none |
| Requirements | none |

### Security Findings
| # | Severity | File | Line | Pattern | Description |
|---|----------|------|------|---------|-------------|
| 1 | Medium | build.js | 5 | env-var-bundle-inject | `for (const key in process.env)` adds ALL current env vars to esbuild `define`; any secret var whose name is referenced as `process.env.X` in the TypeScript source will be baked into the published dist/index.js binary |
| 2 | Medium | build.js | 10 | env-var-bundle-inject | `SECRET_KEY` is explicitly added to esbuild `define`; if `process.env.SECRET_KEY` is referenced in the source and a real value is set at build time, it will be embedded in the published npm package |

## Bugs (PR-worthy)
| # | File | Issue | Impact |
|---|------|-------|--------|
| — | — | No bugs found | — |

## Security Fixes (PR-worthy, Medium/Low only)
| # | File | Issue | Suggested Fix |
|---|------|-------|---------------|
| 1 | build.js | All env vars injected into esbuild define | Replace the `for (const key in process.env)` loop (lines 5–7) with an explicit allowlist of only non-secret build-time vars (e.g. `NODE_ENV`); never derive it from the full environment |
| 2 | build.js | `SECRET_KEY` explicitly baked into compiled binary | Remove line 10; `SECRET_KEY` should be read at runtime via `process.env.SECRET_KEY`, not replaced at build time — if it must be injected, gate it behind a build-time env flag and document that no real secret should be present during `npm publish` |

## Quality Issues (informational)
| # | File | Issue | Penalty |
|---|------|-------|---------|
| 1 | skills/pinme-share/SKILL.md | "valuable" (line 32): vague quantifier — "unless interaction is valuable" gives Claude no actionable threshold | -2 |
| 2 | skills/pinme-share/SKILL.md | "useful" (line 52): vague quantifier — "only when useful to the recipient" is not actionable | -2 |
| 3 | skills/pinme-share/SKILL.md | "appropriate" (line 53): vague quantifier — "only if appropriate" gives no decision rule | -2 |
| 4 | skills/pinme/SKILL.md | "when needed" (line 203): vague quantifier — "can be added when needed" leaves the decision rule unspecified | -2 |
| 5 | skills/pinme/SKILL.md | "clear need" (line 249): vague quantifier — "if there is a clear need" sets no concrete threshold | -2 |

## Cross-Component
All skill cross-references are internally consistent. `skills/pinme-share/SKILL.md` correctly defers to the main `pinme` skill for installation and authentication. `skills/pinme/SKILL.md` explicitly names the integration companion skills (pinme-auth, pinme-email, pinme-llm, pinme-share). `CLAUDE.md` accurately documents the `skills/` directory. The `rollup.config.js` file is noted as legacy/unused in CLAUDE.md and has no associated skill references — no orphan issue. No broken references or terminology drift detected.

## Recommendation
CLEAR — submit PRs for all bugs and medium/low security fixes.
