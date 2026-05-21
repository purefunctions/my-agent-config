#!/usr/bin/env python3
"""Lifecycle-aware installer for user agent skills.

By default, commands operate on a project. The target project is selected by
--project PATH or nearest parent git repo auto-detection:

    python setup.py install
    python /path/to/my-agent-config/setup.py install --project /path/to/project
    python setup.py update
    python setup.py status

Global scope must be explicit:

    python setup.py install --global
    python setup.py uninstall --global --apply

Safety rules:
- Only remove manifest-owned symlinks.
- Changed manifest-owned symlink targets may be updated automatically.
- --force may replace other conflicting symlinks, but never real files.
- prune/uninstall dry-run by default; pass --apply to remove managed links.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Literal, Sequence

Scope = Literal["project", "global"]
ArtifactKind = Literal["skill", "command", "workflow"]
SourceKind = Literal["skill_dir", "skill_md"]

_PROJECT_ROOT: Path | None = None


class ManifestError(Exception):
    pass


SKILL_GROUPS: dict[str, tuple[str, ...]] = {
    "design": (
        "do-design-pass",
        "do-design-review",
        "do-maintainability-check",
        "do-plan-adherence-review",
    ),
}

SHARED_AGENTS_CLIENTS = frozenset({"codex", "pi", "opencode"})


@dataclass(frozen=True)
class InstallDestination:
    id: str
    scope: Scope
    artifact: ArtifactKind
    link_path: str
    source: SourceKind
    clients: frozenset[str] = frozenset()


INSTALL_DESTINATIONS: list[InstallDestination] = [
    # `.agents/skills` is the shared discovery path for Codex, Pi, and OpenCode.
    InstallDestination(
        "agents",
        "project",
        "skill",
        ".agents/skills/{name}",
        "skill_dir",
        SHARED_AGENTS_CLIENTS,
    ),
    InstallDestination("claude", "project", "skill", ".claude/skills/{name}", "skill_dir"),
    InstallDestination("cursor", "project", "skill", ".cursor/skills/{name}", "skill_dir"),
    InstallDestination("cursor", "project", "command", ".cursor/commands/{name}.md", "skill_md"),
    InstallDestination("opencode", "project", "command", ".opencode/commands/{name}.md", "skill_md"),
    InstallDestination("cline", "project", "skill", ".cline/skills/{name}", "skill_dir"),
    InstallDestination("cline", "project", "workflow", ".clinerules/workflows/{name}.md", "skill_md"),
    # Global skills/commands. Global scope is explicit only.
    InstallDestination(
        "agents",
        "global",
        "skill",
        "~/.agents/skills/{name}",
        "skill_dir",
        SHARED_AGENTS_CLIENTS,
    ),
    InstallDestination("claude", "global", "skill", "~/.claude/skills/{name}", "skill_dir"),
    InstallDestination("opencode", "global", "command", "~/.config/opencode/commands/{name}.md", "skill_md"),
    InstallDestination("cline", "global", "skill", "~/.cline/skills/{name}", "skill_dir"),
]

# Client dirs to report as leftovers even though this installer no longer creates
# links there.
CLIENT_UNMANAGED_DIRS: dict[tuple[Scope, str], tuple[str, ...]] = {
    ("project", "pi"): (".pi",),
    ("global", "pi"): ("~/.pi",),
}


def destination_clients(destination: InstallDestination) -> frozenset[str]:
    return destination.clients or frozenset({destination.id})


def destination_matches_clients(destination: InstallDestination, clients: set[str]) -> bool:
    return bool(destination_clients(destination) & clients)


def record_matches_clients(record: LinkRecord, clients: set[str]) -> bool:
    return bool(record_clients(record) & clients)


def clients_for_destination_id(destination_id: str) -> set[str]:
    clients: set[str] = set()
    for destination in INSTALL_DESTINATIONS:
        if destination.id == destination_id:
            clients.update(destination_clients(destination))
    return clients or {destination_id}


def record_clients(record: LinkRecord) -> set[str]:
    if record.clients:
        return set(record.clients)
    return clients_for_destination_id(record.destination_id)


def known_clients() -> set[str]:
    clients: set[str] = set()
    for destination in INSTALL_DESTINATIONS:
        clients.update(destination_clients(destination))
    return clients


def known_client_names() -> list[str]:
    return sorted(known_clients())


@dataclass
class LinkRecord:
    scope: Scope
    destination_id: str
    artifact: ArtifactKind
    name: str
    link: str
    target: str
    source_kind: SourceKind
    clients: tuple[str, ...] = ()
    created_by: str = "my-agent-config"


@dataclass(frozen=True)
class SkillSelection:
    include: frozenset[str] | None = None
    exclude: frozenset[str] = frozenset()

    def matches(self, name: str) -> bool:
        if self.include is not None and name not in self.include:
            return False
        return name not in self.exclude

    def selected_requested_names(self) -> set[str]:
        names = set(self.exclude)
        if self.include is not None:
            names.update(self.include)
        return names

    def describe(self) -> str:
        parts = []
        if self.include is not None:
            parts.append("include=" + ",".join(sorted(self.include)))
        if self.exclude:
            parts.append("exclude=" + ",".join(sorted(self.exclude)))
        return "; ".join(parts) if parts else "all"


def common_root() -> Path:
    return Path(__file__).parent.resolve()


def nearest_git_root(cwd: Path) -> Path | None:
    current = cwd.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def resolve_project_root(project_arg: str | None) -> Path:
    if project_arg is not None:
        project_path = Path(project_arg).expanduser()
        if not project_path.is_absolute():
            project_path = Path.cwd() / project_path
        return project_path.resolve()

    detected = nearest_git_root(Path.cwd())
    if detected is None:
        raise ValueError("No project git repository detected from cwd. Pass --project PATH.")

    if detected == common_root().resolve():
        raise ValueError(
            "Refusing to auto-detect the my-agent-config source checkout as the target project. "
            "Pass --project . to install into this checkout, or pass --project PATH for another project."
        )
    return detected


def configure_project_root(project_arg: str | None) -> None:
    global _PROJECT_ROOT
    _PROJECT_ROOT = resolve_project_root(project_arg)


def project_root() -> Path:
    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT
    return resolve_project_root(None)


def manifest_path(scope: Scope) -> Path:
    if scope == "project":
        return project_root() / ".my-agent-config" / "manifest.json"
    return Path.home() / ".config" / "my-agent-config" / "install-manifest.json"


def rel_or_abs(path: Path, base: Path | None) -> str:
    if base is None:
        return str(path)
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def resolve_link_path(scope: Scope, link_path: str) -> Path:
    if scope == "global":
        # Expand ~ before filesystem operations and manifest records. The
        # filesystem still follows heavy-directory symlinks when links are created.
        path = Path(os.path.expanduser(link_path))
        if path.is_absolute():
            return path
        return Path.home() / path
    return project_root() / link_path


def discover_skills(skills_dir: Path) -> dict[str, Path]:
    if not skills_dir.exists():
        return {}

    search_dirs = [skills_dir]
    nested = skills_dir / "skills"
    if nested.exists():
        search_dirs.append(nested)

    discovered: dict[str, Path] = {}
    for directory in search_dirs:
        for item in directory.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                discovered.setdefault(item.name, item)
    return discovered


def all_skill_sources() -> dict[str, Path]:
    return discover_skills(common_root() / "skills")


def filter_skills(skills: dict[str, Path], selection: SkillSelection) -> dict[str, Path]:
    return {name: path for name, path in skills.items() if selection.matches(name)}


def skill_sources(selection: SkillSelection) -> dict[str, Path]:
    return filter_skills(all_skill_sources(), selection)


def selected_scopes(global_scope: bool) -> list[Scope]:
    return ["global"] if global_scope else ["project"]


def selected_clients(client_arg: str) -> set[str]:
    clients = known_clients()
    if client_arg == "all":
        return clients

    selected: set[str] = set()
    unknown: list[str] = []
    for raw_client in client_arg.split(","):
        client = raw_client.strip()
        if not client:
            continue
        if client not in clients:
            unknown.append(client)
        else:
            selected.add(client)

    if unknown:
        raise ValueError(
            "Unknown client(s): "
            + ", ".join(sorted(unknown))
            + ". Known clients: "
            + ", ".join(known_client_names())
        )
    if not selected:
        raise ValueError("No clients selected")
    return selected


def csv_items(values: Sequence[str]) -> list[str]:
    items: list[str] = []
    for value in values:
        items.extend(item.strip() for item in value.split(",") if item.strip())
    return items


def selected_skills(args: argparse.Namespace) -> SkillSelection:
    included = set(csv_items(args.skill) + csv_items([args.skills]))
    for group in csv_items(args.skill_group):
        if group not in SKILL_GROUPS:
            known = ", ".join(sorted(SKILL_GROUPS)) or "none"
            raise ValueError(f"Unknown skill group: {group}. Known groups: {known}")
        included.update(SKILL_GROUPS[group])

    excluded = set(csv_items(args.exclude_skill))
    include = frozenset(included) if included else None
    exclude = frozenset(excluded)
    if include is not None and not (include - exclude):
        raise ValueError("No skills selected after exclusions")
    return SkillSelection(include=include, exclude=exclude)


def validate_skill_selection(scope: Scope, selection: SkillSelection, command: str) -> None:
    requested = selection.selected_requested_names()
    if not requested:
        return

    known = set(all_skill_sources())
    if command in {"status", "prune", "uninstall"}:
        known.update(record.name for record in managed_records(scope))

    unknown = requested - known
    if unknown:
        raise ValueError(
            f"Unknown skill(s) for {scope} scope: "
            + ", ".join(sorted(unknown))
            + ". Known skills: "
            + (", ".join(sorted(known)) if known else "none")
        )


def validate_scope_selections(scopes: Iterable[Scope], selection: SkillSelection, command: str) -> None:
    for scope in scopes:
        validate_skill_selection(scope, selection, command)


def source_for_skill(skill_dir: Path, source: SourceKind) -> Path:
    if source == "skill_dir":
        return skill_dir
    return skill_dir / "SKILL.md"


def applicable_destinations(scope: Scope, clients: set[str]) -> Iterable[InstallDestination]:
    for destination in INSTALL_DESTINATIONS:
        if destination.scope != scope or not destination_matches_clients(destination, clients):
            continue
        yield destination


def clients_with_destinations(scope: Scope) -> set[str]:
    clients: set[str] = set()
    for destination in INSTALL_DESTINATIONS:
        if destination.scope == scope:
            clients.update(destination_clients(destination))
    return clients


def warn_missing_destinations(scope: Scope, clients: set[str]) -> None:
    missing = sorted(clients - clients_with_destinations(scope))
    if missing:
        print(
            f"Note: no configured {scope} install destinations for: {', '.join(missing)}. "
            "Skipping those clients for this scope."
        )


def shared_discovery_notes(scope: Scope, clients: set[str]) -> list[str]:
    notes = []
    for destination in INSTALL_DESTINATIONS:
        if destination.scope != scope or not destination.clients:
            continue
        selected = destination.clients & clients
        if len(selected) > 1:
            notes.append(
                f"{'/'.join(sorted(selected))} {destination.artifact} uses one shared path: {destination.link_path}."
            )
    return notes


def print_shared_discovery_notes(scope: Scope, clients: set[str]) -> None:
    notes = shared_discovery_notes(scope, clients)
    if not notes:
        return
    print("\nShared skill discovery:")
    for note in notes:
        print(f"  - {note}")


def plan_links(scope: Scope, clients: set[str], selection: SkillSelection) -> list[LinkRecord]:
    skills = skill_sources(selection)
    records: list[LinkRecord] = []
    base = project_root() if scope == "project" else None

    for name, skill_dir in sorted(skills.items()):
        for destination in applicable_destinations(scope, clients):
            link = resolve_link_path(scope, destination.link_path.format(name=name))
            src = source_for_skill(skill_dir, destination.source)
            destination_record_clients = tuple(sorted(destination_clients(destination) & clients))
            records.append(
                LinkRecord(
                    scope=scope,
                    destination_id=destination.id,
                    artifact=destination.artifact,
                    name=name,
                    link=rel_or_abs(link, base),
                    target=rel_or_abs(src, base),
                    source_kind=destination.source,
                    clients=destination_record_clients,
                )
            )
    return records


def record_paths(record: LinkRecord) -> tuple[Path, Path]:
    base = project_root() if record.scope == "project" else Path("/")
    link = Path(record.link)
    target = Path(record.target)
    if record.scope == "project":
        link = project_root() / link
        target = project_root() / target
    return link, target


def relative_target(target: Path, link: Path) -> str:
    return os.path.relpath(target, link.parent)


def previous_manifest_target(record: LinkRecord, previous_record: LinkRecord | None) -> str | None:
    if previous_record is None or previous_record.scope != record.scope or previous_record.link != record.link:
        return None

    link, _ = record_paths(record)
    _, previous_target = record_paths(previous_record)
    return relative_target(previous_target, link)


def create_link(record: LinkRecord, force: bool = False, previous_record: LinkRecord | None = None) -> str:
    link, target = record_paths(record)
    link.parent.mkdir(parents=True, exist_ok=True)
    rel_target = relative_target(target, link)

    if link.is_symlink():
        current = os.readlink(link)
        if current == rel_target:
            return "ok"
        if current == previous_manifest_target(record, previous_record):
            link.unlink()
            link.symlink_to(rel_target)
            return "updated"
        if not force:
            return f"conflict: symlink points to {current}"
        link.unlink()
    elif link.exists():
        return "conflict: real file or directory exists"

    link.symlink_to(rel_target)
    return "created"


def read_manifest(scope: Scope) -> dict:
    path = manifest_path(scope)
    if not path.exists():
        return {"version": 1, "scope": scope, "links": []}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise ManifestError(f"Malformed manifest at {path}: {error}. Repair or move it before retrying.") from error


def write_manifest(scope: Scope, records: list[LinkRecord]) -> None:
    path = manifest_path(scope)
    path.parent.mkdir(parents=True, exist_ok=True)
    source_root = common_root().resolve()
    source_revision = git_revision(source_root)
    data = {
        "version": 1,
        "scope": scope,
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source_root),
        "source_git_revision": source_revision or "unknown",
        "links": [asdict(r) for r in records],
    }
    path.write_text(json.dumps(data, indent=2) + "\n")


def merge_manifest_records(scope: Scope, installed_records: list[LinkRecord]) -> list[LinkRecord]:
    """Merge newly installed records into the manifest without losing stale records.

    Stale managed links must remain in the manifest so status/prune can report
    and remove them after a skill is deleted or an install destination changes.
    Records are replaced by link path, which lets changed targets update cleanly.
    """
    merged = {record.link: record for record in managed_records(scope)}
    for record in installed_records:
        previous = merged.get(record.link)
        if previous is not None:
            clients = record_clients(previous) | record_clients(record)
            record = replace(record, clients=tuple(sorted(clients)))
        merged[record.link] = record
    return sorted(merged.values(), key=lambda r: (r.destination_id, r.artifact, r.name, r.link))


def git_revision(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=path,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return None


def install_scope(scope: Scope, clients: set[str], selection: SkillSelection, force: bool, dry_run: bool) -> dict[str, int]:
    warn_missing_destinations(scope, clients)
    print_shared_discovery_notes(scope, clients)
    records = plan_links(scope, clients, selection)
    stats = {"created": 0, "updated": 0, "ok": 0, "conflict": 0, "planned": 0}
    installed_records: list[LinkRecord] = []
    previous_records = {record.link: record for record in managed_records(scope)}

    if dry_run:
        for record in records:
            print(f"Would link: {record.link} -> {record.target}")
            stats["planned"] += 1
        return stats

    for record in records:
        status = create_link(record, force=force, previous_record=previous_records.get(record.link))
        if status in {"created", "updated"}:
            stats[status] += 1
            installed_records.append(record)
        elif status == "ok":
            stats["ok"] += 1
            installed_records.append(record)
        else:
            stats["conflict"] += 1
            print(f"Conflict: {record.link} -> {status}")

    write_manifest(scope, merge_manifest_records(scope, installed_records))
    return stats


def update_sources() -> bool:
    if (common_root() / ".git").exists():
        print("Updating shared skills source...")
        try:
            subprocess.run(["git", "pull"], cwd=common_root(), check=True)
        except subprocess.CalledProcessError as error:
            print(f"Failed to update shared skills source with git pull (exit {error.returncode}).")
            return False
    return True


def status_for_record(record: LinkRecord) -> str:
    link, target = record_paths(record)
    expected = relative_target(target, link)
    if not link.exists() and not link.is_symlink():
        return "missing"
    if not link.is_symlink():
        return "conflict-real-file"
    current = os.readlink(link)
    if current != expected:
        return f"conflict-symlink:{current}"
    if not target.exists():
        return "broken-target"
    return "ok"


def managed_records(scope: Scope) -> list[LinkRecord]:
    data = read_manifest(scope)
    records = []
    for item in data.get("links", []):
        if "destination_id" not in item and "tool" in item:
            item = dict(item)
            item["destination_id"] = item.pop("tool")
        if "clients" in item:
            item = dict(item)
            item["clients"] = tuple(item["clients"])
        records.append(LinkRecord(**item))
    return records


def stale_records(scope: Scope, clients: set[str], selection: SkillSelection) -> list[LinkRecord]:
    current = {(r.link, r.target) for r in plan_links(scope, clients, selection)}
    stale = []
    for record in managed_records(scope):
        if not record_matches_clients(record, clients) or not selection.matches(record.name):
            continue
        if (record.link, record.target) not in current:
            stale.append(record)
    return stale


def status_scope(scope: Scope, clients: set[str], selection: SkillSelection) -> None:
    warn_missing_destinations(scope, clients)
    print_shared_discovery_notes(scope, clients)
    planned = plan_links(scope, clients, selection)
    counts: dict[str, int] = {}
    for record in planned:
        status = status_for_record(record)
        counts[status] = counts.get(status, 0) + 1
    stale = stale_records(scope, clients, selection)

    print(f"\nStatus for {scope} scope")
    print(f"  skills: {selection.describe()}")
    for key in sorted(counts):
        print(f"  {key}: {counts[key]}")
    print(f"  stale-managed: {len(stale)}")
    if stale:
        print("\nStale managed links:")
        for record in stale:
            print(f"  - {record.link}")


def remove_record(record: LinkRecord, dry_run: bool) -> bool:
    link, target = record_paths(record)

    if not link.exists() and not link.is_symlink():
        if dry_run:
            print(f"Would drop missing manifest record: {record.link}")
            return False
        print(f"Dropped missing manifest record: {record.link}")
        return True

    if not link.is_symlink():
        print(f"Skip conflict: {record.link} is a real file or directory")
        return False

    expected = relative_target(target, link)
    current = os.readlink(link)
    if current != expected:
        print(f"Skip conflict: {record.link} points to unexpected target: {current}")
        return False

    if dry_run:
        print(f"Would remove: {record.link}")
        return False
    link.unlink()
    print(f"Removed: {record.link}")
    return True


def client_ownership_update(record: LinkRecord, clients: set[str]) -> LinkRecord | None:
    remaining = record_clients(record) - clients
    if remaining:
        return replace(record, clients=tuple(sorted(remaining)))
    return None


def print_client_ownership_change(record: LinkRecord, clients: set[str], remaining: LinkRecord, dry_run: bool) -> None:
    removed = record_clients(record) & clients
    action = "Would remove" if dry_run else "Removed"
    print(
        f"{action} client ownership for {record.link}: "
        f"{', '.join(sorted(removed))}; keeping for {', '.join(remaining.clients)}"
    )


def update_manifest_after_client_removal(scope: Scope, removed_links: set[str], updated_records: dict[str, LinkRecord]) -> None:
    if not removed_links and not updated_records:
        return
    remaining = []
    for record in managed_records(scope):
        if record.link in removed_links:
            continue
        remaining.append(updated_records.get(record.link, record))
    write_manifest(scope, remaining)


def prune_scope(scope: Scope, clients: set[str], selection: SkillSelection, dry_run: bool) -> None:
    stale = stale_records(scope, clients, selection)
    print(f"\nPrune {scope} scope ({'dry run' if dry_run else 'apply'})")
    print(f"  clients: {', '.join(sorted(clients))}")
    print(f"  skills: {selection.describe()}")
    removed_links: set[str] = set()
    updated_records: dict[str, LinkRecord] = {}
    for record in stale:
        remaining = client_ownership_update(record, clients)
        if remaining is not None:
            print_client_ownership_change(record, clients, remaining, dry_run)
            if not dry_run:
                updated_records[record.link] = remaining
            continue
        if remove_record(record, dry_run=dry_run):
            removed_links.add(record.link)
    if dry_run:
        print("\nPreview only. Re-run with --apply to remove managed stale symlinks.")
    else:
        update_manifest_after_client_removal(scope, removed_links, updated_records)


def uninstall_scope(scope: Scope, clients: set[str], selection: SkillSelection, dry_run: bool) -> None:
    records = [
        record
        for record in managed_records(scope)
        if record_matches_clients(record, clients) and selection.matches(record.name)
    ]
    print(f"\nUninstall {scope} scope ({'dry run' if dry_run else 'apply'})")
    print(f"  clients: {', '.join(sorted(clients))}")
    print(f"  skills: {selection.describe()}")
    removed_links: set[str] = set()
    updated_records: dict[str, LinkRecord] = {}
    for record in records:
        remaining = client_ownership_update(record, clients)
        if remaining is not None:
            print_client_ownership_change(record, clients, remaining, dry_run)
            if not dry_run:
                updated_records[record.link] = remaining
            continue
        if remove_record(record, dry_run=dry_run):
            removed_links.add(record.link)
    leftovers(scope, clients)
    if dry_run:
        print("\nPreview only. Re-run with --apply to remove managed symlinks.")
    else:
        update_manifest_after_client_removal(scope, removed_links, updated_records)
        print(f"Removed managed links: {len(removed_links)}")


def install_root_for_destination(destination: InstallDestination) -> Path:
    templated = destination.link_path.format(name="__skill__")
    if destination.scope == "project":
        first_part = Path(templated).parts[0]
        return project_root() / first_part

    path = Path(os.path.expanduser(templated))
    try:
        relative = path.relative_to(Path.home())
    except ValueError:
        return path.parent

    if relative.parts[:1] == (".config",) and len(relative.parts) > 1:
        return Path.home() / ".config" / relative.parts[1]
    return Path.home() / relative.parts[0]


def unmanaged_client_dir(scope: Scope, path: str) -> Path:
    expanded = Path(os.path.expanduser(path))
    if expanded.is_absolute():
        return expanded
    if scope == "project":
        return project_root() / expanded
    return Path.home() / expanded


def client_dirs(scope: Scope, clients: set[str]) -> list[Path]:
    paths = {
        install_root_for_destination(destination)
        for destination in INSTALL_DESTINATIONS
        if destination.scope == scope and destination_matches_clients(destination, clients)
    }
    for client in clients:
        for path in CLIENT_UNMANAGED_DIRS.get((scope, client), ()):
            paths.add(unmanaged_client_dir(scope, path))
    return sorted(paths)


def leftovers(scope: Scope, clients: set[str]) -> None:
    print("\nLeftover files/directories not removed:")
    any_left = False
    for path in client_dirs(scope, clients):
        if path.exists() or path.is_symlink():
            any_left = True
            print(f"  - {path}")
    if not any_left:
        print("  None detected in selected client dirs.")
    print("Reason: uninstall only removes manifest-owned symlinks. Client-generated data and unmanaged files are left for manual cleanup.")


def run_command(args: argparse.Namespace) -> int:
    scopes = selected_scopes(args.global_scope)
    try:
        clients = selected_clients(args.client)
        selection = selected_skills(args)
    except ValueError as error:
        print(error)
        return 2

    if getattr(args, "project", None) is not None and args.global_scope:
        print("Use either --project PATH or --global, not both.")
        return 2

    if "project" in scopes:
        try:
            configure_project_root(args.project)
        except ValueError as error:
            print(error)
            return 2

    if getattr(args, "apply", False) and getattr(args, "dry_run", False):
        print("Use either --apply or --dry-run, not both.")
        return 2

    if args.command not in {"prune", "uninstall"} and getattr(args, "apply", False):
        print("--apply is only valid for prune and uninstall.")
        return 2

    try:
        if args.command in {"install", "status", "prune", "uninstall"}:
            validate_scope_selections(scopes, selection, args.command)
    except (ManifestError, ValueError) as error:
        print(error)
        return 2

    try:
        if args.command == "install":
            for scope in scopes:
                stats = install_scope(scope, clients, selection, args.force, args.dry_run)
                print(f"\nInstalled {scope} links: {stats}")
            return 0

        if args.command == "update":
            for scope in scopes:
                if not args.dry_run and not update_sources():
                    return 2
                try:
                    validate_skill_selection(scope, selection, args.command)
                except ValueError as error:
                    print(error)
                    return 2
                stats = install_scope(scope, clients, selection, args.force, args.dry_run)
                print(f"\nUpdated {scope} links: {stats}")
                stale = stale_records(scope, clients, selection)
                if stale:
                    print("\nSuggested next actions:")
                    print("  1. Review stale links: python setup.py status")
                    print("  2. Preview cleanup:   python setup.py prune")
                    print("  3. Apply cleanup:     python setup.py prune --apply")
            return 0

        if args.command == "status":
            for scope in scopes:
                status_scope(scope, clients, selection)
            return 0

        if args.command == "prune":
            dry_run = not args.apply or args.dry_run
            for scope in scopes:
                prune_scope(scope, clients, selection, dry_run)
            return 0

        if args.command == "uninstall":
            dry_run = not args.apply or args.dry_run
            for scope in scopes:
                uninstall_scope(scope, clients, selection, dry_run)
            return 0
    except ManifestError as error:
        print(error)
        return 2

    print(f"Unknown command: {args.command}")
    return 2


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Install and manage my-agent-config skills")
    p.add_argument("command", choices=["install", "update", "status", "prune", "uninstall"])
    target = p.add_mutually_exclusive_group()
    target.add_argument("--global", dest="global_scope", action="store_true", help="Operate on global client config instead of a project.")
    target.add_argument("--project", help="Target project. Resolved relative to the caller's current working directory.")
    p.add_argument("--client", default="all", help="all or comma-separated agent client names")
    p.add_argument("--force", action="store_true", help="Overwrite conflicting symlinks only, never real files")
    p.add_argument("--skill", action="append", default=[], help="Install/manage one skill. May be repeated or comma-separated.")
    p.add_argument("--skills", default="", help="Comma-separated skill names to install/manage")
    p.add_argument("--skill-group", action="append", default=[], help="Skill group to install/manage. Known groups: design")
    p.add_argument("--exclude-skill", action="append", default=[], help="Exclude one skill from the selected set. May be repeated or comma-separated.")
    p.add_argument("--apply", action="store_true", help="Apply prune/uninstall changes. Without this, they dry-run.")
    p.add_argument("--dry-run", action="store_true", help="Preview install/update/prune/uninstall actions. This is the default for prune/uninstall.")
    return p


def main() -> int:
    args = parser().parse_args()
    return run_command(args)


if __name__ == "__main__":
    sys.exit(main())
