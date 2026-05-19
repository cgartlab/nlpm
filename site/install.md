---
title: How to install
outline: [2, 3]
---

# How to install

NLPM ships as a Claude Code plugin via the `xiaolai` marketplace.

## In a project

```bash
claude plugin install nlpm@xiaolai --scope project
```

Then in that project:

```bash
/nlpm:ls              # discover NL artifacts
/nlpm:score           # 100-point quality scoring
/nlpm:check           # cross-component consistency
/nlpm:vocab-init      # bootstrap a vocabulary skill (optional)
/nlpm:report          # render a self-contained HTML report
```

## For all your projects

```bash
claude plugin install nlpm@xiaolai --scope user
```

## Standalone binary (no Claude Code required)

`bin/nlpm-check` is a single-file Python script (stdlib only) that runs the deterministic subset of `/nlpm:check`. Drop into pre-commit hooks or CI.

```bash
git clone https://github.com/xiaolai/nlpm-for-claude
./nlpm-for-claude/bin/nlpm-check /path/to/your/plugin
```

Or copy `bin/nlpm-check` into your repo:

```bash
curl -fsSL https://raw.githubusercontent.com/xiaolai/nlpm-for-claude/main/bin/nlpm-check -o nlpm-check
chmod +x nlpm-check
./nlpm-check .
```

Pre-commit hook and GitHub Actions workflow templates live at:

- `templates/pre-commit-nlpm.sh`
- `templates/workflows/nlpm-check.yml`

## Vocabulary discipline (R51, opt-in)

After installing NLPM in your project, decide whether to enforce a canonical noun/verb registry. If yes:

```bash
/nlpm:vocab-init      # detects layout, runs the extractor, seeds tables
```

This writes `skills/<plugin>/vocabulary/SKILL.md` + `registry.yaml`. Prune the seeded tables, define `deprecated:` synonym lists, then opt into R51 by adding to `.claude/nlpm.local.md`:

```yaml
rule_overrides:
  R51:
    enabled: true
    vocabulary_skill: skills/<plugin>/vocabulary/
```

Now `/nlpm:score` and `/nlpm:check` flag deprecated-synonym occurrences. See [/reference/principles](/reference/principles) for the six principles behind R51.

## Updates

```bash
claude plugin update nlpm@xiaolai
```

## Uninstall

```bash
claude plugin uninstall nlpm@xiaolai
```

## See also

- [/reference/](/reference/) — full framework guide
- [Auditor dashboard](/dashboard.html) — cross-repo audit data
- [GitHub issues](https://github.com/xiaolai/nlpm-for-claude/issues) — bug reports, feature requests
