#!/usr/bin/env python3
"""Install shared instructions and skills through symlinks."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

NEEDS_ATTENTION = {"missing", "stale", "orphaned"}


# a link maps a source to a destination, with kind, backup, orphan, and status
Link = dict[str, Any]


def new_link(kind: str, source: Path, destination: Path, orphan: bool = False) -> Link:
    return {
        "kind": kind,
        "source": source,
        "destination": destination,
        "backup": None,
        "orphan": orphan,
        "status": "",
    }


def reported_backup(link: Link) -> Path | None:
    # check mode only inspects an existing entry, so it has no backup to report
    return None if link["status"] == "stale" else link["backup"]


def link_json(link: Link) -> dict[str, str]:
    result = {
        "kind": link["kind"],
        "destination": str(link["destination"]),
        "source": str(link["source"]),
        "status": link["status"],
    }
    backup = reported_backup(link)
    if backup:
        result["backup"] = str(backup)
    return result


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Defaults:
  instructions  ~/.codex/AGENTS.md, ~/.claude/CLAUDE.md
  skills        ~/.agents/skills, ~/.claude/skills

Custom destinations replace all defaults, for example:
  scripts/setup.py --skills ~/.kiro/skills --skills ~/.agents/skills
Pass the same destinations to --check and --dry-run. For a custom
CODEX_HOME, pass its instruction path.

Setup stops at existing entries. Inspect them, then rerun with
--backup-existing to rename them to *.pre-harness. Existing backups,
non-empty AGENTS.override.md files, and overlapping paths also stop it.

Rerun after adding or removing skills. Setup removes links to deleted
skills, which --check reports as orphaned. After moving the checkout,
rerun with --backup-existing.

Exit codes: 0 success, 1 links need attention, 2 invalid arguments, 3 failure.""",
    )
    parser.add_argument(
        "--instructions",
        type=Path,
        action="append",
        help="instruction file destination (repeatable)",
    )
    parser.add_argument(
        "--skills",
        type=Path,
        action="append",
        help="skill directory destination (repeatable)",
    )
    parser.add_argument(
        "--home", type=Path, default=Path.home(), help="home for default destinations"
    )
    parser.set_defaults(mode="install")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--check",
        action="store_const",
        dest="mode",
        const="check",
        help="validate without changing files",
    )
    modes.add_argument(
        "--dry-run",
        action="store_const",
        dest="mode",
        const="dry-run",
        help="preview installation without changing files",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print machine-readable link results; errors are written to stdout as JSON",
    )
    parser.add_argument(
        "--backup-existing",
        action="store_true",
        help="preserve conflicts with a .pre-harness suffix",
    )
    return parser.parse_args()


def paths_overlap(first: Path, second: Path) -> bool:
    return first == second or first in second.parents or second in first.parents


def resolve_destination(path: Path) -> Path:
    path = path.expanduser().absolute()
    # resolve parent aliases without following the link being replaced
    return path.parent.resolve() / path.name


def plan_links(
    root: Path, instructions: list[Path], skill_directories: list[Path]
) -> tuple[list[Link], list[Path]]:
    skill_sources = sorted(path.parent for path in (root / "skills").glob("*/SKILL.md"))
    if skill_directories and not skill_sources:
        raise ValueError("No skills found")
    links = [
        new_link(
            "instructions", root / "instructions/AGENTS.md", resolve_destination(path)
        )
        for path in instructions
    ]
    links.extend(
        new_link("skill", source, resolve_destination(directory / source.name))
        for directory in skill_directories
        for source in skill_sources
    )
    return links, skill_sources


def validate_link(
    link: Link, protected_sources: list[Path], mode: str, backup_existing: bool
) -> None:
    destination = link["destination"]
    if any(paths_overlap(destination, source) for source in protected_sources):
        raise ValueError(f"Destination overlaps a source: {destination}")
    if not link["source"].exists():
        raise ValueError(f"Missing source: {link['source']}")
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

    if destination.is_symlink() and destination.resolve() == link["source"]:
        link["status"] = "ready"
        return
    if not (destination.exists() or destination.is_symlink()):
        return
    link["backup"] = destination.with_name(destination.name + ".pre-harness")
    if mode == "check":
        return
    if not backup_existing:
        raise ValueError(
            f"Existing entry: {destination}. Inspect it and use --backup-existing"
        )
    if link["backup"].exists() or link["backup"].is_symlink():
        raise ValueError(f"Backup already exists: {link['backup']}")


def validate_layout(links: list[Link]) -> None:
    destinations = {link["destination"] for link in links}
    for link in links:
        if any(parent in destinations for parent in link["destination"].parents):
            raise ValueError(
                f"Overlapping destinations: {link['destination']}. Use separate instruction and skill paths"
            )
        if link["backup"] and any(
            paths_overlap(link["backup"], destination) for destination in destinations
        ):
            raise ValueError(f"Backup overlaps a destination: {link['backup']}")


def find_orphans(
    root: Path,
    skill_directories: list[Path],
    skill_sources: list[Path],
    links: list[Link],
) -> list[Link]:
    destinations = {link["destination"] for link in links}
    orphans = []
    for directory in skill_directories:
        directory = directory.expanduser().absolute().resolve()
        if not directory.is_dir():
            continue
        for entry in sorted(directory.iterdir()):
            if not entry.is_symlink() or entry in destinations:
                continue
            target = Path(os.path.normpath(entry.parent / os.readlink(entry)))
            if target.parent == root / "skills" and target not in skill_sources:
                orphans.append(new_link("skill", target, entry, orphan=True))
    return orphans


def plan_installation(
    root: Path,
    home: Path,
    instructions: list[Path],
    skill_directories: list[Path],
    mode: str,
    backup_existing: bool,
) -> list[Link]:
    if not instructions and not skill_directories:
        instructions = [home / ".codex/AGENTS.md", home / ".claude/CLAUDE.md"]
        skill_directories = [home / ".agents/skills", home / ".claude/skills"]

    links, skill_sources = plan_links(root, instructions, skill_directories)
    seen = set()
    for link in links:
        if link["destination"] in seen:
            raise ValueError(f"Duplicate destination: {link['destination']}")
        seen.add(link["destination"])

    protected_sources = [root / "instructions/AGENTS.md", *skill_sources]
    for link in links:
        validate_link(link, protected_sources, mode, backup_existing)
    validate_layout(links)
    return links + find_orphans(root, skill_directories, skill_sources, links)


def apply_links(links: list[Link], mode: str) -> None:
    for link in links:
        if link["status"] == "ready":
            continue
        if mode == "check":
            if link["orphan"]:
                link["status"] = "orphaned"
            else:
                link["status"] = "stale" if link["backup"] else "missing"
        elif mode == "dry-run":
            link["status"] = "would-remove" if link["orphan"] else "would-link"
        elif link["orphan"]:
            link["destination"].unlink()
            link["status"] = "removed"
        else:
            link["destination"].parent.mkdir(parents=True, exist_ok=True)
            if link["backup"]:
                link["destination"].rename(link["backup"])
            link["destination"].symlink_to(link["source"])
            link["status"] = "replaced" if link["backup"] else "linked"


def display_path(path: Path, home: Path) -> str:
    try:
        return "~/" + str(path.relative_to(home))
    except ValueError:
        return str(path)


def print_summary(links: list[Link], mode: str, home: Path) -> None:
    labels = {
        home / ".claude": "Claude Code",
        home / ".claude/skills": "Claude Code",
        home / ".codex": "Codex",
        home / ".agents/skills": "Codex, OpenCode, Pi",
        home / ".kiro/skills": "Kiro",
    }
    groups: dict[str, list[Link]] = {}
    for link in links:
        label = labels.get(link["destination"].parent, str(link["destination"].parent))
        groups.setdefault(label, []).append(link)
    for label, group in groups.items():
        print(f"\n{label}")
        for link in group:
            print(
                f"  {link['kind']:<12}  {link['status']:<12}  {display_path(link['destination'], home)}"
            )
            if reported_backup(link):
                print(f"    backup: {display_path(reported_backup(link), home)}")
    if mode == "dry-run":
        print("\nDry run. No files changed.")
    elif mode == "check":
        if any(link["status"] in NEEDS_ATTENTION for link in links):
            print("\nSome links need attention. Run setup to repair them.")
        else:
            print("\nAll links are correct.")
    else:
        print("\nStart a new agent session to use the harness.")


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        home = args.home.expanduser().resolve()
        links = plan_installation(
            root,
            home,
            args.instructions or [],
            args.skills or [],
            args.mode,
            args.backup_existing,
        )
        apply_links(links, args.mode)
        if args.json:
            print(
                json.dumps(
                    {"mode": args.mode, "links": [link_json(link) for link in links]}
                )
            )
        else:
            print_summary(links, args.mode, home)
        return 1 if any(link["status"] in NEEDS_ATTENTION for link in links) else 0
    except (OSError, RuntimeError, ValueError) as error:
        if args.json:
            print(json.dumps({"mode": args.mode, "error": str(error)}))
        else:
            print(f"error: {error}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
