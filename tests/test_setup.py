from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SETUP_PATH = ROOT / "setup.py"


def load_setup():
    spec = importlib.util.spec_from_file_location("my_agent_config_setup", SETUP_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module._PROJECT_ROOT = None
    return module


@pytest.fixture
def setup_module():
    return load_setup()


def make_skill(path: Path) -> Path:
    path.mkdir(parents=True)
    (path / "SKILL.md").write_text("---\nname: test\n---\n")
    return path


def skill_args(**overrides):
    values = {
        "skill": [],
        "skills": "",
        "skill_group": [],
        "exclude_skill": [],
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def record(setup, **overrides):
    values = {
        "scope": "project",
        "destination_id": "agents",
        "artifact": "skill",
        "name": "alpha",
        "link": ".agents/skills/alpha",
        "target": "source/skills/alpha",
        "source_kind": "skill_dir",
    }
    values.update(overrides)
    return setup.LinkRecord(**values)


def test_explicit_project_path_is_resolved_from_caller_cwd(setup_module, tmp_path, monkeypatch):
    caller = tmp_path / "caller"
    project = caller / "target"
    caller.mkdir()
    project.mkdir()
    monkeypatch.chdir(caller)
    monkeypatch.setattr(setup_module, "common_root", lambda: tmp_path / "source")

    setup_module.configure_project_root("target")

    assert setup_module.project_root() == project.resolve()


def test_nearest_git_root_is_used_when_project_is_omitted(setup_module, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    nested = repo / "a" / "b"
    (repo / ".git").mkdir(parents=True)
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)
    monkeypatch.setattr(setup_module, "common_root", lambda: tmp_path / "source")

    setup_module.configure_project_root(None)

    assert setup_module.project_root() == repo.resolve()


def test_project_scope_errors_outside_git_repo_without_project(setup_module, tmp_path, monkeypatch):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    monkeypatch.setattr(setup_module, "common_root", lambda: tmp_path / "source")

    with pytest.raises(ValueError, match="Pass --project PATH"):
        setup_module.resolve_project_root(None)


def test_self_install_protection_for_nearest_git_detection(setup_module, tmp_path, monkeypatch):
    source = tmp_path / "my-agent-config"
    (source / ".git").mkdir(parents=True)
    monkeypatch.chdir(source)
    monkeypatch.setattr(setup_module, "common_root", lambda: source)

    with pytest.raises(ValueError, match=r"Pass --project \."):
        setup_module.resolve_project_root(None)


def test_explicit_project_dot_allows_source_checkout(setup_module, tmp_path, monkeypatch):
    source = tmp_path / "my-agent-config"
    (source / ".git").mkdir(parents=True)
    monkeypatch.chdir(source)
    monkeypatch.setattr(setup_module, "common_root", lambda: source)

    setup_module.configure_project_root(".")

    assert setup_module.project_root() == source.resolve()


def test_project_option_is_rejected_with_global(setup_module, capsys):
    with pytest.raises(SystemExit) as error:
        setup_module.parser().parse_args(["status", "--global", "--project", "."])

    assert error.value.code == 2
    assert "not allowed with argument" in capsys.readouterr().err


def test_selected_clients_derives_all_from_install_destinations_and_rejects_unknown(setup_module):
    expected_clients = setup_module.known_clients()

    assert setup_module.selected_clients("all") == expected_clients
    assert setup_module.selected_clients("codex,pi") == {"codex", "pi"}

    with pytest.raises(ValueError, match="Unknown client"):
        setup_module.selected_clients("pi,nope")


def test_selected_skills_handles_include_exclude_groups_and_empty_selection(setup_module):
    selection = setup_module.selected_skills(
        skill_args(
            skill=["custom,do-design-pass"],
            skill_group=["design"],
            exclude_skill=["do-design-review"],
        )
    )

    assert selection.matches("custom")
    assert selection.matches("do-design-pass")
    assert not selection.matches("do-design-review")
    assert not selection.matches("unselected")

    with pytest.raises(ValueError, match="No skills selected"):
        setup_module.selected_skills(skill_args(skill=["only"], exclude_skill=["only"]))


def test_discover_skills_handles_direct_and_nested_skill_dirs(setup_module, tmp_path):
    skills_root = tmp_path / "skills"
    direct = make_skill(skills_root / "direct")
    nested = make_skill(skills_root / "skills" / "nested")

    assert setup_module.discover_skills(skills_root) == {"direct": direct, "nested": nested}


def test_project_manifest_path_uses_my_agent_config_dir(setup_module, tmp_path):
    setup_module._PROJECT_ROOT = tmp_path / "project"

    assert setup_module.manifest_path("project") == setup_module._PROJECT_ROOT / ".my-agent-config" / "manifest.json"


def test_plan_links_uses_fake_skill_tree_and_selected_client(setup_module, tmp_path, monkeypatch):
    project = tmp_path / "project"
    source = tmp_path / "source"
    skill_dir = make_skill(source / "skills" / "alpha")
    monkeypatch.setattr(setup_module, "common_root", lambda: source)
    setup_module._PROJECT_ROOT = project

    records = setup_module.plan_links("project", {"pi"}, setup_module.SkillSelection())

    assert records == [
        setup_module.LinkRecord(
            scope="project",
            destination_id="agents",
            artifact="skill",
            name="alpha",
            link=".agents/skills/alpha",
            target=str(skill_dir),
            source_kind="skill_dir",
            clients=("pi",),
        )
    ]


def test_plan_links_uses_one_shared_agents_skill_target_for_codex_pi_opencode(setup_module, tmp_path, monkeypatch):
    project = tmp_path / "project"
    source = tmp_path / "source"
    skill_dir = make_skill(source / "skills" / "alpha")
    monkeypatch.setattr(setup_module, "common_root", lambda: source)
    setup_module._PROJECT_ROOT = project

    records = setup_module.plan_links("project", {"codex", "pi", "opencode"}, setup_module.SkillSelection())

    assert records == [
        setup_module.LinkRecord(
            scope="project",
            destination_id="agents",
            artifact="skill",
            name="alpha",
            link=".agents/skills/alpha",
            target=str(skill_dir),
            source_kind="skill_dir",
            clients=("codex", "opencode", "pi"),
        ),
        setup_module.LinkRecord(
            scope="project",
            destination_id="opencode",
            artifact="command",
            name="alpha",
            link=".opencode/commands/alpha.md",
            target=str(skill_dir / "SKILL.md"),
            source_kind="skill_md",
            clients=("opencode",),
        ),
    ]


def test_merge_manifest_records_preserves_stale_and_replaces_by_link(setup_module, monkeypatch):
    stale = record(setup_module, name="stale", link="old", target="old-target")
    replaced_old = record(setup_module, name="old", link="same", target="old-target", clients=("codex",))
    replaced_new = record(setup_module, name="new", link="same", target="new-target", clients=("pi",))
    monkeypatch.setattr(setup_module, "managed_records", lambda scope: [stale, replaced_old])

    merged = setup_module.merge_manifest_records("project", [replaced_new])

    assert {item.link: item for item in merged} == {
        "old": stale,
        "same": record(setup_module, name="new", link="same", target="new-target", clients=("codex", "pi")),
    }


def test_create_link_refuses_real_files_and_force_only_overwrites_symlink_conflicts(setup_module, tmp_path):
    project = tmp_path / "project"
    setup_module._PROJECT_ROOT = project
    real_conflict = record(setup_module, link="links/real", target="targets/alpha")
    real_path = project / "links" / "real"
    real_path.parent.mkdir(parents=True)
    real_path.write_text("owned by user")

    assert setup_module.create_link(real_conflict, force=True) == "conflict: real file or directory exists"
    assert real_path.read_text() == "owned by user"

    symlink_conflict = record(setup_module, link="links/symlink", target="targets/alpha")
    symlink_path = project / "links" / "symlink"
    symlink_path.symlink_to("other-target")

    assert setup_module.create_link(symlink_conflict, force=False).startswith("conflict: symlink")
    assert os.readlink(symlink_path) == "other-target"
    assert setup_module.create_link(symlink_conflict, force=True) == "created"
    assert os.readlink(symlink_path) == "../targets/alpha"


def test_create_link_updates_manifest_owned_previous_symlink_without_force(setup_module, tmp_path):
    project = tmp_path / "project"
    setup_module._PROJECT_ROOT = project
    previous = record(setup_module, link="links/skill", target="old/SKILL.md", source_kind="skill_md")
    current = record(setup_module, link="links/skill", target="new", source_kind="skill_dir")
    link_path = project / "links" / "skill"
    link_path.parent.mkdir(parents=True)
    link_path.symlink_to("../old/SKILL.md")

    assert setup_module.create_link(current, force=False, previous_record=previous) == "updated"
    assert os.readlink(link_path) == "../new"


def test_create_link_does_not_treat_unexpected_symlink_as_manifest_owned(setup_module, tmp_path):
    project = tmp_path / "project"
    setup_module._PROJECT_ROOT = project
    previous = record(setup_module, link="links/skill", target="old/SKILL.md", source_kind="skill_md")
    current = record(setup_module, link="links/skill", target="new", source_kind="skill_dir")
    link_path = project / "links" / "skill"
    link_path.parent.mkdir(parents=True)
    link_path.symlink_to("../manual-target")

    assert setup_module.create_link(current, force=False, previous_record=previous).startswith("conflict: symlink")
    assert os.readlink(link_path) == "../manual-target"


def test_install_scope_updates_manifest_owned_previous_symlink_and_manifest(setup_module, tmp_path, monkeypatch):
    project = tmp_path / "project"
    source = tmp_path / "source"
    skill_dir = make_skill(source / "skills" / "alpha")
    setup_module._PROJECT_ROOT = project
    monkeypatch.setattr(setup_module, "common_root", lambda: source)
    previous = record(setup_module, link=".agents/skills/alpha", target="old/SKILL.md", source_kind="skill_md")
    link_path = project / ".agents" / "skills" / "alpha"
    link_path.parent.mkdir(parents=True)
    link_path.symlink_to("../../old/SKILL.md")
    monkeypatch.setattr(setup_module, "git_revision", lambda path: "test-revision")
    setup_module.write_manifest("project", [previous])

    stats = setup_module.install_scope(
        "project",
        {"pi"},
        setup_module.SkillSelection(include=frozenset({"alpha"})),
        force=False,
        dry_run=False,
    )

    assert stats["updated"] == 1
    assert os.readlink(link_path) == os.path.relpath(skill_dir, link_path.parent)
    manifest = setup_module.read_manifest("project")
    assert manifest["links"][0]["target"] == str(skill_dir)
    assert manifest["links"][0]["source_kind"] == "skill_dir"


def test_remove_record_only_removes_expected_manifest_owned_symlinks(setup_module, tmp_path):
    project = tmp_path / "project"
    setup_module._PROJECT_ROOT = project
    expected_record = record(setup_module, link="links/owned", target="targets/alpha")
    link_path = project / "links" / "owned"
    link_path.parent.mkdir(parents=True)
    link_path.symlink_to("unexpected")

    assert not setup_module.remove_record(expected_record, dry_run=False)
    assert link_path.is_symlink()

    link_path.unlink()
    link_path.symlink_to("../targets/alpha")
    assert setup_module.remove_record(expected_record, dry_run=False)
    assert not link_path.exists() and not link_path.is_symlink()


def test_uninstall_removes_only_selected_client_ownership_for_shared_destinations(setup_module, tmp_path, monkeypatch):
    project = tmp_path / "project"
    source = tmp_path / "source"
    setup_module._PROJECT_ROOT = project
    monkeypatch.setattr(setup_module, "common_root", lambda: source)
    monkeypatch.setattr(setup_module, "git_revision", lambda path: "test-revision")
    shared_record = record(
        setup_module,
        link=".agents/skills/alpha",
        target="targets/alpha",
        clients=("codex", "pi"),
    )
    link_path = project / ".agents" / "skills" / "alpha"
    link_path.parent.mkdir(parents=True)
    link_path.symlink_to("../../targets/alpha")
    setup_module.write_manifest("project", [shared_record])

    setup_module.uninstall_scope("project", {"pi"}, setup_module.SkillSelection(), dry_run=False)

    assert link_path.is_symlink()
    manifest_record = setup_module.managed_records("project")[0]
    assert manifest_record.clients == ("codex",)


def test_stale_records_respects_skill_and_client_filters(setup_module, monkeypatch):
    current = record(setup_module, name="current", link="current", target="target")
    stale = record(setup_module, name="stale", link="stale", target="target")
    other_client = record(setup_module, destination_id="claude", name="stale", link="claude", target="target")
    excluded = record(setup_module, name="excluded", link="excluded", target="target")
    monkeypatch.setattr(setup_module, "plan_links", lambda scope, clients, selection: [current])
    monkeypatch.setattr(setup_module, "managed_records", lambda scope: [current, stale, other_client, excluded])
    selection = setup_module.SkillSelection(include=frozenset({"current", "stale", "excluded"}), exclude=frozenset({"excluded"}))

    assert setup_module.stale_records("project", {"pi"}, selection) == [stale]


def test_stale_records_treats_shared_agents_records_as_codex_pi_opencode(setup_module, monkeypatch):
    current = record(setup_module, name="current", link="current", target="target")
    stale = record(setup_module, name="stale", link="stale", target="target")
    old_native_pi = record(setup_module, destination_id="pi", name="old-pi", link=".pi/skills/old-pi", target="target")
    monkeypatch.setattr(setup_module, "plan_links", lambda scope, clients, selection: [current])
    monkeypatch.setattr(setup_module, "managed_records", lambda scope: [current, stale, old_native_pi])

    assert setup_module.stale_records("project", {"pi"}, setup_module.SkillSelection()) == [stale, old_native_pi]


def test_client_dirs_are_derived_from_install_destinations_with_unmanaged_extras(setup_module, tmp_path):
    setup_module._PROJECT_ROOT = tmp_path / "project"

    assert setup_module.client_dirs("project", {"codex", "cline"}) == [
        setup_module._PROJECT_ROOT / ".agents",
        setup_module._PROJECT_ROOT / ".cline",
        setup_module._PROJECT_ROOT / ".clinerules",
    ]


def test_run_command_stops_update_when_git_pull_fails(setup_module, tmp_path, monkeypatch, capsys):
    project = tmp_path / "project"
    source = tmp_path / "source"
    project.mkdir()
    (source / ".git").mkdir(parents=True)
    monkeypatch.setattr(setup_module, "common_root", lambda: source)

    def fail_git_pull(*args, **kwargs):
        raise setup_module.subprocess.CalledProcessError(1, ["git", "pull"])

    monkeypatch.setattr(setup_module.subprocess, "run", fail_git_pull)
    monkeypatch.setattr(setup_module, "install_scope", lambda *args, **kwargs: pytest.fail("install should not run"))
    args = setup_module.parser().parse_args(["update", "--project", str(project), "--client", "pi"])

    assert setup_module.run_command(args) == 2
    assert "Failed to update shared skills source" in capsys.readouterr().out


def test_run_command_rejects_malformed_manifest_without_overwriting(setup_module, tmp_path, capsys):
    project = tmp_path / "project"
    manifest = project / ".my-agent-config" / "manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("{")
    args = setup_module.parser().parse_args(["status", "--project", str(project), "--client", "pi"])

    assert setup_module.run_command(args) == 2
    assert "Malformed manifest" in capsys.readouterr().out
    assert manifest.read_text() == "{"

