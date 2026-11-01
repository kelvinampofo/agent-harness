# Repository instructions

- Follow [personal instructions](instructions/AGENTS.md). Setup installs only that file for other projects.
- Base changes on real workflows or observed failures. Read only what the task needs.
- For commands and installation, run `scripts/harness.py --help` and `scripts/harness.py setup --help`.
- For session reviews and harness improvements, use [improve-harness](skills/improve-harness/SKILL.md).
- For skill descriptions and scripts, read [description guidance](https://agentskills.io/skill-creation/optimizing-descriptions) and [script guidance](https://agentskills.io/skill-creation/using-scripts).
- Keep repository rules here, personal conventions in `instructions/AGENTS.md`, the overview in [README](README.md#how-it-works), and command usage in `--help`. Document each once.
- Keep skills in `skills/<name>/SKILL.md`, matching frontmatter names to directories and following the [specification](https://agentskills.io/specification).
- Keep skill-specific scripts and references with their skill. Put shared tools in `scripts/`.
- Check referenced paths and tools. Run changed scripts, including error paths. Report checks and limitations.
- Correct documentation made inaccurate by workflow changes. Add documentation only when requested or needed to use the change.
