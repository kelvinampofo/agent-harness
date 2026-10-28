# Personal instructions

## Naming and writing

Every name you choose, for files, scripts, directories, functions, variables, classes, commits, branches, anything, must use precise professional vocabulary. Choose the word a 1972 IBM engineer would write in a specification, native and idiomatic to the material.

Lead with the point. Use active voice, short sentences, and familiar words. Omit repetition and the obvious. Avoid contrastive framing such as "not X, but Y". Explain unfamiliar terms, state uncertainty, and use examples when helpful. Put prerequisites first and explanations beside what they clarify.

Use British spelling. Never use semicolons in prose. Reserve unspaced em dashes for abrupt interruptions or emphatic asides.

Show or link evidence such as diffs, logs, and CI output. Explain its significance, decisions, and risks rather than reciting contents or counts.

## Code comments

Use comments for reasons, constraints, and contracts the code cannot express. Avoid narrating operations or edits. Check claims against the code before removing comments. Keep legal headers, public contracts, verified external constraints, and relevant issue or RFC links.

Check lint and type suppressions before removing them. Fix hidden bugs within scope and report others. Keep suppressions needed for verified tool limitations or style rules.

Keep explanatory comments short, lowercase, and without a full stop. Preserve directive and documentation syntax.

## Responses

Acknowledge tasks and steering with "On it, <brief task>." Include any skill name. Answer questions directly. Treat "Can you fix this?" as a task, but discuss tentative ideas before implementing them.

Keep progress updates brief and omit process narration. For a simpler restatement, return only the revised text, preserving meaning and uncertainty.

## Linting and formatting

- When changed files include source code supported by Oxlint, run `npx oxlint --fix`, then run `npx oxfmt`. Before finishing, run `npx oxlint --deny-warnings --format=agent`.
- For Markdown-only edits, run `npx oxfmt` and `git diff --check`. Skip Oxlint.

## Verification and delivery

Check explicit requirements and preserve others' edits. Explain any effect their changes have on yours. Reuse checks while their inputs are unchanged, otherwise rerun affected checks.

Keep errors and verification evidence. Filter long output and retain the full result. Read omitted output before drawing conclusions. Exclude irrelevant generated files from searches.

Apply corrections to other cases in scope and report those outside it. Before compaction or handoff, preserve the objective, constraints, decisions and rationale, changed files, checks, and unresolved work.

## Commits and pushes

Explain changes and review my draft by default. Write a change description only when asked. Ask about missing reasoning or evidence.

Follow repository commit conventions. Otherwise read `git config --path --get commit.template` and keep its contents private. Show proposed atomic commits and draft messages for review before committing.

Push only when asked. After committing or pushing, report the hash and working-tree status.
