from __future__ import annotations

import os
from collections import Counter, defaultdict
from pathlib import Path

from .identity import LANG_MAP, SKIP_DIRS

CATEGORY_MAP = {
    "source": {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".rb", ".java",
               ".kt", ".scala", ".c", ".cpp", ".cc", ".h", ".hpp", ".cs", ".php",
               ".swift", ".lua", ".zig", ".ex", ".exs", ".hs", ".dart", ".vue",
               ".svelte", ".sol", ".mjs", ".cjs", ".pyx", ".pyi"},
    "test": set(),
    "config": {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
               ".env", ".xml", ".properties"},
    "docs": {".md", ".rst", ".txt", ".adoc"},
    "style": {".css", ".scss", ".sass", ".less", ".styl"},
    "template": {".html", ".htm", ".ejs", ".hbs", ".pug", ".jinja", ".j2", ".twig"},
    "data": {".sql", ".csv", ".tsv", ".parquet", ".sqlite", ".db"},
    "image": {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".bmp"},
    "other": set(),
}


def analyze_structure(root: Path) -> dict:
    tree: dict[str, list[str]] = defaultdict(list)
    lang_loc: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    total_dirs = 0
    total_files = 0
    largest_files: list[tuple[str, int]] = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames
            if d not in SKIP_DIRS
            and not d.startswith(".")
            and not (Path(dirpath) / d / "pyvenv.cfg").exists()
            and d != "site-packages"
        )
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            rel_dir = ""

        depth = rel_dir.count(os.sep) if rel_dir else 0
        if depth <= 2:
            total_dirs += 1
            for d in dirnames:
                if depth <= 1:
                    tree[rel_dir].append(d + "/")

        for fname in filenames:
            total_files += 1
            full_path = os.path.join(dirpath, fname)
            ext = Path(fname).suffix.lower()

            cat = _categorize(fname, ext, rel_dir)
            category_counts[cat] += 1

            if ext in LANG_MAP:
                try:
                    loc = _count_lines(full_path)
                    lang_loc[LANG_MAP[ext]] += loc
                except (OSError, PermissionError):
                    pass

            try:
                size = os.path.getsize(full_path)
                rel_path = os.path.join(rel_dir, fname) if rel_dir else fname
                largest_files.append((rel_path, size))
            except OSError:
                pass

    largest_files.sort(key=lambda x: x[1], reverse=True)
    top_dirs = _get_top_dirs(root)

    return {
        "tree": dict(tree),
        "top_dirs": top_dirs,
        "total_dirs": total_dirs,
        "total_files": total_files,
        "loc_by_language": lang_loc.most_common(10),
        "total_loc": sum(lang_loc.values()),
        "category_counts": dict(category_counts),
        "largest_files": largest_files[:10],
    }


def _categorize(fname: str, ext: str, rel_dir: str) -> str:
    lower = fname.lower()
    if "test" in lower or "spec" in lower or rel_dir.startswith("test") or "/test" in rel_dir:
        return "test"
    for cat, exts in CATEGORY_MAP.items():
        if ext in exts:
            return cat
    return "other"


def _count_lines(path: str) -> int:
    count = 0
    try:
        with open(path, "r", errors="replace") as f:
            for _ in f:
                count += 1
    except (OSError, PermissionError):
        pass
    return count


def _get_top_dirs(root: Path) -> list[tuple[str, int]]:
    counts: Counter[str] = Counter()
    for item in root.iterdir():
        if (item.is_dir()
            and item.name not in SKIP_DIRS
            and not item.name.startswith(".")
            and not (item / "pyvenv.cfg").exists()
            and item.name != "site-packages"):
            count = _count_files_recursive(item)
            counts[item.name] = count
    return counts.most_common(10)


def _count_files_recursive(path: Path) -> int:
    count = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            dirnames[:] = [
                d for d in dirnames
                if d not in SKIP_DIRS
                and not d.startswith(".")
                and not (Path(dirpath) / d / "pyvenv.cfg").exists()
                and d != "site-packages"
            ]
            count += len(filenames)
    except PermissionError:
        pass
    return count
