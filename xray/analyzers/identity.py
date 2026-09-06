from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path

LANG_MAP = {
    ".py": "Python", ".pyx": "Python", ".pyi": "Python",
    ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".jsx": "JavaScript",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby", ".erb": "Ruby",
    ".java": "Java", ".kt": "Kotlin", ".scala": "Scala",
    ".c": "C", ".h": "C",
    ".cpp": "C++", ".cc": "C++", ".cxx": "C++", ".hpp": "C++",
    ".cs": "C#",
    ".php": "PHP",
    ".swift": "Swift",
    ".lua": "Lua",
    ".zig": "Zig",
    ".ex": "Elixir", ".exs": "Elixir",
    ".hs": "Haskell",
    ".dart": "Dart",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".sol": "Solidity",
}

FRAMEWORK_SIGNALS: list[tuple[str, str, str]] = [
    ("next.config.js", "JavaScript", "Next.js"),
    ("next.config.mjs", "JavaScript", "Next.js"),
    ("next.config.ts", "TypeScript", "Next.js"),
    ("nuxt.config.ts", "TypeScript", "Nuxt"),
    ("nuxt.config.js", "JavaScript", "Nuxt"),
    ("svelte.config.js", "JavaScript", "SvelteKit"),
    ("astro.config.mjs", "JavaScript", "Astro"),
    ("remix.config.js", "JavaScript", "Remix"),
    ("angular.json", "TypeScript", "Angular"),
    ("gatsby-config.js", "JavaScript", "Gatsby"),
    ("vite.config.ts", "TypeScript", "Vite"),
    ("vite.config.js", "JavaScript", "Vite"),
    ("webpack.config.js", "JavaScript", "Webpack"),
    ("manage.py", "Python", "Django"),
    ("settings.py", "Python", "Django"),
    ("wsgi.py", "Python", "Django"),
    ("app.py", "Python", "Flask"),
    ("fastapi", "Python", "FastAPI"),
    ("Cargo.toml", "Rust", "Cargo"),
    ("go.mod", "Go", "Go Modules"),
    ("Gemfile", "Ruby", "Bundler"),
    ("config/routes.rb", "Ruby", "Rails"),
    ("pom.xml", "Java", "Maven"),
    ("build.gradle", "Java", "Gradle"),
    ("build.gradle.kts", "Kotlin", "Gradle"),
    ("composer.json", "PHP", "Composer"),
    ("artisan", "PHP", "Laravel"),
    ("pubspec.yaml", "Dart", "Flutter/Dart"),
    ("CMakeLists.txt", "C++", "CMake"),
]

BUILD_TOOLS: list[tuple[str, str]] = [
    ("Makefile", "Make"),
    ("Justfile", "Just"),
    ("Taskfile.yml", "Task"),
]

PACKAGE_MANAGERS = {
    "package-lock.json": "npm",
    "yarn.lock": "Yarn",
    "pnpm-lock.yaml": "pnpm",
    "bun.lockb": "Bun",
    "requirements.txt": "pip",
    "Pipfile.lock": "Pipenv",
    "poetry.lock": "Poetry",
    "pdm.lock": "PDM",
    "uv.lock": "uv",
    "Cargo.lock": "Cargo",
    "go.sum": "Go Modules",
    "Gemfile.lock": "Bundler",
    "composer.lock": "Composer",
    "pubspec.lock": "pub",
}

CI_SIGNALS = {
    ".github/workflows": "GitHub Actions",
    ".gitlab-ci.yml": "GitLab CI",
    "Jenkinsfile": "Jenkins",
    ".circleci": "CircleCI",
    ".travis.yml": "Travis CI",
    "bitbucket-pipelines.yml": "Bitbucket Pipelines",
    ".buildkite": "Buildkite",
}

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", "env",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build", ".next",
    ".nuxt", "target", "vendor", ".cargo", "coverage", ".cache",
    ".gradle", ".idea", ".vscode", "bin", "obj", ".terraform",
    "out", ".output", ".turbo", ".svelte-kit",
}


def analyze_identity(root: Path) -> dict:
    file_counts: Counter[str] = Counter()
    lang_counts: Counter[str] = Counter()
    total_files = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS
            and not d.startswith(".")
            and not (Path(dirpath) / d / "pyvenv.cfg").exists()
            and d != "site-packages"
        ]
        for fname in filenames:
            total_files += 1
            ext = Path(fname).suffix.lower()
            if ext in LANG_MAP:
                lang = LANG_MAP[ext]
                lang_counts[lang] += 1
                file_counts[ext] += 1

    languages = lang_counts.most_common(5)
    primary_lang = languages[0][0] if languages else None

    framework = _detect_framework(root, primary_lang)
    build_tool = _detect_build_tool(root)
    pkg_manager = _detect_package_manager(root)
    ci = _detect_ci(root)
    has_docker = (root / "Dockerfile").exists() or (root / "docker-compose.yml").exists() or (root / "docker-compose.yaml").exists()
    has_monorepo = _detect_monorepo(root)

    return {
        "languages": languages,
        "primary_language": primary_lang,
        "framework": framework,
        "build_tool": build_tool,
        "package_manager": pkg_manager,
        "ci": ci,
        "docker": has_docker,
        "monorepo": has_monorepo,
        "total_files": total_files,
        "file_counts": file_counts.most_common(10),
    }


def _detect_framework(root: Path, primary_lang: str | None) -> str | None:
    for signal_path, lang, framework in FRAMEWORK_SIGNALS:
        if (root / signal_path).exists():
            return framework

    if primary_lang == "Python":
        reqs = _read_text(root / "requirements.txt") + _read_text(root / "pyproject.toml")
        if "fastapi" in reqs.lower():
            return "FastAPI"
        if "flask" in reqs.lower():
            return "Flask"
        if "django" in reqs.lower():
            return "Django"
        if "streamlit" in reqs.lower():
            return "Streamlit"

    if primary_lang in ("JavaScript", "TypeScript"):
        pkg = _read_json(root / "package.json")
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        if "react" in deps and "next" not in deps:
            return "React"
        if "express" in deps:
            return "Express"
        if "fastify" in deps:
            return "Fastify"
        if "hono" in deps:
            return "Hono"
        if "vue" in deps:
            return "Vue"

    return None


def _detect_build_tool(root: Path) -> str | None:
    for signal_path, name in BUILD_TOOLS:
        if (root / signal_path).exists():
            return name
    return None


def _detect_package_manager(root: Path) -> str | None:
    for lockfile, name in PACKAGE_MANAGERS.items():
        if (root / lockfile).exists():
            return name
    if (root / "package.json").exists():
        return "npm"
    if (root / "pyproject.toml").exists():
        return "pip"
    return None


def _detect_ci(root: Path) -> str | None:
    for path, name in CI_SIGNALS.items():
        if (root / path).exists():
            return name
    return None


def _detect_monorepo(root: Path) -> str | None:
    if (root / "lerna.json").exists():
        return "Lerna"
    if (root / "pnpm-workspace.yaml").exists():
        return "pnpm workspaces"
    if (root / "turbo.json").exists():
        return "Turborepo"
    if (root / "nx.json").exists():
        return "Nx"
    pkg = _read_json(root / "package.json")
    if pkg.get("workspaces"):
        return "npm workspaces"
    return None


def _read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except (OSError, PermissionError):
        return ""


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError, PermissionError):
        return {}
