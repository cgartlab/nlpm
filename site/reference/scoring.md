---
title: Scoring & severity
outline: [2, 3]
---

# Scoring & Severity

How the 100-point rubric maps to score bands and how the scorer assigns severity levels to findings.

## Score bands {#score-bands}

| Range | Label | Meaning |
|-------|-------|---------|
| 90–100 | Excellent | Production-ready; minor or no issues |
| 80–89 | Good | Solid; one or two non-critical gaps |
| 70–79 | Adequate | Meets threshold; noticeable gaps to address |
| 60–69 | Weak | Below threshold; significant issues |
| <60 | Rewrite | Fundamental problems; recommend rewriting from scratch |

**Default pass threshold:** 70. Configurable in `.claude/nlpm.local.md`.

---

## Severity levels {#severity-levels}

| Severity | Local scorer | Auditor schema |
|----------|--------------|----------------|
| **HIGH** | penalty ≥ 10 points | scorer reproduced the breakage during the scoring pass; `confidence: high`, requires concrete `evidence`. Only HIGH findings reach the contribute step. |
| **MEDIUM** | penalty 5–9 points | default confidence; no reproducer required. |
| **LOW** | penalty < 5 points | weakest signal; kept for our own learning but not for PRs. |
