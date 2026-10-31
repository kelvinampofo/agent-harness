#!/usr/bin/env python3
"""Install shared agent instructions and skills."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Callable, Iterable, NamedTuple

ROOT = Path(__file__).resolve().parents[1]
INSTRUCTIONS = ROOT / "instructions/AGENTS.md"


class Agent(NamedTuple):
    name: str
    instruction_file: str
    skill_directory: str


class Link(NamedTuple):
    # a missing source marks an entry for removal
    source: Path | None
    destination: Path
    status: str


AGENTS = (
    Agent("Claude Code", ".claude/CLAUDE.md", ".claude/skills"),
    Agent("Codex", ".codex/AGENTS.md", ".agents/skills"),
)


def same_file(first: Path, second: Path) -> bool:
    # path comparison misses aliases on case-insensitive file systems
    try:
        return first.samefile(second)
    except OSError:
        return False


def backup_path(destination: Path) -> Path:
    return destination.with_name(destination.name + ".pre-harness")


def display_path(home: Path, path: Path) -> str:
    if home in path.parents:
        return f"~/{path.relative_to(home)}"
    return str(path)


def instruction_links(home: Path) -> list[tuple[Path, Path]]:
    return [(INSTRUCTIONS, home / agent.instruction_file) for agent in AGENTS]


def skill_links(home: Path, skills: Iterable[Path]) -> list[tuple[Path, Path]]:
    return [
        (skill, home / agent.skill_directory / skill.name)
        for agent in AGENTS
        for skill in skills
    ]


def validate_links(links: list[tuple[Path, Path]]) -> list[tuple[Path, Path]]:
    validated = []
    seen = set()
    for source, destination in links:
        # resolve parent aliases without following the link being replaced
        destination = destination.parent.resolve() / destination.name
        if destination in seen:
            continue
        seen.add(destination)

        if (
            destination == ROOT
            or ROOT in destination.parents
            or destination in ROOT.parents
        ):
            raise ValueError(
                f"Destination overlaps the repository: {destination}"
            )
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

        validated.append((source, destination))
    return validated


def link_status(source: Path, destination: Path) -> str:
    if destination.is_symlink() and same_file(destination, source):
        return "ready"
    if destination.exists() or destination.is_symlink():
        return "stale"
    return "missing"


def plan_installs(links: list[tuple[Path, Path]]) -> list[Link]:
    return [
        Link(source, destination, link_status(source, destination))
        for source, destination in links
    ]


def plan_removals(links: list[tuple[Path, Path]]) -> list[Link]:
    plan = []
    for source, destination in links:
        status = link_status(source, destination)
        if status == "stale":
            raise ValueError(
                f"Refusing to unlink an entry not linked to {source}: "
                f"{destination}"
            )
        if status == "ready":
            plan.append(Link(None, destination, "pending"))
        else:
            plan.append(Link(None, destination, "ready"))
    return plan


def plan_orphans(
    home: Path, skills: Iterable[Path], plan: list[Link]
) -> list[Link]:
    orphans = []
    seen = {link.destination for link in plan}
    for agent in AGENTS:
        directory = (home / agent.skill_directory).resolve()
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
            if same_file(target.parent, ROOT / "skills") and not any(
                same_file(target, skill) for skill in skills
            ):
                orphans.append(Link(None, entry, "orphaned"))
                seen.add(entry)
    return orphans


def require_replaceable(plan: list[Link], backup_existing: bool) -> None:
    for link in plan:
        if link.status != "stale":
            continue
        if not backup_existing:
            raise ValueError(
                f"Existing entry: {link.destination}. "
                "Inspect it and rerun with --backup-existing"
            )
        backup = backup_path(link.destination)
        if backup.exists() or backup.is_symlink():
            raise ValueError(f"Backup already exists: {backup}")


def inspect_link(link: Link) -> str:
    return link.status


def preview_link(link: Link) -> str:
    if link.status == "ready":
        return "ready"
    if link.source is None:
        return "would-remove"
    return "would-link"


def apply_link(home: Path, link: Link) -> str:
    if link.status == "ready":
        return "ready"
    if link.source is None:
        link.destination.unlink()
        return "removed"

    link.destination.parent.mkdir(parents=True, exist_ok=True)
    if link.status == "stale":
        link.destination.rename(backup_path(link.destination))
        print(
            f"    backup: {display_path(home, link.destination)}.pre-harness"
        )
    link.destination.symlink_to(link.source)
    return "linked"


def destination_owners(home: Path) -> dict[Path, list[Agent]]:
    owners: dict[Path, list[Agent]] = {}
    for agent in AGENTS:
        directories = {
            (home / agent.skill_directory).resolve(),
            (home / agent.instruction_file).parent.resolve(),
        }
        for directory in directories:
            owners.setdefault(directory, []).append(agent)
    return owners


def process_plan(
    home: Path, plan: list[Link], act: Callable[[Link], str]
) -> None:
    owners = destination_owners(home)
    links_by_owner: dict[str, list[Link]] = {}
    for link in plan:
        label = ", ".join(
            agent.name for agent in owners[link.destination.parent]
        )
        links_by_owner.setdefault(label, []).append(link)

    for label, links in links_by_owner.items():
        print(f"\n{label}")
        for link in links:
            kind = "skill"
            if link.source == INSTRUCTIONS:
                kind = "instructions"
            status = act(link)
            path = display_path(home, link.destination)
            print(f"  {kind:12}  {status:12}  {path}")


def run_setup(args: argparse.Namespace, skills: dict[str, Path]) -> int:
    if not skills:
        raise ValueError("No skills found")

    home = Path.home().resolve()
    selection = args.skill or args.unlink_skill
    if selection:
        requested = [
            path for name, path in skills.items() if name in selection
        ]
        links = skill_links(home, requested)
    else:
        links = instruction_links(home) + skill_links(home, skills.values())
    links = validate_links(links)

    if args.unlink_skill:
        plan = plan_removals(links)
    else:
        plan = plan_installs(links)
        if not selection:
            plan += plan_orphans(home, skills.values(), plan)

    if args.check:
        process_plan(home, plan, inspect_link)
        if any(link.status != "ready" for link in plan):
            print("\nSetup needs attention.")
            return 1
        print("\nSetup is correct.")
        return 0

    require_replaceable(plan, args.backup_existing)
    if args.dry_run:
        process_plan(home, plan, preview_link)
        print("\nDry run. No files changed.")
    else:
        process_plan(home, plan, lambda link: apply_link(home, link))
        print("\nStart a new agent session to use the harness.")
    return 0


def build_parser(skills: dict[str, Path]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    setup = commands.add_parser(
        "setup",
        help="install personal instructions and skills",
        description="Install personal agent instructions and skills.",
        allow_abbrev=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  scripts/harness.py setup                  Install the harness
  scripts/harness.py setup --dry-run        Preview changes
  scripts/harness.py setup --skill explain  Install one skill

Exit status of --check:
  0  setup is correct
  1  setup needs attention
  3  inspection failed
""",
    )
    modes = setup.add_mutually_exclusive_group()
    modes.add_argument(
        "--check",
        action="store_true",
        help="check installation without changing files",
    )
    modes.add_argument(
        "--dry-run",
        action="store_true",
        help="preview changes without applying them",
    )
    setup.add_argument(
        "--backup-existing",
        action="store_true",
        help="back up existing files before replacing them",
    )
    selection = setup.add_mutually_exclusive_group()
    selection.add_argument(
        "--skill",
        action="append",
        choices=skills,
        default=[],
        metavar="NAME",
        help="install only the named skill (repeatable)",
    )
    selection.add_argument(
        "--unlink-skill",
        action="append",
        choices=skills,
        default=[],
        metavar="NAME",
        help="temporarily unlink a skill (repeatable)",
    )
    return parser


def main() -> int:
    skills = {
        path.parent.name: path.parent
        for path in sorted((ROOT / "skills").glob("*/SKILL.md"))
    }
    parser = build_parser(skills)
    args = parser.parse_args()
    if args.unlink_skill and (args.check or args.backup_existing):
        parser.error(
            "--unlink-skill cannot be combined with --check or "
            "--backup-existing"
        )
    return run_setup(args, skills)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(
            f"error: {error}\n"
            "Fix the error and rerun. Completed links are kept.",
            file=sys.stderr,
        )
        sys.exit(3)
    except KeyboardInterrupt:
        print("\nCancelled. Rerun to finish setup.", file=sys.stderr)
        sys.exit(130)
