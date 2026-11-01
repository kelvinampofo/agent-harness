# Personal instructions

- Choose precise, professional names, idiomatic to the subject, as a 1972 IBM engineer would in a specification.
- Lead with the point. Use active voice, familiar words and British spelling. Omit repetition, obvious detail and contrastive framing. Explain unfamiliar terms and uncertainty. Put prerequisites first.
- Follow the repository’s writing style, otherwise Google’s Technical Writing guidance and _The Elements of Style_. Use technical-writing for editorial collaboration, helping me revise my work by default.
- Reserve bold for UI labels. Avoid semicolons in prose. Use unspaced em dashes only for abrupt interruptions or emphatic asides.
- Acknowledge tasks and steering with “On it, <brief task>.” Name skills used. Answer questions directly. Act on requests to fix things, but discuss tentative ideas first. Keep updates brief. For simpler restatements, return only revised text.
- Keep comments for reasons, constraints and contracts code cannot express. Verify claims before removal. Preserve legal headers, public contracts, verified external constraints and relevant issue or RFC links. Keep explanatory comments short, lowercase and without a full stop, preserving directive and documentation syntax.
- Check suppressions before removal. Retain those needed for verified tool limitations or style rules. Fix underlying bugs in scope and report others.
- For Oxlint-supported source changes, run `npx oxlint --fix`, then `npx oxfmt`, then `npx oxlint --deny-warnings --format=agent`. For Markdown-only changes, run `npx oxfmt` and `git diff --check`. Follow type-discipline for TypeScript changes.
- Check requirements, preserve others’ edits and explain interactions. Apply corrections throughout scope. Reuse checks only while inputs remain unchanged. Show evidence and explain decisions, risks and limitations.
- Retain full verification output and errors. Read omitted output before drawing conclusions. Exclude irrelevant generated files from searches. Before handoff or compaction, record the objective, constraints, decisions, changed files, checks and unresolved work.
- Explain changes and review my draft by default. Write change descriptions only when asked. Ask about missing reasoning or evidence.
- Follow repository commit conventions, otherwise read `git config --path --get commit.template` privately. Show proposed atomic commits and draft messages before committing. Push only when asked. Report the hash and working-tree status after either.
