# Common Agent Configuration

Shared agent skills, design reference docs, and installer lifecycle for project-local and explicit global agent-client integration.

## Ownership

- Dotfiles own durable always-on guidance and client directory shape.
- `my-agent-config` owns reusable workflows and generated skill symlinks.
- Generated skill links belong in client directories, not in the dotfiles repo.

## Project install

Project scope is the default. Keep one checkout of `my-agent-config` and install into projects with nearest-git auto-detection or `--project PATH`.

```bash
# Auto-detect nearest git repo from cwd
python /path/to/my-agent-config/setup.py install

# Explicit target project
python /path/to/my-agent-config/setup.py install --project /path/to/project

# Explicit current directory, including intentional self-install into this checkout
python /path/to/my-agent-config/setup.py install --project .
```

Project installs discover shared skills from this repo. Codex, Pi, and OpenCode share `.agents/skills`; client-specific links are written only where the client needs native artifacts such as `.claude/skills`, `.cursor/skills`, `.opencode/commands`, `.cline/skills`, and `.clinerules/workflows`.

Nearest-git auto-detection refuses to target the `my-agent-config` source checkout itself; pass `--project .` only when that is intentional. `--project` is rejected with `--global`.

## Global install

Global scope must be explicit:

```bash
python setup.py install --global --skill-group design
python setup.py install --global --skills do-design-review,do-maintainability-check
python setup.py install --global --skill do-design-pass --skill do-design-review
```

Global installs write generated symlinks into client home/config directories such as `~/.agents/skills`, `~/.claude/skills`, `~/.config/opencode/commands`, and `~/.cline/skills`. Codex, Pi, and OpenCode share `~/.agents/skills`; generated links are not written into dotfiles.

```bash
python /path/to/my-agent-config/setup.py install --global --skill-group design
```

## Skill selection

By default, install/update/status/prune/uninstall operate on all discovered skills for the selected scope and clients. Narrow the operation with:

- `--skill NAME` (repeatable; comma-separated values also accepted)
- `--skills NAME,NAME`
- `--skill-group design`
- `--exclude-skill NAME` (repeatable; comma-separated values also accepted)

Current skill groups:

- `design`: `do-design-pass`, `do-design-review`, `do-maintainability-check`, `do-plan-adherence-review`

Skill selectors are conservative operation filters. For example, `uninstall --global --skill-group design --apply` removes only managed global links for the design skills, not every other installed skill.

## Commands

```bash
python setup.py install   [--project PATH | --global] [--client CLIENT|all]
python setup.py update    [--project PATH | --global] [--client CLIENT|all]
python setup.py status    [--project PATH | --global] [--client CLIENT|all]
python setup.py prune     [--project PATH | --global] [--client CLIENT|all] [--apply]
python setup.py uninstall [--project PATH | --global] [--client CLIENT|all] [--apply]
```

Safety rules:

- `prune` and `uninstall` are dry-run by default; pass `--apply` to remove managed symlinks.
- `install` and `update` accept `--dry-run` to preview links without writing manifests or symlinks.
- Only manifest-owned symlinks are removed.
- Real files and client-generated data are never deleted.
- Generated client directories, manifests, and runtime state are local artifacts and should not be committed to this source repo.

## Manifests

Manifests track installed links and source metadata:

- Project: `.my-agent-config/manifest.json`
- Global: `~/.config/my-agent-config/install-manifest.json`

Each link record includes scope, destination id, artifact kind, skill name, link path, source path, source kind, and `clients`. The `clients` field records which selected agent clients own that link; for shared destinations such as `.agents/skills`, prune and uninstall remove only the selected client ownership until no clients remain.

If links are reconstructed manually, remove generated links and manifests first so new records include explicit `clients` ownership.

`setup.py` creates generated install state such as `<project>/.my-agent-config/manifest.json`; it does not create or clone the source checkout inside target projects.

## Repository layout

The current source layout is intentionally nested for compatibility with existing manifests and discovery:

- Skills: `skills/skills/<skill-name>/SKILL.md`
- Design docs: `design/design/*.md`

Skill instructions should refer to other workflows by skill name when possible instead of assuming this source-tree path is available inside installed client directories.

## Updating shared skills

From this repo checkout:

```bash
git pull
python setup.py update --project /path/to/project
```

For global installs:

```bash
git pull
python setup.py update --global --skill-group design
```
