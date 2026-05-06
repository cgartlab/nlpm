# NLPM Re-Audit: kubesphere/kubesphere

**Date**: 2026-05-06  |  **Artifacts**: 26  |  **Strategy**: batched
**NL Score**: 92/100
**Bugs**: 3  |  **Quality Issues**: 5

## NL Score Summary

| File | Type | Score | Top Issue |
|------|------|-------|-----------|
| skills/kubesphere-devops-tenant/SKILL.md | skill | 82 | Orphaned shell fragment in List Pipelines code example |
| skills/kubesphere-fluid/SKILL.md | skill | 82 | YAML indentation error in ThinRuntime template |
| skills/whizard-notification/SKILL.md | skill | 84 | Incomplete curl commands with dangling backslash continuation |
| skills/kubesphere-devops-overview/SKILL.md | skill | 88 | Duplicate architecture table and duplicate section header |
| skills/kubesphere-devops-pipeline/SKILL.md | skill | 90 | Duplicate troubleshooting table at end of file |
| skills/kubesphere-openkruise/SKILL.md | skill | 91 | Redundant `# Skill:` heading inside body |
| skills/kubesphere-devops-credentials/SKILL.md | skill | 92 | — |
| skills/kubesphere-volcano/SKILL.md | skill | 92 | — |
| skills/whizard-telemetry-ruler/SKILL.md | skill | 92 | Stray empty bullet in Dependencies section |
| skills/wiztelemetry-tracing/SKILL.md | skill | 92 | — |
| skills/frontend-forge-fi-operations/SKILL.md | skill | 93 | — |
| skills/kubesphere-devops-argocd/SKILL.md | skill | 93 | — |
| skills/kubesphere-devops-jenkins/SKILL.md | skill | 93 | — |
| skills/kubesphere-extension-management/SKILL.md | skill | 93 | — |
| skills/kubesphere-multi-tenant-management/SKILL.md | skill | 93 | — |
| skills/kubesphere-network-extension-operations/SKILL.md | skill | 93 | — |
| skills/opensearch/SKILL.md | skill | 93 | — |
| skills/vector/SKILL.md | skill | 93 | — |
| skills/whizard-auditing/SKILL.md | skill | 93 | — |
| skills/whizard-logging/SKILL.md | skill | 93 | — |
| skills/whizard-telemetry/SKILL.md | skill | 93 | — |
| skills/frontend-integration-yaml/SKILL.md | skill | 95 | — |
| skills/kubesphere-cluster-management/SKILL.md | skill | 95 | — |
| skills/kubesphere-core/SKILL.md | skill | 95 | — |
| skills/nodegroup/SKILL.md | skill | 95 | — |
| skills/whizard-events/SKILL.md | skill | 95 | — |

## Bugs (PR-worthy)

| # | File | Issue | Confidence | Evidence | Impact |
|---|------|-------|------------|----------|--------|
| 1 | skills/kubesphere-fluid/SKILL.md | YAML indentation error in ThinRuntime template: `thin:` and its children use 1-space indent instead of 2, making them peers of `spec:` rather than children | high | `thin:` appears at column 1 relative to `spec:`, breaking YAML hierarchy — the block would fail a YAML parser's structure validation | Users copy-paste invalid YAML that fails `kubectl apply` with a schema error |
| 2 | skills/kubesphere-devops-tenant/SKILL.md | Orphaned shell fragment in List Pipelines (Tenant View) code example (~line 249): a duplicate `-H "Authorization: Bearer ${API_TOKEN}" \| jq` line appears after a complete curl command, not attached to any curl invocation | high | Third line of the code block is a detached header+pipe fragment with no preceding command; the block is not copy-paste executable | Readers cannot run the example as shown; the fragment produces a shell parse error |
| 3 | skills/whizard-notification/SKILL.md | Two curl GET commands (lines ~251 and ~256) end with a backslash line-continuation character but the next line is blank, producing syntactically broken shell commands | high | Both curl calls terminate with `\` at end of line; the blank continuation makes each a syntax error when pasted into a shell | Copy-pasting either command fails silently or raises a shell parse error |

## Quality Issues (informational)

| # | File | Issue | Penalty |
|---|------|-------|---------|
| 1 | skills/kubesphere-devops-overview/SKILL.md | Architecture table appears twice; second occurrence is identical to the first and adds no new information | -8 |
| 2 | skills/kubesphere-devops-overview/SKILL.md | `## Key Resources` section header appears twice consecutively (lines ~338 and ~341) | -4 |
| 3 | skills/kubesphere-devops-pipeline/SKILL.md | Troubleshooting table near end of file (~lines 1276–1284) duplicates the Common Mistakes table (~lines 1239–1248) | -6 |
| 4 | skills/kubesphere-openkruise/SKILL.md | Redundant `# Skill: kubesphere-openkruise` heading at line 7 inside the body; the frontmatter `name:` already carries this | -3 |
| 5 | skills/whizard-telemetry-ruler/SKILL.md | Stray empty `- ` bullet with no content in the Dependencies section at line 34 | -2 |

## Cross-Component

No orphaned components or broken cross-references found. The WizTelemetry dependency chain is consistent: `vector` and `opensearch` are declared as prerequisites in `whizard-logging`, `whizard-auditing`, `whizard-events`, and `whizard-notification`. The `whizard-telemetry` base service is correctly identified as the root dependency. The DevOps skills (`kubesphere-devops-overview`, `kubesphere-devops-tenant`, `kubesphere-devops-pipeline`, `kubesphere-devops-credentials`, `kubesphere-devops-jenkins`, `kubesphere-devops-argocd`) form a coherent cluster with consistent terminology across the suite.

## Recommendation

The kubesphere/kubesphere skill suite is high quality at 92/100 across 26 artifacts; the three PR-worthy bugs are all in code examples (one broken YAML template, one orphaned shell fragment, one dangling backslash) and are straightforward one-line fixes that will make the suite fully copy-paste safe.
