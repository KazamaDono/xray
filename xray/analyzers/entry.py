from __future__ import annotations

import json
import os
import re
from pathlib import Path

from .identity import SKIP_DIRS


def analyze_entry_points(root: Path) -> dict:
    main_files = _find_main_files(root)
    config_files = _find_config_files(root)
    routes = _find_routes(root)
    api_endpoints = _find_api_patterns(root)

    return {
        "main_files": main_files,
        "config_files": config_files,
        "routes": routes[:30],
        "api_endpoints": api_endpoints[:30],
    }


def _find_main_files(root: Path) -> list[str]:
    targets = [
        "main.py", "app.py", "server.py", "index.py", "run.py", "manage.py", "wsgi.py",
        "main.go", "cmd/main.go",
        "main.rs", "src/main.rs", "src/lib.rs",
        "index.js", "index.ts", "server.js", "server.ts", "app.js", "app.ts",
        "src/index.js", "src/index.ts", "src/main.js", "src/main.ts",
        "src/App.tsx", "src/App.jsx", "src/app.tsx",
        "pages/index.tsx", "pages/index.js",
        "app/page.tsx", "app/page.js",
        "Main.java", "App.java",
        "Program.cs",
    ]
    found = []
    for t in targets:
        if (root / t).exists():
            found.append(t)

    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            if "main" in data:
                entry = data["main"]
                if (root / entry).exists():
                    found.append(f"{entry} (package.json main)")
        except (json.JSONDecodeError, OSError):
            pass

    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            for m in re.finditer(r'(\w+)\s*=\s*"([^"]+):(\w+)"', content):
                found.append(f"{m.group(1)} -> {m.group(2)}:{m.group(3)} (pyproject entry)")
        except OSError:
            pass

    return found


def _find_config_files(root: Path) -> list[str]:
    configs = [
        ".env", ".env.example", ".env.local",
        "tsconfig.json", "jsconfig.json",
        "eslint.config.js", ".eslintrc.js", ".eslintrc.json", ".eslintrc.yml",
        "prettier.config.js", ".prettierrc", ".prettierrc.json",
        "tailwind.config.js", "tailwind.config.ts",
        "postcss.config.js", "postcss.config.mjs",
        "babel.config.js", ".babelrc",
        "jest.config.js", "jest.config.ts", "vitest.config.ts",
        "pytest.ini", "setup.cfg", "tox.ini", "mypy.ini",
        ".flake8", "ruff.toml", "pyproject.toml",
        "rustfmt.toml", "clippy.toml",
        ".editorconfig", ".gitignore", ".gitattributes",
        ".dockerignore", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
        "Procfile", "vercel.json", "netlify.toml", "fly.toml",
        "terraform.tf", "serverless.yml",
    ]
    found = []
    for c in configs:
        if (root / c).exists():
            found.append(c)
    return found


def _find_routes(root: Path) -> list[str]:
    routes = []
    route_patterns = [
        re.compile(r'''@(?:app|router|api)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'"]+)''', re.I),
        re.compile(r'''router\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'"]+)''', re.I),
        re.compile(r'''@(?:Get|Post|Put|Delete|Patch|RequestMapping)\s*\(\s*['\"]([^'"]+)'''),
    ]

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext not in (".py", ".js", ".ts", ".tsx", ".java", ".go", ".rb"):
                continue
            full = os.path.join(dirpath, fname)
            rel = os.path.relpath(full, root)
            try:
                content = open(full, "r", errors="replace").read(50000)
            except (OSError, PermissionError):
                continue
            for pattern in route_patterns:
                for m in pattern.finditer(content):
                    groups = m.groups()
                    if len(groups) == 2:
                        method, path = groups
                        routes.append(f"{method.upper()} {path}  ({rel})")
                    else:
                        routes.append(f"{groups[0]}  ({rel})")
            if len(routes) > 50:
                break
    return routes


def _find_api_patterns(root: Path) -> list[str]:
    endpoints = []

    pages_api = root / "pages" / "api"
    if pages_api.is_dir():
        for f in pages_api.rglob("*"):
            if f.is_file() and f.suffix in (".js", ".ts", ".tsx"):
                rel = f.relative_to(root)
                route = "/api/" + str(f.relative_to(pages_api)).replace(f.suffix, "").replace("[", ":").replace("]", "")
                endpoints.append(f"{route}  ({rel})")

    app_api = root / "app" / "api"
    if app_api.is_dir():
        for f in app_api.rglob("route.*"):
            if f.is_file():
                rel = f.relative_to(root)
                route = "/api/" + str(f.parent.relative_to(app_api)).replace("[", ":").replace("]", "")
                endpoints.append(f"{route}  ({rel})")

    return endpoints
