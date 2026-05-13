---
name: do-prime
description: Prime agent with codebase understanding
argument-hint: scope (e.g. cli, sdk, server, full — defaults to full)
---

# Prime: Load Project Context

## Objective

Build understanding of the codebase, scoped to the area you will be working in. All package analysis runs in subagents to conserve the main context window. The main agent receives only structured summaries.

## Scope Selection

**Arguments provided**: $ARGUMENTS

Interpret the first token as the scope. If no argument is given, default to `full`.

**Project Structure**:
Read `AGENTS.md` (look for sections like "Project Structure", "Architecture", or "Repository Layout") to identify the available scopes and their corresponding paths.

**Rules for determining detail tiers**:
- Packages matching the scope get a **detailed** summary.
- Packages not in scope but adjacent (one layer away) get a **brief** summary.
- Packages two layers away get **minimal**.
- `full` = all packages get detailed summaries.

---

## Process

### Phase 1: Always Load (all scopes)

These are cheap and universally needed. Read them directly (no subagent).

1. Read `AGENTS.md` — skip if already loaded.
2. Read root configuration file (e.g. `Cargo.toml`, `pyproject.toml`, `package.json`).
3. Check current branch and status:
   !`git status`
4. Recent activity:
   !`git log -10 --oneline`
5. Top-level directory overview only:
   !`tree -L 2 -I 'target|.git|node_modules|__pycache__|dist|build'`

### Phase 2: Analyze Packages via Subagents

All package analysis runs in **Task (explore)** subagents — do NOT read package source files directly in the main context. Launch all subagent tasks in parallel.

Use the paths found in `AGENTS.md` to target the analysis.

**Detailed summary** (for focused/deep-read packages) — instruct the subagent:
> Analyze the package at `<package_path>`. Read all source files. Return a summary of 40-60 lines covering:
> - Purpose, responsibility, and how it fits in the overall system
> - Directory structure (run `tree` on the source directory, depth 3)
> - Every source file with a one-line description of its purpose
> - Public API surface: key classes/structs, functions, and their signatures
> - Data models/types with field names
> - Key patterns, conventions, and architectural decisions
> - Dependencies on other packages in this workspace
> - Tests overview: list test files with a one-line description of what each covers
> - Read the package's config file (Cargo.toml/pyproject.toml/etc) and note dependencies

**Brief summary** (for adjacent packages) — instruct the subagent:
> Analyze the package at `<package_path>`. Return a summary of 15-25 lines covering:
> - Purpose and responsibility
> - Public API surface (key classes/structs, functions)
> - Data models and their fields
> - Dependencies on other packages in this workspace
> - Any patterns or conventions worth knowing

**Minimal summary** (for packages unlikely to be touched) — instruct the subagent:
> Analyze the package at `<package_path>`. Return a summary of 5-10 lines covering:
> - One-line purpose
> - Key entry points (file names only)
> - Public types/models (names only, no field details)

### Phase 3: Assemble Report

After all subagents return, produce the output report below. Inline the subagent summaries in the appropriate sections.

---

## Output Report

Provide a concise summary covering:

### Project Overview
- Purpose and type of application
- Primary technologies and frameworks
- Current version/state

### Architecture (Focused Area — detailed subagent summaries)
- Detailed structure and organization of the focused packages
- Key architectural patterns identified
- Important files and their purposes
- Public API surface

### Architecture (Adjacent Areas — brief/minimal subagent summaries)
- Summarized structure of adjacent packages
- Key interfaces and models that the focused area depends on

### Tech Stack
- Languages and versions
- Frameworks and major libraries
- Build tools and package managers
- Testing frameworks

### Core Principles
- Code style and conventions observed (from AGENTS.md)
- Documentation standards
- Testing approach

### Current State
- Active branch
- Recent changes or development focus
- Any immediate observations or concerns

**Make this summary easy to scan — use bullet points and clear headers.**
**Indicate which scope was used so the reader knows what was deep-read vs. summarized.**
