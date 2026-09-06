from __future__ import annotations

import os
import subprocess
from collections import Counter
from pathlib import Path


def analyze_git(root: Path) -> dict:
    if not (root / ".git").exists():
        return {"is_git": False}

    result: dict = {"is_git": True}

    result["recent_commits"] = _run_git(root, [
        "log", "--oneline", "--no-decorate", "-20"
    ])

    result["contributors"] = _get_contributors(root)
    result["branch"] = _run_git(root, ["branch", "--show-current"]).strip()

    branches_raw = _run_git(root, ["branch", "-a", "--no-color"])
    branches = [b.strip().lstrip("* ") for b in branches_raw.splitlines() if b.strip()]
    result["branch_count"] = len(branches)
    result["branches"] = branches[:15]

    result["hot_files"] = _get_hot_files(root)

    status_raw = _run_git(root, ["status", "--porcelain"])
    lines = [l for l in status_raw.splitlines() if l.strip()]
    result["uncommitted_changes"] = len(lines)
    result["dirty_files"] = [l.strip() for l in lines[:10]]

    first = _run_git(root, ["log", "--reverse", "--format=%ai", "-1"]).strip()
    latest = _run_git(root, ["log", "--format=%ai", "-1"]).strip()
    result["first_commit"] = first[:10] if first else None
    result["latest_commit"] = latest[:10] if latest else None

    total = _run_git(root, ["rev-list", "--count", "HEAD"]).strip()
    result["total_commits"] = int(total) if total.isdigit() else 0

    result["tags"] = _run_git(root, ["tag", "-l", "--sort=-version:refname"]).splitlines()[:10]

    remotes_raw = _run_git(root, ["remote", "-v"])
    remotes = set()
    for line in remotes_raw.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            remotes.add(f"{parts[0]} -> {parts[1]}")
    result["remotes"] = sorted(remotes)

    return result


def _get_contributors(root: Path) -> list[tuple[str, int]]:
    raw = _run_git(root, ["shortlog", "-sne", "--no-merges", "HEAD"])
    contributors = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2:
            count = parts[0].strip()
            name = parts[1].strip()
            if count.isdigit():
                contributors.append((name, int(count)))
    return contributors[:15]


def _get_hot_files(root: Path) -> list[tuple[str, int]]:
    raw = _run_git(root, [
        "log", "--pretty=format:", "--name-only", "-100", "--no-merges"
    ])
    counts: Counter[str] = Counter()
    for line in raw.splitlines():
        line = line.strip()
        if line:
            counts[line] += 1
    return counts.most_common(10)


def _run_git(root: Path, args: list[str]) -> str:
    try:
        r = subprocess.run(
            ["git"] + args,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return r.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""
