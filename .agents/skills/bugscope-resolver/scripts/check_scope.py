#!/usr/bin/env python3
"""Check a working tree against the scope a BugScope plan declares.

    python3 check_scope.py .bugscope/plan-<bug_id>.md [--repo .] [--json]

Reads the plan's "Allowed scope" and "Forbidden scope" sections, asks git what has actually
changed, and classifies every changed path:

    allowed      the plan said this file could be touched
    FORBIDDEN    the plan said explicitly not to
    UNDECLARED   the plan says nothing about it, which is the same problem quietly

Exits 0 when everything is allowed, 1 when anything is forbidden or undeclared, 2 when the
plan or the repository could not be read. The point is to make the scope promise checkable
instead of taking the executor's word for it.

No third-party dependencies; git is the only external tool.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Paths the plan never needs to mention: the plan file itself lives here.
ALWAYS_ALLOWED = (".bugscope/",)

SECTION = re.compile(r"^##\s+(Allowed|Forbidden)\s+scope\s*$", re.I)
NEXT_SECTION = re.compile(r"^##\s+")
# A bullet's path is the first backticked token, else the first whitespace-delimited token.
BULLET = re.compile(r"^\s*[-*]\s+(?:`([^`]+)`|(\S+))")


def parse_scopes(plan_text: str) -> tuple[list[str], list[str]]:
    allowed: list[str] = []
    forbidden: list[str] = []
    current: list[str] | None = None

    for line in plan_text.splitlines():
        header = SECTION.match(line)
        if header:
            current = allowed if header.group(1).lower() == "allowed" else forbidden
            continue
        if current is not None and NEXT_SECTION.match(line):
            current = None
            continue
        if current is None:
            continue
        bullet = BULLET.match(line)
        if bullet:
            pattern = (bullet.group(1) or bullet.group(2)).strip().rstrip(",;.")
            # Prose bullets ("Unrelated lint cleanups anywhere") carry no path; skip them.
            if "/" in pattern or "." in pattern or pattern.endswith("*"):
                current.append(pattern)
    return allowed, forbidden


def to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a glob into a regex. `**` spans directories, `*` does not."""
    pattern = pattern.lstrip("./")
    if pattern.endswith("/"):
        pattern += "**"
    out, i = [], 0
    while i < len(pattern):
        char = pattern[i]
        if char == "*":
            if pattern.startswith("**", i):
                out.append(".*")
                i += 2
                if pattern.startswith("/", i):  # `dir/**/x` should also match `dir/x`
                    out.append("/?")
                    i += 1
                continue
            out.append("[^/]*")
        elif char == "?":
            out.append("[^/]")
        else:
            out.append(re.escape(char))
        i += 1
    body = "".join(out)
    # A bare directory or file name also covers everything beneath it.
    return re.compile(rf"^{body}(/.*)?$")


def matches(path: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        if to_regex(pattern).match(path):
            return pattern
    return None


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {args[0]} failed")
    return result.stdout


def changed_paths(repo: Path) -> tuple[list[str], int]:
    """Paths changed in the working tree, relative to `repo`.

    git reports porcelain paths from the repository root. When the plan lives in a
    subproject of a larger repo — a monorepo package, say — those paths need rebasing onto
    the subproject, and changes elsewhere in the repo are not this plan's business.
    """
    prefix = git(repo, "rev-parse", "--show-prefix").strip()
    result = git(repo, "status", "--porcelain", "--untracked-files=all")

    raw: list[str] = []
    for line in result.splitlines():
        if not line.strip():
            continue
        entry = line[3:]
        if " -> " in entry:  # a rename touches both sides
            before, after = entry.split(" -> ", 1)
            raw.extend([before.strip('"'), after.strip('"')])
        else:
            raw.append(entry.strip('"'))

    paths, elsewhere = [], 0
    for path in raw:
        if not prefix:
            paths.append(path)
        elif path.startswith(prefix):
            paths.append(path[len(prefix):])
        else:
            elsewhere += 1
    return sorted(set(paths)), elsewhere


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("plan", type=Path, help="path to .bugscope/plan-<bug_id>.md")
    parser.add_argument("--repo", type=Path, default=Path("."), help="repository root")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    try:
        plan_text = args.plan.read_text(encoding="utf-8")
    except OSError as error:
        print(f"cannot read plan: {error}", file=sys.stderr)
        return 2

    allowed, forbidden = parse_scopes(plan_text)
    if not allowed:
        print(
            f"{args.plan}: no 'Allowed scope' paths found — the plan is incomplete, "
            "and nothing can be checked against it.",
            file=sys.stderr,
        )
        return 2

    try:
        paths, elsewhere = changed_paths(args.repo)
    except (RuntimeError, FileNotFoundError) as error:
        print(f"cannot read git status: {error}", file=sys.stderr)
        return 2

    findings = []
    for path in paths:
        if any(path.startswith(prefix) for prefix in ALWAYS_ALLOWED):
            continue
        hit = matches(path, forbidden)
        if hit:
            findings.append({"path": path, "verdict": "FORBIDDEN", "rule": hit})
            continue
        hit = matches(path, allowed)
        findings.append(
            {"path": path, "verdict": "allowed", "rule": hit}
            if hit
            else {"path": path, "verdict": "UNDECLARED", "rule": None}
        )

    violations = [f for f in findings if f["verdict"] != "allowed"]

    if args.json:
        print(
            json.dumps(
                {
                    "findings": findings,
                    "changed_outside_this_subtree": elsewhere,
                    "in_scope": not violations,
                },
                indent=2,
            )
        )
    else:
        for finding in findings:
            rule = f"  (matched: {finding['rule']})" if finding["rule"] else ""
            print(f"{finding['verdict']:>10}  {finding['path']}{rule}")
        print()
        if violations:
            print(f"{len(violations)} file(s) outside the plan's scope.")
            print(
                "Do not silently keep these. Either revert them, or stop and ask the user "
                "to widen the plan's Allowed scope — that decision is theirs."
            )
        elif findings:
            print(f"in scope: all {len(findings)} changed file(s) are covered by the plan.")
        else:
            print("nothing has changed in the working tree yet.")
        if elsewhere:
            print(
                f"note: {elsewhere} change(s) elsewhere in the repository were not checked — "
                "this plan is scoped to a subproject."
            )

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
