from __future__ import annotations

import json
import os
import re
from pathlib import Path


def analyze_commands(root: Path) -> dict:
    npm_scripts = _get_npm_scripts(root)
    make_targets = _get_make_targets(root)
    just_recipes = _get_just_recipes(root)
    docker_services = _get_docker_services(root)
    script_files = _find_scripts(root)

    return {
        "npm_scripts": npm_scripts,
        "make_targets": make_targets,
        "just_recipes": just_recipes,
        "docker_services": docker_services,
        "script_files": script_files,
    }


def _get_npm_scripts(root: Path) -> list[tuple[str, str]]:
    try:
        data = json.loads((root / "package.json").read_text())
        scripts = data.get("scripts", {})
        return [(k, v) for k, v in list(scripts.items())[:25]]
    except (json.JSONDecodeError, OSError):
        return []


def _get_make_targets(root: Path) -> list[str]:
    makefile = root / "Makefile"
    if not makefile.exists():
        return []
    try:
        content = makefile.read_text(errors="replace")
    except OSError:
        return []

    targets = []
    for m in re.finditer(r"^([a-zA-Z_][\w.-]*)\s*:", content, re.MULTILINE):
        target = m.group(1)
        if target not in ("PHONY", "FORCE", "SUFFIXES"):
            targets.append(target)
    return targets[:25]


def _get_just_recipes(root: Path) -> list[str]:
    justfile = root / "Justfile"
    if not justfile.exists():
        justfile = root / "justfile"
    if not justfile.exists():
        return []

    try:
        content = justfile.read_text(errors="replace")
    except OSError:
        return []

    recipes = []
    for m in re.finditer(r"^([a-zA-Z_][\w-]*)\s*(?:\(|:)", content, re.MULTILINE):
        recipes.append(m.group(1))
    return recipes[:25]


def _get_docker_services(root: Path) -> list[str]:
    for name in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"):
        path = root / name
        if path.exists():
            try:
                content = path.read_text(errors="replace")
            except OSError:
                continue
            services = []
            in_services = False
            for line in content.splitlines():
                stripped = line.strip()
                if stripped == "services:":
                    in_services = True
                    continue
                if in_services:
                    if not line.startswith(" ") and not line.startswith("\t") and stripped:
                        break
                    if line and (line[0] == " " or line[0] == "\t"):
                        indent = len(line) - len(line.lstrip())
                        if indent <= 4 and stripped.endswith(":") and not stripped.startswith("#"):
                            services.append(stripped[:-1])
            return services[:20]
    return []


def _find_scripts(root: Path) -> list[str]:
    script_dirs = ["scripts", "bin", "tools", "hack"]
    found = []

    for d in script_dirs:
        scripts_dir = root / d
        if scripts_dir.is_dir():
            try:
                for f in sorted(scripts_dir.iterdir()):
                    if f.is_file() and not f.name.startswith("."):
                        found.append(f"{d}/{f.name}")
            except PermissionError:
                continue

    for name in ("run.sh", "start.sh", "build.sh", "deploy.sh", "setup.sh", "install.sh",
                 "test.sh", "lint.sh", "dev.sh", "entrypoint.sh"):
        if (root / name).exists():
            found.append(name)

    return found[:25]
