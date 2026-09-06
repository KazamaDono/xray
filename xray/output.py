from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns

BANNER = r"""

  \_  _/  |__|  /--\  \_  _/
    \/   |    | |    |   \/
   /  \  |    | |    |  /  \
  /    \ |    |  \--/  /    \

"""


def render(data: dict, console: Console, verbose: bool = False):
    console.print(Text(BANNER, style="bold green"))
    console.print("  [dim]See through any codebase.[/dim]\n")

    _render_identity(data.get("identity", {}), console)
    _render_structure(data.get("structure", {}), console)
    _render_entry(data.get("entry", {}), console, verbose)
    _render_health(data.get("health", {}), console, verbose)
    _render_deps(data.get("deps", {}), console, verbose)
    _render_git(data.get("git", {}), console, verbose)
    _render_commands(data.get("commands", {}), console)


def _section(title: str, console: Console, content, border: str = "cyan"):
    console.print(Panel(content, title=Text(f" {title} ", style="bold"), border_style=border, padding=(0, 1)))
    console.print()


def _render_identity(d: dict, console: Console):
    if not d:
        return

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold cyan", min_width=18)
    table.add_column()

    langs = d.get("languages", [])
    if langs:
        lang_str = ", ".join(f"{name} ({count})" for name, count in langs)
        table.add_row("Languages", lang_str)

    if d.get("primary_language"):
        table.add_row("Primary", Text(d["primary_language"], style="bold green"))

    if d.get("framework"):
        table.add_row("Framework", Text(d["framework"], style="bold yellow"))

    if d.get("build_tool"):
        table.add_row("Build Tool", d["build_tool"])

    if d.get("package_manager"):
        table.add_row("Package Manager", d["package_manager"])

    if d.get("ci"):
        table.add_row("CI/CD", d["ci"])

    if d.get("docker"):
        table.add_row("Docker", "yes")

    if d.get("monorepo"):
        table.add_row("Monorepo", d["monorepo"])

    table.add_row("Total Files", str(d.get("total_files", 0)))

    _section("Identity", console, table)


def _render_structure(d: dict, console: Console):
    if not d:
        return

    lines = Text()

    top_dirs = d.get("top_dirs", [])
    if top_dirs:
        for name, count in top_dirs:
            lines.append(f"  {name}/", style="bold cyan")
            lines.append(f"  ({count} files)\n", style="dim")
        lines.append("\n")

    loc = d.get("loc_by_language", [])
    if loc:
        lines.append("  Lines of code:\n", style="bold")
        for lang, count in loc:
            bar_len = min(int(count / max(loc[0][1], 1) * 30), 30)
            bar = "#" * bar_len
            lines.append(f"    {lang:<14} ", style="cyan")
            lines.append(f"{bar} ", style="green")
            lines.append(f"{count:>8,}\n")
        lines.append(f"\n    Total: {d.get('total_loc', 0):,} lines\n")

    cats = d.get("category_counts", {})
    if cats:
        lines.append("\n  File categories:\n", style="bold")
        for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
            lines.append(f"    {cat:<12} {count:>6}\n")

    _section("Structure", console, lines)


def _render_entry(d: dict, console: Console, verbose: bool):
    if not d:
        return

    lines = Text()

    mains = d.get("main_files", [])
    if mains:
        lines.append("  Entry points:\n", style="bold")
        for m in mains[:10]:
            lines.append(f"    > {m}\n", style="green")
        lines.append("\n")

    routes = d.get("routes", [])
    if routes:
        lines.append("  Routes:\n", style="bold")
        limit = 20 if verbose else 8
        for r in routes[:limit]:
            lines.append(f"    {r}\n", style="yellow")
        if len(routes) > limit:
            lines.append(f"    ... and {len(routes) - limit} more\n", style="dim")
        lines.append("\n")

    apis = d.get("api_endpoints", [])
    if apis:
        lines.append("  API endpoints:\n", style="bold")
        for a in apis[:10]:
            lines.append(f"    {a}\n", style="yellow")

    configs = d.get("config_files", [])
    if configs:
        lines.append("  Config files:\n", style="bold")
        for c in configs[:15]:
            lines.append(f"    {c}\n", style="dim")

    if not str(lines).strip():
        return

    _section("Entry Points", console, lines)


def _render_health(d: dict, console: Console, verbose: bool):
    if not d:
        return

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(min_width=18)
    table.add_column()

    checks = [
        ("README", d.get("readme", False)),
        ("LICENSE", d.get("license", False)),
        ("CHANGELOG", d.get("changelog", False)),
        ("Type Checking", d.get("has_type_checking", False)),
        ("Linting", d.get("has_linting", False)),
        ("Formatting", d.get("has_formatting", False)),
        ("Pre-commit", d.get("has_pre_commit", False)),
        ("CI/CD", d.get("has_ci", False)),
    ]

    for name, ok in checks:
        icon = Text("*", style="green") if ok else Text("-", style="red")
        label = Text(name, style="green" if ok else "red")
        table.add_row(icon, label)

    table.add_row("", "")
    table.add_row(Text("Test files", style="bold"), str(d.get("test_files", 0)))
    table.add_row(Text("TODOs", style="yellow"), str(d.get("todo_count", 0)))
    table.add_row(Text("FIXMEs", style="red"), str(d.get("fixme_count", 0)))
    table.add_row(Text("HACKs", style="red"), str(d.get("hack_count", 0)))

    _section("Health", console, table)

    if verbose:
        todos = d.get("todos", [])
        if todos:
            lines = Text()
            for path, line_num, msg in todos[:10]:
                lines.append(f"  {path}:{line_num}", style="dim")
                lines.append(f"  {msg}\n", style="yellow")
            _section("TODOs", console, lines, "yellow")


def _render_deps(d: dict, console: Console, verbose: bool):
    if not d or not d.get("managers"):
        return

    lines = Text()
    lines.append(f"  Managers: {', '.join(d.get('managers', []))}\n", style="bold")
    lines.append(f"  Dependencies: {d.get('total_deps', 0)}\n")
    lines.append(f"  Dev dependencies: {d.get('total_dev_deps', 0)}\n")

    if d.get("has_lockfile"):
        lines.append("  Lockfile: ", style="")
        lines.append("present\n", style="green")
    else:
        lines.append("  Lockfile: ", style="")
        lines.append("missing\n", style="red")

    if verbose:
        deps = d.get("dependencies", [])
        if deps:
            lines.append("\n  Dependencies:\n", style="bold")
            for dep in deps[:20]:
                lines.append(f"    {dep}\n", style="dim")
            if len(deps) > 20:
                lines.append(f"    ... and {len(deps) - 20} more\n", style="dim")

    _section("Dependencies", console, lines)


def _render_git(d: dict, console: Console, verbose: bool):
    if not d or not d.get("is_git"):
        return

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold cyan", min_width=18)
    table.add_column()

    if d.get("branch"):
        table.add_row("Branch", Text(d["branch"], style="bold green"))

    table.add_row("Total Commits", str(d.get("total_commits", 0)))
    table.add_row("Branches", str(d.get("branch_count", 0)))

    if d.get("first_commit"):
        table.add_row("First Commit", d["first_commit"])
    if d.get("latest_commit"):
        table.add_row("Latest Commit", d["latest_commit"])

    changes = d.get("uncommitted_changes", 0)
    if changes > 0:
        table.add_row("Uncommitted", Text(str(changes), style="yellow"))

    if d.get("tags"):
        table.add_row("Latest Tags", ", ".join(d["tags"][:5]))

    _section("Git", console, table)

    contributors = d.get("contributors", [])
    if contributors:
        lines = Text()
        for name, count in contributors[:10]:
            lines.append(f"  {name}", style="bold")
            lines.append(f"  ({count} commits)\n", style="dim")
        _section("Contributors", console, lines, "blue")

    if verbose:
        hot = d.get("hot_files", [])
        if hot:
            lines = Text()
            for path, count in hot:
                lines.append(f"  {path}", style="yellow")
                lines.append(f"  ({count} changes)\n", style="dim")
            _section("Hot Files", console, lines, "yellow")

        commits = d.get("recent_commits", "")
        if commits:
            lines = Text()
            for line in commits.strip().splitlines()[:10]:
                lines.append(f"  {line}\n", style="dim")
            _section("Recent Commits", console, lines, "blue")


def _render_commands(d: dict, console: Console):
    if not d:
        return

    has_content = False
    lines = Text()

    npm = d.get("npm_scripts", [])
    if npm:
        has_content = True
        lines.append("  npm scripts:\n", style="bold")
        for name, cmd in npm[:15]:
            lines.append(f"    npm run {name}", style="green")
            lines.append(f"  {cmd}\n", style="dim")
        lines.append("\n")

    make = d.get("make_targets", [])
    if make:
        has_content = True
        lines.append("  make targets:\n", style="bold")
        for t in make[:15]:
            lines.append(f"    make {t}\n", style="green")
        lines.append("\n")

    just = d.get("just_recipes", [])
    if just:
        has_content = True
        lines.append("  just recipes:\n", style="bold")
        for r in just[:15]:
            lines.append(f"    just {r}\n", style="green")
        lines.append("\n")

    docker = d.get("docker_services", [])
    if docker:
        has_content = True
        lines.append("  docker-compose services:\n", style="bold")
        for s in docker:
            lines.append(f"    {s}\n", style="cyan")
        lines.append("\n")

    scripts = d.get("script_files", [])
    if scripts:
        has_content = True
        lines.append("  scripts:\n", style="bold")
        for s in scripts[:15]:
            lines.append(f"    ./{s}\n", style="green")

    if has_content:
        _section("Commands", console, lines)


def render_json(data: dict, console: Console):
    import json
    console.print_json(json.dumps(data, default=str))
