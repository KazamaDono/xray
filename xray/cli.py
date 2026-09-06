from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from rich.console import Console

from xray import __version__
from xray.analyzers.identity import analyze_identity
from xray.analyzers.structure import analyze_structure
from xray.analyzers.entry import analyze_entry_points
from xray.analyzers.health import analyze_health
from xray.analyzers.deps import analyze_deps
from xray.analyzers.git_info import analyze_git
from xray.analyzers.commands import analyze_commands
from xray.output import render, render_json


def main():
    parser = argparse.ArgumentParser(
        prog="xray",
        description="See through any codebase. Instant project intelligence from your terminal.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Path to project root (default: current directory)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show extended details")
    parser.add_argument("-q", "--quiet", action="store_true", help="Minimal output")
    parser.add_argument("--json", dest="json_output", action="store_true", help="Output as JSON")
    parser.add_argument("--no-banner", action="store_true", help="Skip the ASCII banner")
    parser.add_argument("--no-git", action="store_true", help="Skip git analysis")
    parser.add_argument("--version", action="version", version=f"xray {__version__}")

    args = parser.parse_args()
    root = Path(args.path).resolve()

    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    console = Console(stderr=True) if args.json_output else Console()

    if not args.json_output and not args.quiet:
        console.print(f"[dim]Scanning {root}...[/dim]")

    start = time.time()

    data: dict = {}
    data["identity"] = analyze_identity(root)
    data["structure"] = analyze_structure(root)
    data["entry"] = analyze_entry_points(root)
    data["health"] = analyze_health(root)
    data["deps"] = analyze_deps(root)
    if not args.no_git:
        data["git"] = analyze_git(root)
    data["commands"] = analyze_commands(root)

    elapsed = time.time() - start
    data["_meta"] = {
        "path": str(root),
        "scan_time": round(elapsed, 2),
        "version": __version__,
    }

    if args.json_output:
        out = Console()
        render_json(data, out)
    else:
        render(data, console, verbose=args.verbose)
        if not args.quiet:
            console.print(f"[dim]Scanned in {elapsed:.2f}s[/dim]\n")


if __name__ == "__main__":
    main()
