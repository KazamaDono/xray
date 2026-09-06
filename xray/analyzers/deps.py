from __future__ import annotations

import json
import re
from pathlib import Path


def analyze_deps(root: Path) -> dict:
    result: dict = {
        "managers": [],
        "dependencies": [],
        "dev_dependencies": [],
        "total_deps": 0,
        "total_dev_deps": 0,
        "has_lockfile": False,
        "outdated_signals": [],
    }

    if (root / "package.json").exists():
        _parse_package_json(root, result)
    if (root / "requirements.txt").exists():
        _parse_requirements_txt(root, result)
    if (root / "pyproject.toml").exists():
        _parse_pyproject(root, result)
    if (root / "Cargo.toml").exists():
        _parse_cargo(root, result)
    if (root / "go.mod").exists():
        _parse_go_mod(root, result)
    if (root / "Gemfile").exists():
        _parse_gemfile(root, result)
    if (root / "composer.json").exists():
        _parse_composer(root, result)

    lockfiles = [
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
        "Pipfile.lock", "poetry.lock", "pdm.lock", "uv.lock",
        "Cargo.lock", "go.sum", "Gemfile.lock", "composer.lock",
    ]
    for lf in lockfiles:
        if (root / lf).exists():
            result["has_lockfile"] = True
            break

    result["total_deps"] = len(result["dependencies"])
    result["total_dev_deps"] = len(result["dev_dependencies"])

    return result


def _parse_package_json(root: Path, result: dict):
    try:
        data = json.loads((root / "package.json").read_text())
    except (json.JSONDecodeError, OSError):
        return

    result["managers"].append("npm/node")

    deps = data.get("dependencies", {})
    dev_deps = data.get("devDependencies", {})

    for name, version in list(deps.items())[:50]:
        result["dependencies"].append(f"{name}@{version}")

    for name, version in list(dev_deps.items())[:50]:
        result["dev_dependencies"].append(f"{name}@{version}")


def _parse_requirements_txt(root: Path, result: dict):
    try:
        lines = (root / "requirements.txt").read_text().splitlines()
    except OSError:
        return

    result["managers"].append("pip")

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        result["dependencies"].append(line.split("#")[0].strip())
        if len(result["dependencies"]) > 100:
            break


def _parse_pyproject(root: Path, result: dict):
    try:
        content = (root / "pyproject.toml").read_text()
    except OSError:
        return

    if "pip" not in [m for m in result["managers"]]:
        result["managers"].append("pip/pyproject")

    in_deps = False
    in_dev = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "dependencies = [":
            in_deps = True
            continue
        if "[tool.poetry.dependencies]" in stripped:
            in_deps = True
            continue
        if any(x in stripped for x in ["[tool.poetry.group.dev", "[project.optional-dependencies]"]):
            in_dev = True
            in_deps = False
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            in_deps = False
            in_dev = False
            continue

        if in_deps and stripped.startswith('"'):
            dep = stripped.strip('",').strip()
            if dep:
                result["dependencies"].append(dep)
        elif in_dev and stripped.startswith('"'):
            dep = stripped.strip('",').strip()
            if dep:
                result["dev_dependencies"].append(dep)


def _parse_cargo(root: Path, result: dict):
    try:
        content = (root / "Cargo.toml").read_text()
    except OSError:
        return

    result["managers"].append("cargo")

    in_deps = False
    in_dev = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "[dependencies]":
            in_deps = True
            in_dev = False
            continue
        if stripped == "[dev-dependencies]":
            in_dev = True
            in_deps = False
            continue
        if stripped.startswith("["):
            in_deps = False
            in_dev = False
            continue

        m = re.match(r'^(\w[\w-]*)\s*=', stripped)
        if m:
            name = m.group(1)
            if in_deps:
                result["dependencies"].append(name)
            elif in_dev:
                result["dev_dependencies"].append(name)


def _parse_go_mod(root: Path, result: dict):
    try:
        content = (root / "go.mod").read_text()
    except OSError:
        return

    result["managers"].append("go modules")

    in_require = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "require (":
            in_require = True
            continue
        if stripped == ")":
            in_require = False
            continue
        if in_require and stripped and not stripped.startswith("//"):
            parts = stripped.split()
            if len(parts) >= 2:
                result["dependencies"].append(f"{parts[0]}@{parts[1]}")


def _parse_gemfile(root: Path, result: dict):
    try:
        lines = (root / "Gemfile").read_text().splitlines()
    except OSError:
        return

    result["managers"].append("bundler")

    for line in lines:
        m = re.match(r"""^\s*gem\s+['"]([\w-]+)['"]""", line)
        if m:
            result["dependencies"].append(m.group(1))


def _parse_composer(root: Path, result: dict):
    try:
        data = json.loads((root / "composer.json").read_text())
    except (json.JSONDecodeError, OSError):
        return

    result["managers"].append("composer")

    for name in list(data.get("require", {}).keys())[:50]:
        if name != "php":
            result["dependencies"].append(name)

    for name in list(data.get("require-dev", {}).keys())[:50]:
        result["dev_dependencies"].append(name)
