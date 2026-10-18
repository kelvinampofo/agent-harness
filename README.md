# Agent harness

Agents repeat their mistakes until something around them changes. This repository is where I make those changes, once, for every agent I use.

When an agent slips, I fix the cause here. A recurring slip becomes a line in the instructions. A judgement call becomes a skill, such as how to explain a change or how much proof a fix needs. When an agent can't tell whether its work is right, I give it a command that can, such as `scripts/setup.py --check`.

Every fix starts from a real session, so the harness grows from what went wrong and what worked. Over time I supervise less, and hopefully less code for me to maintain.

## Usage

Requires Python 3.9+. From the repository root:

```sh
scripts/setup.py
```

Run `scripts/setup.py --help` for options and troubleshooting.

You can also ask an agent in this repository to set up the harness.

## How it works

Setup symlinks the files each agent client reads to this checkout. Edit a file here once to update every linked client. Keep the checkout where it is.

- [Personal instructions](instructions/AGENTS.md) set how agents work in every project.
- Skills in `skills/` provide task-specific knowledge and workflows, following the [Agent Skills specification](https://agentskills.io/specification).
- [Repository instructions](AGENTS.md) cover changes to the harness. Setup does not install them.

The agent client runs the agent and provides its tools and permissions.

## Licence

MIT
