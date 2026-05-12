#!/usr/bin/env python3
"""Render the quarterly rule-review issue body.

Reads:
  auditor/docs-citations.json
  auditor/disagreements.jsonl   (optional)

Writes the rendered markdown body to stdout. The caller pipes it to
`gh issue create --body-file -` or saves it for later.

Extracted from auditor-rule-review.yml in v0.8.10 — the previous
inline-shell version had 147 lines mixing two Python heredocs and bash
template assembly. Single-language extraction here is more testable and
removes shellcheck noise.
"""

import json
import sys
from datetime import datetime, timedelta, timezone


def citation_stats(path: str = "auditor/docs-citations.json"):
    try:
        with open(path) as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return 0, []

    urls = [k for k in data if not k.startswith("_")]
    today = datetime.now(timezone.utc).date()
    cutoff = today - timedelta(days=90)
    stale = []
    for url in urls:
        try:
            lv = datetime.fromisoformat(
                data[url].get("last_verified", "1970-01-01")
            ).date()
            if lv < cutoff:
                stale.append((url, lv.isoformat()))
        except (TypeError, ValueError):
            stale.append((url, "unparseable"))
    return len(urls), stale


def doc_citation_events(path: str = "auditor/disagreements.jsonl", days: int = 90):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    count = 0
    examples = []
    try:
        with open(path) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("event") != "maintainer_rejected":
                    continue
                if e.get("dissent_type") != "docs_citation":
                    continue
                if e.get("timestamp", "") < cutoff:
                    continue
                count += 1
                if len(examples) < 5:
                    examples.append(
                        f"  - {e.get('pr', '?')}: {e.get('quote', '')[:120]}"
                    )
    except FileNotFoundError:
        pass
    return count, examples


def render(quarter: str, date: str) -> str:
    total_urls, stale = citation_stats()
    doc_citation_count, doc_citation_examples = doc_citation_events()

    out = [
        f"## Quarterly Rule Review — {quarter}",
        "",
        f"Filed: {date}. The next review is in ~90 days.",
        "",
        "NLPM's rules encode assumptions about Claude Code's schema",
        "(required/optional fields, tool catalog, hook events, path",
        "conventions). The ecosystem is a moving target. Three",
        "automated checks (docs-diff, classifier docs_citation,",
        "maintainer feedback) cover most drift, but quarterly",
        "review catches what they miss.",
        "",
        "### Citation index health",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Tracked doc URLs | {total_urls} |",
        f"| Stale citations (last_verified > 90 days ago) | {len(stale)} |",
        f"| docs_citation events from maintainers (last 90d) | {doc_citation_count} |",
        "",
    ]

    if stale:
        out.extend([
            "#### Stale citations to re-verify",
            "",
        ])
        for url, lv in stale:
            out.append(f"- {url} (last verified {lv})")
        out.extend([
            "",
            "For each: open the URL, confirm the cited `quote` still",
            "appears, then update `last_verified` in",
            "`auditor/docs-citations.json`.",
            "",
        ])

    if doc_citation_examples:
        out.extend([
            "#### docs_citation events to triage",
            "",
        ])
        out.extend(doc_citation_examples)
        out.extend([
            "",
            "For each: read the PR comment, confirm whether the cited",
            "URL contradicts an NLPM rule, and either fix the rule or",
            "mark the citation as a known-acceptable disagreement.",
            "",
        ])

    out.extend([
        "### Manual checklist",
        "",
        "- [ ] Re-verify every URL in `auditor/docs-citations.json`",
        "  against the live page; bump `last_verified` for each",
        "  citation that still holds.",
        "- [ ] Skim <https://code.claude.com/docs/en/changelog>",
        "  (if it exists) for new tools, hook events, frontmatter",
        "  fields, or path conventions added since last review.",
        "  For each new feature: does an NLPM rule already cover",
        "  it? If not, draft one.",
        "- [ ] Skim <https://agentskills.io/specification> for any",
        "  spec revisions; cross-check against",
        "  `skills/nlpm/conventions/SKILL.md` §5.",
        "- [ ] Review the 50 catalog rules in",
        "  `skills/nlpm/rules/SKILL.md` and ask, for each: \"if a",
        "  maintainer cited official docs against this rule, would",
        "  the docs side win?\" Flag any that feel shaky.",
        "- [ ] Check the daily report's \"noisy rules\" section for",
        "  rules that have been noisy for >2 quarters — that's a",
        "  sign the rule itself may be wrong, not just imprecise.",
        "- [ ] If any rules need updating, open a follow-up PR",
        "  with the changes + bump the citation `last_verified`",
        "  dates.",
        "",
        "### Action when review is complete",
        "",
        "Close this issue with a brief comment summarizing what",
        "changed (if anything) and which citations were re-verified.",
        "",
        "---",
        "",
        "_Filed automatically by `auditor-rule-review.yml`._",
    ])
    return "\n".join(out) + "\n"


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "usage: generate-rule-review-body.py <QUARTER> <DATE>",
            file=sys.stderr,
        )
        return 2
    sys.stdout.write(render(sys.argv[1], sys.argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
