#!/usr/bin/env python3
"""User skills setup script.

Wires user skills into all tool directories with per-file symlinks.
Supports install and update subcommands.
Prioritizes project-specific skills (overrides) over common skills.
"""

import os
import sys
from pathlib import Path
import subprocess


def get_project_root() -> Path:
    """Return project root directory (parent of .agent-config)."""
    # common/setup.py -> common -> user -> .agent-config -> project_root
    return Path(__file__).parent.parent.parent.parent


def discover_skills(skills_dir: Path) -> dict[str, Path]:
    """Discover all skill directories containing SKILL.md.

    Returns:
        Dict mapping skill_name -> path_to_skill_dir
    """
    if not skills_dir.exists():
        return {}

    skills = {}
    for item in skills_dir.iterdir():
        if item.is_dir() and (item / "SKILL.md").exists():
            skills[item.name] = item

    return skills


def confirm_action(message: str) -> bool:
    """Ask user for confirmation."""
    while True:
        response = input(f"{message} [y/N]: ").strip().lower()
        if response == "y":
            return True
        if response == "n" or response == "":
            return False


def create_relative_symlink(target: Path, link: Path) -> None:
    """Create a relative symlink from link to target with safety checks."""
    # Ensure parent directory exists
    link.parent.mkdir(parents=True, exist_ok=True)

    # Calculate relative path from link to target
    rel_target = os.path.relpath(target, link.parent)

    # Check if link exists
    if link.is_symlink():
        current_target = os.readlink(link)
        if current_target == rel_target:
            return  # Already correct

        # Link exists but points elsewhere
        print(f"\nConflict for '{link.name}':")
        print(f"  Current: {current_target}")
        print(f"  New:     {rel_target}")
        if not confirm_action("  Overwrite?"):
            print("  Skipping.")
            return
        link.unlink()

    elif link.exists():
        # Exists but not a symlink
        print(f"\nConflict for '{link.name}': File exists and is not a symlink.")
        if not confirm_action("  Delete and link?"):
            print("  Skipping.")
            return
        link.unlink()

    # Create symlink
    link.symlink_to(rel_target)


def install_skills(project_root: Path, verbose: bool = True) -> dict[str, int]:
    """Install user skills into all tool directories.

    Returns dict with counts: {added: N, overridden: N}
    """
    # Define paths
    user_repo_root = project_root / ".agent-config" / "user"
    project_skills_dir = user_repo_root / "skills"
    common_skills_dir = user_repo_root / "common" / "skills"
    convergence_dir = project_root / ".agents" / "skills"

    # Discover skills
    project_skills = discover_skills(project_skills_dir)
    common_skills = discover_skills(common_skills_dir)

    # Merge skills (Project overrides Common)
    all_skills = common_skills.copy()

    for name, path in project_skills.items():
        if name in all_skills:
            print(f"\nCollision detected for skill '{name}':")
            print(f"  [1] Project Specific (Override)")
            print(f"  [2] Common (Submodule)")

            choice = ""
            while choice not in ["1", "2"]:
                choice = input("  Which version should be installed? [1/2]: ").strip()

            if choice == "1":
                print(f"  Selecting Project override for '{name}'")
                all_skills[name] = path
            else:
                print(f"  Keeping Common version for '{name}'")
                # all_skills[name] already points to common_skills[name]
        else:
            all_skills[name] = path

    skills_to_install = sorted(all_skills.keys())

    if not skills_to_install:
        if verbose:
            print("No user skills found.")
        return {"added": 0, "overridden": 0}

    # Create convergence directory
    convergence_dir.mkdir(parents=True, exist_ok=True)

    # Track stats
    installed_count = 0
    team_override_count = 0

    # Check for team skills that will be overridden
    team_skills = set()
    if convergence_dir.exists():
        for item in convergence_dir.iterdir():
            if item.is_symlink():
                team_skills.add(item.name)

    # Create symlinks for each skill
    for skill_name in skills_to_install:
        skill_dir = all_skills[skill_name]
        skill_md = skill_dir / "SKILL.md"

        # Check if overriding team skill
        if skill_name in team_skills:
            team_override_count += 1
            if verbose:
                print(f"Warning: user skill '{skill_name}' overrides team skill")
        else:
            installed_count += 1

        # Convergence point: .agents/skills/<name> → skill directory
        create_relative_symlink(skill_dir, convergence_dir / skill_name)

        # Claude Code: .claude/skills/<name> → skill directory
        create_relative_symlink(skill_dir, project_root / ".claude" / "skills" / skill_name)

        # Pi: .pi/skills/<name> → skill directory
        create_relative_symlink(skill_dir, project_root / ".pi" / "skills" / skill_name)

        # Cursor: .cursor/skills/<name> → skill directory
        create_relative_symlink(skill_dir, project_root / ".cursor" / "skills" / skill_name)

        # Cursor commands: .cursor/commands/<name>.md → SKILL.md file
        create_relative_symlink(
            skill_md, project_root / ".cursor" / "commands" / f"{skill_name}.md"
        )

        # OpenCode commands: .opencode/commands/<name>.md → SKILL.md file
        create_relative_symlink(
            skill_md, project_root / ".opencode" / "commands" / f"{skill_name}.md"
        )

        # Codex prompts: .codex/prompts/<name>.md → SKILL.md file
        create_relative_symlink(skill_md, project_root / ".codex" / "prompts" / f"{skill_name}.md")

        # Cline workflows: .clinerules/workflows/<name>.md → SKILL.md file
        create_relative_symlink(
            skill_md, project_root / ".clinerules" / "workflows" / f"{skill_name}.md"
        )

    # Create system prompt wiring for Cline
    agents_md = project_root / "AGENTS.md"
    if agents_md.exists():
        create_relative_symlink(agents_md, project_root / ".clinerules" / "system.md")

    if verbose:
        print(f"Installed {len(skills_to_install)} user skills:")
        for skill in skills_to_install:
            source = "Project" if skill in project_skills else "Common"
            print(f"  - {skill} ({source})")
        print(f"\nSymlinks created in:")
        print(f"  - .agents/skills/ (convergence)")
        print(f"  - .opencode/commands/")
        print(f"  - .claude/skills/")
        print(f"  - .cursor/skills/")
        print(f"  - .cursor/commands/")
        print(f"  - .pi/skills/")
        print(f"  - .codex/prompts/")
        print(f"  - .clinerules/workflows/")

    return {"added": installed_count, "overridden": team_override_count}


def update_skills(project_root: Path) -> dict[str, int]:
    """Update user skills (pull if git repo, then reinstall)."""
    user_dir = project_root / ".agent-config" / "user"
    common_dir = user_dir / "common"

    # 1. Update User Dir (Parent)
    if (user_dir / ".git").exists():
        print("Pulling latest user customizations...")
        try:
            # We use --rebase to keep history clean, but capture failure if no remote
            subprocess.run(
                ["git", "pull", "--rebase"],
                cwd=user_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            print("✓ User customizations updated")
        except subprocess.CalledProcessError:
            print("Note: Skipping pull for user customizations (remote may not be configured)")

    # 2. Update Common Submodule
    if (common_dir / ".git").exists():
        print("Updating shared skills...")

        # Check if it's a submodule of the user dir
        is_submodule = False
        if (user_dir / ".git").exists():
            res = subprocess.run(
                ["git", "submodule", "status", "common"],
                cwd=user_dir,
                capture_output=True,
                text=True,
            )
            is_submodule = res.returncode == 0

        if is_submodule:
            try:
                subprocess.run(
                    ["git", "submodule", "update", "--init", "--recursive", "--remote"],
                    cwd=user_dir,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                print("✓ Shared skills updated (via submodule)")
            except subprocess.CalledProcessError as e:
                print(f"Warning: Submodule update failed: {e.stderr}")
        else:
            # Fallback to direct pull if it's just a clone
            try:
                subprocess.run(
                    ["git", "pull"], cwd=common_dir, check=True, capture_output=True, text=True
                )
                print("✓ Shared skills updated (via pull)")
            except subprocess.CalledProcessError:
                print("Note: Skipping pull for shared skills (remote may not be configured)")

    # Reinstall (smart link update)
    print("\nReinstalling skills...")
    # clean_skill_symlinks is removed to avoid destructive behavior without confirmation
    # install_skills will handle updates safely
    return install_skills(project_root)


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python setup.py [install|update]")
        return 1

    command = sys.argv[1]
    project_root = get_project_root()

    if command == "install":
        stats = install_skills(project_root)
        if stats["overridden"] > 0:
            print(f"\n⚠️  {stats['overridden']} team skill(s) overridden by user skills")
        return 0

    elif command == "update":
        stats = update_skills(project_root)
        print(f"\n✓ Update complete:")
        print(f"  - {stats['added']} skills added/refreshed")
        if stats["overridden"] > 0:
            print(f"  - {stats['overridden']} team skills overridden")
        return 0

    else:
        print(f"Unknown command: {command}")
        print("Usage: python setup.py [install|update]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
