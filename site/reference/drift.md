---
title: Drift criteria
outline: [2, 3]
---

# Drift Dispositions & Confidence

How the `vocab-drift-scanner` agent classifies candidate synonym clusters when running on a corpus without a declared registry.

## Disposition criteria {#disposition-criteria}

For each cluster, decide its disposition:

| Disposition | Criteria | Confidence |
|-------------|----------|------------|
| **drift** | Surface similar + role compatible + ≥ 60% co-occurrence overlap | high |
| **likely drift** | Surface similar + role compatible + < 60% co-occurrence overlap | medium |
| **co-occurrence drift** | Surface dissimilar but role + neighbors match | medium |
| **distinct** | Surface similar but different roles, or context shows clear semantic split | (suppressed from report) |
| **ambiguous** | Mixed signals; can't tell from corpus alone | low |

For `distinct`, do not emit. For everything else, emit a finding.

## Confidence levels {#confidence-criteria}

| Confidence | What it means |
|------------|---------------|
| **high** | Surface similarity + role compatibility + ≥ 60% co-occurrence overlap. Strong recommendation to declare a canonical. |
| **medium** | Surface similarity + role compatibility, but co-occurrence overlap below 60%; or surface dissimilar but role + neighbors match. Worth a maintainer's review. |
| **low** | Mixed signals; the scanner can't tell from the corpus alone. Treat as a hint, not a directive. |
