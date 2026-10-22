#!/usr/bin/env python3
"""Install personal agent instructions and skills."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def plan_links(
    root: Path, home: Path, args: argparse.Namespace
) -> list[tuple[Path | None, Path, str]]:
    skills = sorted(path.parent for path in (root / "skills").glob("*/SKILL.md"))
    if not skills:
        raise ValueError("No skills found")

    skill_directories = [home / ".agents/skills", home / ".claude/skills"]
    links = [
        (root / "instructions/AGENTS.md", home / ".codex/AGENTS.md"),
        (root / "instructions/AGENTS.md", home / ".claude/CLAUDE.md"),
    ]
    links.extend(
        (source, directory / source.name)
        for directory in skill_directories
        for source in skills
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

        if destination.is_symlink() and destination.resolve() == source:
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
            if target.parent == root / "skills" and target not in skills:
                plan.append((None, entry, "orphaned"))
                seen.add(entry)

    return plan


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        allow_abbrev=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Destinations:
  ~/.codex/AGENTS.md, ~/.claude/CLAUDE.md
  ~/.agents/skills, ~/.claude/skills

Existing entries require --backup-existing, which preserves them with a
.pre-harness suffix. Existing backups and non-empty AGENTS.override.md
files stop setup. Custom destinations are not supported.

Rerun after adding or removing skills. Only links to deleted skills in
this repository are removed; other skills and backups are kept.
Start a new agent session after setup.

Exit codes: 0 success, 1 links need attention, 2 invalid arguments, 3 failure.""",
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--check", action="store_true", help="check links without changing files"
    )
    modes.add_argument(
        "--dry-run", action="store_true", help="preview setup without changing files"
    )
    parser.add_argument(
        "--backup-existing",
        action="store_true",
        help="preserve conflicting entries before linking",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
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
        print(
            "\nSome links need attention."
            if needs_attention
            else "\nAll links are correct."
        )
    elif args.dry_run:
        print("\nDry run. No files changed.")
    else:
        print("\nStart a new agent session to use the harness.")

    return int(args.check and needs_attention)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(
            f"error: {error}\nFix the error and rerun; completed links are kept.",
            file=sys.stderr,
        )
        sys.exit(3)
    except KeyboardInterrupt:
        print("\nCancelled. Rerun to finish setup.", file=sys.stderr)
        sys.exit(130)
