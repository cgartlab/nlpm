#!/usr/bin/env python3
"""Parse rule_overrides from an NLPM config markdown file.

Reads YAML frontmatter from the file given as argv[1].
Prints one JSON object per rule override, one per line.
Exits silently (no output) if the file has no overrides or no frontmatter.
"""

import json
import re
import sys

try:
    import yaml
except ImportError:
    print(
        "parse-suppressions: PyYAML not installed; suppressions disabled "
        "(install with `pip install pyyaml` to enable).",
        file=sys.stderr,
    )
    sys.exit(0)


def main() -> int:
    if len(sys.argv) < 2:
        return 0

    try:
        with open(sys.argv[1]) as f:
            content = f.read()
    except OSError as e:
        # Distinguish "no config file" (expected, silent) from
        # "config exists but is unreadable" (must surface).
        from os.path import exists
        if exists(sys.argv[1]):
            print(
                f"parse-suppressions: config {sys.argv[1]} unreadable: {e}",
                file=sys.stderr,
            )
            return 1
        return 0

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return 0

    try:
        frontmatter = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        print(
            f"parse-suppressions: YAML parse error in {sys.argv[1]}: {e}",
            file=sys.stderr,
        )
        return 1

    if not isinstance(frontmatter, dict):
        return 0

    overrides = frontmatter.get("rule_overrides") or {}
    if not isinstance(overrides, dict):
        return 0

    for rule, val in overrides.items():
        print(json.dumps({"rule_id": str(rule), "override": val}))

    return 0


if __name__ == "__main__":
    sys.exit(main())
