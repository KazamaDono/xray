<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=32&duration=3000&pause=1000&color=00FF41&center=true&vCenter=true&repeat=false&width=200&height=60&lines=xray" alt="xray" />

**See through any codebase.**

<sub>Clone a repo. Run one command. Understand everything.</sub>

<br>

[![Python](https://img.shields.io/badge/Python_3.9+-14354C?style=for-the-badge&logo=python&logoColor=ffd343)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-0d1117?style=for-the-badge&logoColor=00ff41)](LICENSE)
[![Platform](https://img.shields.io/badge/Linux_|_macOS-0d1117?style=for-the-badge&logo=linux&logoColor=00ff41)](https://github.com/KazamaDono/xray)

---

<img src="demo.gif" alt="xray demo" width="720" />

</div>

<br>

## `> cat problem.txt`

Every time you clone a repo, you spend 10-15 minutes doing the same thing: reading the README (if it exists), checking `package.json`, looking for a `Makefile`, reading `pyproject.toml`, running `git log`, opening `docker-compose.yml`. You're mentally stitching together the same picture every single time.

**xray does it in under a second.**

One command gives you the full picture: what the project is built with, how it's structured, where the entry points are, how healthy the codebase is, what commands you can run, and who's been working on it.

---

## `> xray --architecture`

```mermaid
graph LR
    A["xray CLI"] --> B["Analyzers"]
    B --> C["Identity"]
    B --> D["Structure"]
    B --> E["Entry Points"]
    B --> F["Health"]
    B --> G["Dependencies"]
    B --> H["Git"]
    B --> I["Commands"]
    
    C --> J["Output Engine"]
    D --> J
    E --> J
    F --> J
    G --> J
    H --> J
    I --> J
    
    J --> K["Rich Terminal"]
    J --> L["JSON"]

    style A fill:#0d1117,stroke:#00ff41,color:#00ff41
    style B fill:#0d1117,stroke:#00ff41,color:#00ff41
    style J fill:#0d1117,stroke:#00ff41,color:#00ff41
    style K fill:#0d1117,stroke:#58a6ff,color:#58a6ff
    style L fill:#0d1117,stroke:#58a6ff,color:#58a6ff
    style C fill:#161b22,stroke:#30363d,color:#c9d1d9
    style D fill:#161b22,stroke:#30363d,color:#c9d1d9
    style E fill:#161b22,stroke:#30363d,color:#c9d1d9
    style F fill:#161b22,stroke:#30363d,color:#c9d1d9
    style G fill:#161b22,stroke:#30363d,color:#c9d1d9
    style H fill:#161b22,stroke:#30363d,color:#c9d1d9
    style I fill:#161b22,stroke:#30363d,color:#c9d1d9
```

---

## `> xray --analyzers`

```mermaid
mindmap
  root((xray))
    Identity
      25+ Languages
      30+ Frameworks
      14 Package Managers
      7 CI Systems
      4 Monorepo Tools
      Docker Detection
    Structure
      Directory Layout
      LOC by Language
      File Categories
      Largest Files
    Entry Points
      Main Files
      API Routes
      Endpoints
      Config Files
    Health
      README / LICENSE
      Type Checking
      Linting / Formatting
      Pre-commit / CI
      TODOs / FIXMEs
      Test Coverage
    Dependencies
      All Managers
      Dep Counts
      Lockfile Check
    Git
      Branch Info
      Contributors
      Hot Files
      Commit History
      Tags / Remotes
    Commands
      npm Scripts
      Make Targets
      Just Recipes
      Docker Services
      Script Files
```

---

## `> pip install xray-cli`

```bash
pip install xray-cli
```

Or from source:

```bash
git clone https://github.com/KazamaDono/xray
cd xray
pip install -e .
```

---

## `> xray --help`

```
usage: xray [-h] [-v] [-q] [--json] [--no-banner] [--no-git] [--version] [path]

See through any codebase. Instant project intelligence from your terminal.

positional arguments:
  path          Path to project root (default: current directory)

options:
  -v, --verbose   Show extended details (routes, TODOs, hot files, deps list)
  -q, --quiet     Minimal output
  --json          Output as JSON (pipe to jq, feed to scripts)
  --no-banner     Skip the ASCII banner
  --no-git        Skip git analysis
  --version       Show version
```

---

## `> xray --examples`

```bash
# scan current directory
xray

# scan a specific project
xray ~/projects/my-app

# verbose mode -- all routes, every TODO, hot files, full dep list
xray -v

# json output -- pipe to jq, use in scripts, feed to other tools
xray --json | jq '.identity.primary_language'

# quick recon on something you just cloned
git clone https://github.com/someone/something && xray something

# compare two projects
diff <(xray projectA --json | jq '.identity') <(xray projectB --json | jq '.identity')

# check project health in CI
xray --json | jq -e '.health.has_linting and .health.has_type_checking'
```

---

## `> xray --what-it-finds`

<div align="center">

| Analyzer | What it detects |
|:---|:---|
| **Identity** | Primary language, framework (Next.js, Django, Rails, etc.), package manager, CI/CD system, Docker, monorepo tool |
| **Structure** | Top-level directory layout, lines of code per language with visual bars, file breakdown by category (source/test/config/docs/style) |
| **Entry Points** | Main files, CLI entry points, API routes (Express, FastAPI, Django, Flask, Spring), Next.js file-based routes, config files |
| **Health** | README, LICENSE, CHANGELOG presence. Type checking, linting, formatting, pre-commit hooks, CI/CD. TODO/FIXME/HACK counts with locations. Test file count |
| **Dependencies** | Parses package.json, requirements.txt, pyproject.toml, Cargo.toml, go.mod, Gemfile, composer.json. Counts deps vs dev-deps. Checks lockfile |
| **Git** | Current branch, total commits, contributor list with commit counts, most-changed files, tags, remotes, uncommitted changes, project age |
| **Commands** | npm/yarn scripts with their commands, Makefile targets, Justfile recipes, docker-compose services, executable scripts in bin/ scripts/ tools/ |

</div>

---

## `> xray --detection-matrix`

```mermaid
graph TD
    subgraph Languages["Languages -- 25+"]
        L1["Python"] ~~~ L2["TypeScript"] ~~~ L3["JavaScript"]
        L4["Go"] ~~~ L5["Rust"] ~~~ L6["Ruby"]
        L7["Java"] ~~~ L8["Kotlin"] ~~~ L9["C / C++"]
        L10["C#"] ~~~ L11["PHP"] ~~~ L12["Swift"]
        L13["Dart"] ~~~ L14["Elixir"] ~~~ L15["Zig"]
    end

    subgraph Frameworks["Frameworks -- 30+"]
        F1["Next.js / Nuxt / Astro"] ~~~ F2["React / Vue / Svelte"]
        F3["Django / Flask / FastAPI"] ~~~ F4["Express / Fastify / Hono"]
        F5["Rails / Laravel / Spring"] ~~~ F6["Flutter / CMake / Gradle"]
    end

    subgraph PackageManagers["Package Managers -- 14"]
        P1["npm / Yarn / pnpm / Bun"]
        P2["pip / Poetry / PDM / uv"]
        P3["Cargo / Go Modules"]
        P4["Bundler / Composer / pub"]
    end

    style Languages fill:#0d1117,stroke:#00ff41,color:#c9d1d9
    style Frameworks fill:#0d1117,stroke:#58a6ff,color:#c9d1d9
    style PackageManagers fill:#0d1117,stroke:#f0883e,color:#c9d1d9
```

---

## `> xray --json`

Every section is available as structured JSON. Pipe it, parse it, build on it.

```json
{
  "identity": {
    "primary_language": "TypeScript",
    "framework": "Next.js",
    "package_manager": "pnpm",
    "ci": "GitHub Actions",
    "docker": true,
    "monorepo": "Turborepo"
  },
  "structure": {
    "total_files": 1847,
    "total_loc": 132537,
    "loc_by_language": [["TypeScript", 89412], ["Python", 34891]]
  },
  "health": {
    "readme": true,
    "has_type_checking": true,
    "has_linting": true,
    "todo_count": 34,
    "fixme_count": 7,
    "test_files": 187
  },
  "git": {
    "total_commits": 1847,
    "branch": "main",
    "contributors": [["Sarah Chen", 634], ["Alex Rivera", 412]]
  },
  "_meta": {
    "scan_time": 0.34,
    "version": "1.0.0"
  }
}
```

---

## `> xray --design`

```
No config files. No setup. No API keys.
No network requests. Runs entirely offline.
No dependencies beyond Rich.
Single pip install. Works on Python 3.9+.

Intelligently skips virtual environments (detects pyvenv.cfg),
node_modules, __pycache__, .git, build artifacts, and 30+ other
generated directories so you see signal, not noise.

Scans a 3,000-file project in under a second.
```

---

<div align="center">

<sub>Built by <a href="https://github.com/KazamaDono">KazamaDono</a></sub>

</div>
