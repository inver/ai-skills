#!/usr/bin/env python3
"""Verify that every `path:line` citation in a report points at a line that exists.

An audit report is only as trustworthy as its citations, and line numbers written from memory are the
most common way a report goes wrong. This checks the cheap, mechanical part: the file exists (matched by
path suffix, so `web/Foo.java:12` and bare `Foo.java:12` both work) and has at least that many lines. It
cannot check that the cited line *says* what the report claims -- re-read the code for that.

Usage:
    check_citations.py <report.md | -> [--repo <root>] [--format text|json]   (- reads the report from stdin)

Exit status: 0 when every citation resolves, 1 when any does not, 2 on usage error.
Ranges (`Foo.java:10-40`) are checked at their upper bound; `:12,30` style lists are checked per number.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

SKIP_DIRS = {".git", "node_modules", "build", "target", "dist", "out", ".gradle", ".idea", "__pycache__", ".venv", "venv"}
EXT = r"java|kt|kts|tsx?|jsx?|py|ya?ml|xml|sql|gradle|properties|md|json|toml"
# path:12  path:12-40  path:12,30,45  (the path must carry an extension)
CITE = re.compile(rf"([\w./@-]+\.(?:{EXT})):(\d+(?:[-,]\d+)*)")


def repo_root(given: str | None) -> str:
    if given:
        return os.path.abspath(given)
    try:
        return subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return os.getcwd()


def index_files(root: str) -> dict[str, list[str]]:
    idx: dict[str, list[str]] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            idx.setdefault(fn, []).append(os.path.join(dirpath, fn))
    return idx


def line_count(path: str) -> int:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report")
    ap.add_argument("--repo", help="repo root (default: git toplevel, else cwd)")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    a = ap.parse_args()
    if a.report != "-" and not os.path.isfile(a.report):
        print(f"error: {a.report} not found", file=sys.stderr)
        return 2

    root = repo_root(a.repo)
    idx = index_files(root)
    text = sys.stdin.read() if a.report == "-" else open(a.report, encoding="utf-8", errors="replace").read()

    cites: set[tuple[str, int]] = set()
    for path, nums in CITE.findall(text):
        for part in nums.split(","):
            cites.add((path, int(part.split("-")[-1])))

    counts: dict[str, int] = {}
    bad: list[dict] = []
    for path, line in sorted(cites):
        candidates = [p for p in idx.get(os.path.basename(path), []) if p.replace(os.sep, "/").endswith(path.lstrip("./"))]
        if not candidates:
            bad.append({"cite": f"{path}:{line}", "reason": "file not found"})
            continue
        best = max(counts.setdefault(p, line_count(p)) for p in candidates)
        if line < 1 or line > best:
            bad.append({"cite": f"{path}:{line}", "reason": f"file has {best} lines"})

    result = {"total": len(cites), "valid": len(cites) - len(bad), "invalid": bad}
    if a.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['valid']}/{result['total']} citations resolve")
        for b in bad:
            print(f"  BAD  {b['cite']}  ({b['reason']})")
        if bad:
            print("Fix or remove these before finalising the report: re-open each file and cite the real line.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
