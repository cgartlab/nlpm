#!/usr/bin/env python3
"""Render an HTML audit report for a single external repo.

Uses the same template + vendored G6 as `/nlpm:report` but populates from
auditor data (filtered to one repo). Output: `auditor/reports/<slug>.html`.

Reads:
  - auditor/findings.jsonl              (all-repo findings; filtered here)
  - auditor/vocab-advisories.jsonl      (all-repo advisories; filtered)
  - auditor/audits/<slug>.md            (audit report; extract overall score)
  - auditor/audits/<slug>.findings.jsonl
  - auditor/audits/<slug>.re-audit.findings.jsonl  (if present)
  - auditor/audits/<slug>.vocab-drift.jsonl       (if present)
  - auditor/registry/repos.json         (repo metadata)
  - auditor/logs/events.jsonl           (lifecycle events for trend)

Usage:
  python3 auditor/scripts/render-repo-report.py --repo owner/name
  python3 auditor/scripts/render-repo-report.py --repo owner/name --out auditor/reports/
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT / "templates" / "report"
AUDITOR = ROOT / "auditor"
DOCS_BUILDER = ROOT / "bin" / "nlpm-build-docs"


class _JsonlList(list):
    """`list` subclass that accepts attribute assignment.

    Used to surface a `malformed_count` alongside the parsed records
    without breaking callers that just iterate the list.
    """

    malformed_count: int = 0


def read_jsonl(path: Path) -> _JsonlList:
    if not path.exists():
        return _JsonlList()
    out: _JsonlList = _JsonlList()
    malformed = 0
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as exc:
            malformed += 1
            print(f"WARN {path}:{i} malformed JSON: {exc}", file=sys.stderr)
    if malformed:
        # Surface the counter on the list so build_data can include it in
        # the report's metadata — a silent skip would let bad log lines
        # hide finding drops from anyone reading the per-repo report.
        out.malformed_count = malformed
    return out


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def slug_for(repo: str) -> str:
    return repo.replace("/", "-")


def assert_slug_uniqueness(repo: str) -> None:
    """Fail loudly if `repo`'s slug collides with another repo in the registry.

    The owner-repo → owner-repo slug scheme is ambiguous when both halves
    contain hyphens — `a/b-c` and `a-b/c` produce the same slug. The current
    corpus has no collision (47 owners and 150 names contain `-`, all
    distinct after slugging), but a future audit could introduce one and
    silently overwrite the prior repo's HTML/JSON/audit files.

    This check reads the registry and raises if any *other* repo would
    produce the same slug as this one. Catches the collision at write
    time rather than after the file has been overwritten.
    """
    registry_path = AUDITOR / "registry" / "repos.json"
    if not registry_path.exists():
        return
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    target = slug_for(repo)
    colliding = sorted(
        other
        for other in registry.get("repos", {})
        if other != repo and slug_for(other) == target
    )
    if colliding:
        raise ValueError(
            f"slug collision: '{repo}' produces slug='{target}', which is "
            f"also the slug for {colliding}. The current owner-repo scheme "
            f"is ambiguous when both halves contain '-'. Resolve before "
            f"rendering — rename one repo's entry or switch to a "
            f"hash-suffixed slug."
        )


def extract_score(md_text: str) -> int | None:
    """Audit markdown has lines like 'Score: 87/100' or '87/100'."""
    m = re.search(r"([0-9]{1,3})\s*/\s*100", md_text)
    if not m:
        return None
    val = int(m.group(1))
    return val if 0 <= val <= 100 else None


def extract_security(md_text: str) -> str | None:
    m = re.search(r"Security[^:]*:\s*(CLEAR|REVIEW|BLOCKED)", md_text)
    return m.group(1) if m else None


def build_history(audit_md: Path, reaudit_md: Path) -> list[dict]:
    """Pull score-at-original-audit and score-at-HEAD-of-re-audit when present."""
    out = []
    if audit_md.exists():
        score = extract_score(audit_md.read_text(encoding="utf-8"))
        if score is not None:
            ts = audit_md.stat().st_mtime
            out.append({"timestamp": datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "average_score": score, "kind": "initial_audit"})
    if reaudit_md.exists():
        score = extract_score(reaudit_md.read_text(encoding="utf-8"))
        if score is not None:
            ts = reaudit_md.stat().st_mtime
            out.append({"timestamp": datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "average_score": score, "kind": "re_audit"})
    out.sort(key=lambda x: x["timestamp"])
    return out


def build_files_panel(findings: list[dict]) -> tuple[list[dict], dict]:
    """Group findings by file path; no per-file scores from the auditor.

    Returns (files_array, summary). The 'score' field is null per file
    because the auditor records overall score in markdown, not per-file.
    """
    by_file: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        path = f.get("file") or ""
        if path:
            by_file[path].append(f)
    files = []
    for path, fs in sorted(by_file.items()):
        # Derive a "type" from the path heuristically
        kind = "?"
        if path.startswith("commands/") or path.startswith("./commands/"):
            kind = "command"
        elif path.startswith("agents/"):
            kind = "agent"
        elif path.endswith("SKILL.md") or "/skills/" in path:
            kind = "skill"
        elif path.endswith("plugin.json"):
            kind = "manifest"
        elif path == "CLAUDE.md" or path.endswith("/CLAUDE.md"):
            kind = "claude-md"
        elif "/hooks/" in path or path.endswith("hooks.json"):
            kind = "hook-config"
        files.append({
            "path": path,
            "type": kind,
            "score": None,
            "findings": [
                {"rule": x.get("rule_id"), "severity": x.get("severity"), "line": x.get("line"),
                 "message": x.get("description") or x.get("evidence") or ""}
                for x in fs
            ],
        })
    summary = {
        "total_files": len(files),
        "average_score": None,  # auditor doesn't track per-file averages
        "pass_count": 0,
        "fail_count": 0,
    }
    return files, summary


def build_findings_panel(findings: list[dict]) -> list[dict]:
    out = []
    for f in findings:
        sev = f.get("severity") or "low"
        conf = f.get("confidence") or "medium"
        evidence = f.get("evidence") or ""
        msg = f.get("description") or evidence
        if evidence and evidence != msg:
            msg = f"{msg} — {evidence}"
        out.append({
            "rule": f.get("rule_id") or "UNCLASSIFIED",
            "severity": sev,
            "confidence": conf,
            "file": f.get("file") or "",
            "line": f.get("line"),
            "message": msg,
        })
    return out


def build_drift_panel(advisories: list[dict]) -> dict:
    return {
        "candidates": [
            {
                "terms": a.get("terms", []),
                "confidence": a.get("confidence", "medium"),
                "disposition": a.get("disposition", "drift"),
                "suggested_canonical": a.get("suggested_canonical", ""),
                "files_affected": a.get("files_affected", 0),
                "evidence": a.get("evidence", ""),
            }
            for a in advisories
        ]
    }


def build_data(repo: str) -> dict:
    slug = slug_for(repo)
    all_findings = read_jsonl(AUDITOR / "findings.jsonl")
    all_advisories = read_jsonl(AUDITOR / "vocab-advisories.jsonl")
    registry = read_json(AUDITOR / "registry" / "repos.json", {})

    repo_findings = [f for f in all_findings if f.get("repo") == repo]
    repo_advisories = [a for a in all_advisories if a.get("repo") == repo]

    # Prefer the per-audit sidecar if it exists — newer than the global log
    # for the most-recent run.
    sidecar = AUDITOR / "audits" / f"{slug}.findings.jsonl"
    if sidecar.exists():
        sidecar_findings = read_jsonl(sidecar)
        # Tag with repo so build_files_panel can group correctly
        for f in sidecar_findings:
            f.setdefault("repo", repo)
        if sidecar_findings:
            repo_findings = sidecar_findings

    audit_md = AUDITOR / "audits" / f"{slug}.md"
    reaudit_md = AUDITOR / "audits" / f"{slug}.re-audit.md"
    audit_md_text = audit_md.read_text(encoding="utf-8") if audit_md.exists() else ""
    overall_score = extract_score(audit_md_text)
    security = extract_security(audit_md_text)

    files, summary = build_files_panel(repo_findings)
    summary["average_score"] = overall_score  # the auditor's overall, not per-file avg

    history = build_history(audit_md, reaudit_md)
    findings = build_findings_panel(repo_findings)
    drift = build_drift_panel(repo_advisories)

    repo_info = (registry.get("repos") or {}).get(repo, {}) if isinstance(registry, dict) else {}
    status = repo_info.get("status") if isinstance(repo_info, dict) else None
    stars = repo_info.get("stars") if isinstance(repo_info, dict) else None

    data = {
        "project": repo,
        "score_threshold": 70,
        "r51_enabled": False,
        "summary": summary,
        "files": files,
        "history": history,
        "cross_component": {"nodes": [], "edges": []},
        "vocabulary": None,
        "vocab_drift": drift,
        "findings": findings,
        # Per-repo extras surfaced in the header via the same data blob.
        "repo_meta": {
            "status": status,
            "stars": stars,
            "security": security,
            "audit_report_path": str(audit_md.relative_to(ROOT)) if audit_md.exists() else None,
        },
    }
    return data


def render(data: dict, out_dir: Path) -> Path:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Vendor + assets — share between dashboard.html and per-repo reports.
    # Always refresh assets (small CSS/JS files; cheap; lets template fixes
    # propagate to already-rendered reports). Vendor (1.3 MB G6) only on
    # first render — it doesn't change between releases.
    vendor_dst = out_dir / "vendor"
    assets_dst = out_dir / "assets"
    if not vendor_dst.exists():
        shutil.copytree(TEMPLATE_DIR / "vendor", vendor_dst)
    if assets_dst.exists():
        shutil.rmtree(assets_dst)
    shutil.copytree(TEMPLATE_DIR / "assets", assets_dst)

    template = (TEMPLATE_DIR / "single.html").read_text(encoding="utf-8")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data["generated_at"] = ts

    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = (
        template
        .replace("{{PROJECT}}", data["project"])
        .replace("{{GENERATED_AT}}", ts)
        .replace("{{DATA_JSON}}", data_json)
    )

    repo = data["project"]
    assert_slug_uniqueness(repo)
    slug = slug_for(repo)
    target = out_dir / f"{slug}.html"
    target.write_text(html, encoding="utf-8")

    # JSON sidecar — see analysis/report-data-schema.md.
    data.setdefault("schema_version", 1)
    (out_dir / f"{slug}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Docs are shared across all per-repo reports in this out_dir. Build
    # once if missing; cheap to rebuild but per-repo runs may be many.
    # On a docs-build failure the per-repo report at `target` is still
    # valid — but the rule-anchor cross-links would 404. Surface the
    # failure loudly via stderr and a sidecar (same pattern as
    # bin/nlpm-report and render-dashboard.py) instead of swallowing it.
    docs_index = out_dir / "docs" / "index.html"
    if not docs_index.exists():
        proc = subprocess.run(
            [sys.executable, str(DOCS_BUILDER), "--out", str(out_dir / "docs")],
            check=False, capture_output=True, text=True,
        )
        if proc.returncode != 0:
            print(
                f"render-repo-report: docs build failed (exit {proc.returncode}); "
                f"rule-anchor links in {target} will not resolve until this is "
                f"resolved.",
                file=sys.stderr,
            )
            if proc.stderr:
                print(proc.stderr, file=sys.stderr)
            (out_dir / "docs").mkdir(exist_ok=True)
            (out_dir / "docs" / "_build_error.txt").write_text(
                f"exit_code: {proc.returncode}\n\nstdout:\n{proc.stdout}\n\nstderr:\n{proc.stderr}\n",
                encoding="utf-8",
            )

    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--repo", required=True, help="Target repo (owner/name)")
    parser.add_argument("--out", default=str(AUDITOR / "reports"), help="Output directory")
    parser.add_argument("--vocab-data", default=None,
                        help="Optional path to a VocabularyData JSON (see "
                             "analysis/report-data-schema.md). When present, "
                             "the contents land in the report's `vocabulary` field.")
    args = parser.parse_args(argv)

    if "/" not in args.repo:
        print("error: --repo must be owner/name", file=sys.stderr)
        return 2

    data = build_data(args.repo)
    if args.vocab_data:
        vpath = Path(args.vocab_data)
        if vpath.exists():
            try:
                data["vocabulary"] = json.loads(vpath.read_text(encoding="utf-8"))
                print(f"  Loaded vocabulary from {vpath}")
            except json.JSONDecodeError as e:
                print(f"  warning: --vocab-data {vpath} invalid JSON: {e}", file=sys.stderr)
        else:
            print(f"  warning: --vocab-data {vpath} not found; vocabulary stays null", file=sys.stderr)
    result = render(data, Path(args.out))
    print(f"Wrote {result}")
    print(f"  Score: {data['summary'].get('average_score')}")
    print(f"  Findings: {len(data['findings'])}")
    print(f"  Vocab advisories: {len(data['vocab_drift']['candidates'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
