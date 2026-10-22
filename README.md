# Agent harness

Shared instructions, skills, and tools for the agents I use. Updated when real sessions reveal something worth fixing.

## Usage

Requires Python 3.9+. From the repository root:

```sh
scripts/setup.py
```

Run `scripts/setup.py --help` for previews, checks, and backups.

## How it works

Setup creates symlinks from each agent's settings to the files in this repository. Edit a file here once to update every linked client. Keep this repository folder in place.

- [Personal instructions](instructions/AGENTS.md) set how agents work in every project.
- [Repository instructions](AGENTS.md) cover changes to the harness. Setup does not install them.
- Skills provide task-specific knowledge and workflows, following the [Agent Skills specification](https://agentskills.io/specification).

The agent client runs the agent and provides its tools and permissions.

## Licence

MIT
