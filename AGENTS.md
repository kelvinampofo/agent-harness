# Repository instructions

Follow these rules and the [personal instructions](instructions/AGENTS.md). Setup installs only the latter for use in all projects.

## Scope

Base each change on a real workflow or an observed failure.

## Routing

Read only what the task needs.

- Installation: run `scripts/setup.py --help`.
- Session review and harness improvement: [improve-harness](skills/improve-harness/SKILL.md).
- Harness overview: [README](README.md#how-it-works).

## Organisation

- Keep repository rules here and personal conventions in `instructions/AGENTS.md`.
- Keep skills in `skills/<skill-name>/SKILL.md`, following the [Agent Skills specification](https://agentskills.io/specification). Match the frontmatter name to the directory.
- Keep skill-specific scripts and references with their skill. Put shared and maintenance tools in `scripts/`.
- Keep the overview in README and command usage in `--help`. Document each rule or command in one place.

## Validation

Check that referenced paths and tools exist. Run changed scripts, including their error paths. Report what you checked and what you could not.

## Cleanup

When a workflow changes, correct existing documentation that becomes inaccurate. Add documentation only when requested or needed to use the changed workflow.
