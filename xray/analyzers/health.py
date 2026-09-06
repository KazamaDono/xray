from __future__ import annotations

import os
import re
from collections import Counter
from pathlib import Path

from .identity import SKIP_DIRS


def analyze_health(root: Path) -> dict:
    todos: list[tuple[str, int, str]] = []
    fixmes: list[tuple[str, int, str]] = []
    hacks: list[tuple[str, int, str]] = []
    test_files = 0
    test_dirs: list[str] = []
    has_type_checking = False
    has_linting = False
    has_formatting = False
    has_pre_commit = False
    has_ci = False
    readme_exists = (root / "README.md").exists() or (root / "readme.md").exists()
    license_exists = (root / "LICENSE").exists() or (root / "LICENSE.md").exists() or (root / "LICENCE").exists()
    changelog_exists = (root / "CHANGELOG.md").exists() or (root / "CHANGES.md").exists() or (root / "HISTORY.md").exists()

    todo_re = re.compile(r"#.*\bTODO\b[:\s]*(.*)", re.I)
    fixme_re = re.compile(r"#.*\bFIXME\b[:\s]*(.*)", re.I)
    hack_re = re.compile(r"#.*\bHACK\b[:\s]*(.*)", re.I)

    code_exts = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".rb",
                 ".java", ".kt", ".c", ".cpp", ".h", ".cs", ".php", ".swift"}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS
            and not d.startswith(".")
            and not (Path(dirpath) / d / "pyvenv.cfg").exists()
            and d != "site-packages"
        ]
        rel_dir = os.path.relpath(dirpath, root)

        if any(t in Path(dirpath).name.lower() for t in ("test", "spec", "__tests__")):
            test_dirs.append(rel_dir)

        for fname in filenames:
            lower = fname.lower()
            ext = Path(fname).suffix.lower()

            if "test" in lower or "spec" in lower:
                if ext in code_exts:
                    test_files += 1

            if ext not in code_exts:
                continue

            full = os.path.join(dirpath, fname)
            rel = os.path.join(rel_dir, fname) if rel_dir != "." else fname
            try:
                with open(full, "r", errors="replace") as f:
                    for line_num, line in enumerate(f, 1):
                        if line_num > 5000:
                            break
                        m = todo_re.search(line)
                        if m:
                            todos.append((rel, line_num, m.group(1).strip()[:80]))
                        m = fixme_re.search(line)
                        if m:
                            fixmes.append((rel, line_num, m.group(1).strip()[:80]))
                        m = hack_re.search(line)
                        if m:
                            hacks.append((rel, line_num, m.group(1).strip()[:80]))
            except (OSError, PermissionError):
                continue

    type_check_signals = [
        "tsconfig.json", "mypy.ini", ".mypy.ini", "pyrightconfig.json",
        "pyproject.toml",
    ]
    for s in type_check_signals:
        p = root / s
        if p.exists():
            if s == "pyproject.toml":
                try:
                    content = p.read_text()
                    if "[tool.mypy]" in content or "[tool.pyright]" in content:
                        has_type_checking = True
                except OSError:
                    pass
            else:
                has_type_checking = True
                break

    if (root / "tsconfig.json").exists():
        has_type_checking = True

    lint_signals = [
        ".eslintrc.js", ".eslintrc.json", ".eslintrc.yml", "eslint.config.js",
        "eslint.config.mjs", ".flake8", "ruff.toml",
    ]
    for s in lint_signals:
        if (root / s).exists():
            has_linting = True
            break
    if not has_linting and (root / "pyproject.toml").exists():
        try:
            content = (root / "pyproject.toml").read_text()
            if "[tool.ruff]" in content or "[tool.flake8]" in content or "[tool.pylint]" in content:
                has_linting = True
        except OSError:
            pass

    fmt_signals = [
        ".prettierrc", ".prettierrc.json", "prettier.config.js",
        "rustfmt.toml", ".clang-format",
    ]
    for s in fmt_signals:
        if (root / s).exists():
            has_formatting = True
            break
    if not has_formatting and (root / "pyproject.toml").exists():
        try:
            content = (root / "pyproject.toml").read_text()
            if "[tool.black]" in content or "ruff format" in content:
                has_formatting = True
        except OSError:
            pass

    has_pre_commit = (root / ".pre-commit-config.yaml").exists()
    has_ci = (root / ".github" / "workflows").is_dir() or (root / ".gitlab-ci.yml").exists()

    return {
        "todos": todos[:20],
        "fixmes": fixmes[:20],
        "hacks": hacks[:10],
        "todo_count": len(todos),
        "fixme_count": len(fixmes),
        "hack_count": len(hacks),
        "test_files": test_files,
        "test_dirs": test_dirs[:10],
        "has_type_checking": has_type_checking,
        "has_linting": has_linting,
        "has_formatting": has_formatting,
        "has_pre_commit": has_pre_commit,
        "has_ci": has_ci,
        "readme": readme_exists,
        "license": license_exists,
        "changelog": changelog_exists,
    }
