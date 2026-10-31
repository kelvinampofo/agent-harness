#!/usr/bin/env python3
"""Install personal agent instructions and skills."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def same_file(first: Path, second: Path) -> bool:
    # path comparison misses aliases on case-insensitive file systems
    try:
        return first.samefile(second)
    except OSError:
        return False


def plan_links(
    root: Path, home: Path, args: argparse.Namespace
) -> list[tuple[Path | None, Path, str]]:
    skills = sorted(path.parent for path in (root / "skills").glob("*/SKILL.md"))
    if not skills:
        raise ValueError("No skills found")

    selection = args.skill or args.unlink_skill
    selected_skills = (
        [path for path in skills if path.name in selection] if selection else skills
    )

    skill_directories = [home / ".agents/skills", home / ".claude/skills"]
    links = [
        (root / "instructions/AGENTS.md", home / ".codex/AGENTS.md"),
        (root / "instructions/AGENTS.md", home / ".claude/CLAUDE.md"),
    ]
    if selection:
        links = []
    links.extend(
        (source, directory / source.name)
        for directory in skill_directories
        for source in selected_skills
    )

    plan = []
    seen = set()
    for source, destination in links:
        # resolve parent aliases without following the link being replaced
        destination = destination.parent.resolve() / destination.name
        if destination in seen:
            continue
        seen.add(destination)

        if (
            destination == root
            or root in destination.parents
            or destination in root.parents
        ):
            raise ValueError(f"Destination overlaps the repository: {destination}")
        if not source.exists():
            raise ValueError(f"Missing source: {source}")
        for parent in destination.parents:
            if parent.exists() and not parent.is_dir():
                raise ValueError(f"Parent is not a directory: {parent}")

        override = destination.with_name("AGENTS.override.md")
        if (
            destination.name == "AGENTS.md"
            and override.is_file()
            and override.read_text().strip()
        ):
            raise ValueError(f"Override takes precedence: {override}")

        if args.unlink_skill:
            if destination.is_symlink() and same_file(destination, source):
                plan.append((None, destination, "linked"))
            elif destination.exists() or destination.is_symlink():
                raise ValueError(
                    f"Refusing to unlink an entry not linked to {source}: {destination}"
                )
            else:
                plan.append((None, destination, "ready"))
            continue

        if destination.is_symlink() and same_file(destination, source):
            status = "ready"
        elif destination.exists() or destination.is_symlink():
            status = "stale"
            if not args.check:
                backup = destination.with_name(destination.name + ".pre-harness")
                if not args.backup_existing:
                    raise ValueError(
                        f"Existing entry: {destination}. Inspect it and rerun with --backup-existing"
                    )
                if backup.exists() or backup.is_symlink():
                    raise ValueError(f"Backup already exists: {backup}")
        else:
            status = "missing"
        plan.append((source, destination, status))

    if selection:
        return plan

    for directory in skill_directories:
        directory = directory.resolve()
        if not directory.is_dir():
            continue

        for entry in sorted(directory.iterdir()):
            if (
                not entry.is_symlink()
                or entry in seen
                or entry.name.endswith(".pre-harness")
            ):
                continue

            target = Path(os.path.normpath(entry.parent / os.readlink(entry)))
            if same_file(target.parent, root / "skills") and not any(
                same_file(target, skill) for skill in skills
            ):
                plan.append((None, entry, "orphaned"))
                seen.add(entry)

    return plan


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    skill_names = sorted(
        path.parent.name for path in (root / "skills").glob("*/SKILL.md")
    )
    available_skills = "\n  ".join(skill_names)
    parser = argparse.ArgumentParser(
        description=__doc__,
        allow_abbrev=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""Examples:
  scripts/setup.py                  Install the harness
  scripts/setup.py --dry-run        Preview changes
  scripts/setup.py --skill explain  Install one skill

Instructions:
  instructions/AGENTS.md

Skills:
  {available_skills}""",
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--check", action="store_true", help="check installation without changing files"
    )
    modes.add_argument(
        "--dry-run", action="store_true", help="preview changes without applying them"
    )
    parser.add_argument(
        "--backup-existing",
        action="store_true",
        help="back up existing files before replacing them",
    )
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--skill",
        action="append",
        choices=skill_names,
        default=[],
        metavar="NAME",
        help="install only the named skill (repeatable)",
    )
    selection.add_argument(
        "--unlink-skill",
        action="append",
        choices=skill_names,
        default=[],
        metavar="NAME",
        help="temporarily unlink a skill (repeatable)",
    )
    args = parser.parse_args()

    home = Path.home().resolve()
    plan = plan_links(root, home, args)

    labels = {
        (home / ".codex").resolve(): "Codex",
        (home / ".claude").resolve(): "Claude Code",
        (home / ".claude/skills").resolve(): "Claude Code",
        (home / ".agents/skills").resolve(): "Codex, OpenCode, Pi",
    }

    links_by_client = {}
    for source, destination, status in plan:
        label = labels.get(destination.parent, str(destination.parent))
        links_by_client.setdefault(label, []).append((source, destination, status))

    for label, links in links_by_client.items():
        print(f"\n{label}")
        for source, destination, status in links:
            path = (
                f"~/{destination.relative_to(home)}"
                if home in destination.parents
                else str(destination)
            )
            kind = (
                "instructions" if source == root / "instructions/AGENTS.md" else "skill"
            )

            if args.check or status == "ready":
                pass
            elif args.dry_run:
                status = "would-remove" if source is None else "would-link"
            elif source is None:
                destination.unlink()
                status = "removed"
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                if status == "stale":
                    backup = destination.with_name(destination.name + ".pre-harness")
                    destination.rename(backup)
                    print(f"    backup: {path}.pre-harness")
                destination.symlink_to(source)
                status = "linked"

            print(f"  {kind:12}  {status:12}  {path}")

    needs_attention = any(status != "ready" for _, _, status in plan)
    if args.check:
        print("\nSetup needs attention." if needs_attention else "\nSetup is correct.")
    elif args.dry_run:
        print("\nDry run. No files changed.")
    else:
        print("\nStart a new agent session to use the harness.")

    return int(args.check and needs_attention)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        print(
            f"error: {error}\nFix the error and rerun. Completed links are kept.",
            file=sys.stderr,
        )
        sys.exit(3)
    except KeyboardInterrupt:
        print("\nCancelled. Rerun to finish setup.", file=sys.stderr)
        sys.exit(130)
