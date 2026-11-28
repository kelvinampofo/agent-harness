---
name: change-description
description: Write or update a pull or merge request description that tells reviewers what changed, how it behaved before and why. Use when asked to write up a branch, open or update a PR or MR, trim its description, or derive a commit or squash message from it. Not for reviewing a PR's code or writing release notes. Use technical-writing for other prose and standalone commit messages.
---

# Change description

Write for a reviewer who can already see the diff, tests, CI, logs, commits and the Git forge's UI. Use plain prose in the first person plural. Scale the length to the change: one paragraph for a small fix, more for several causes or a measured claim.

## Gather

1. Read the diff against the target branch in the PR or MR metadata, otherwise the default branch.
2. When updating, read the current description. Keep the author's edits, useful links and sections the repository requires. Correct claims the diff has made stale.

## Write

1. Title the resulting behaviour. Follow the repository's title convention, otherwise use `<area>: <summary>`.
2. Put issue links first, such as `Fixes #123`. Follow them with any breaking change, prefixed `Breaking:`.
3. Open with the new behaviour in the user's or caller's terms.
4. Follow with what happened previously and a concrete reproduction: an input, command or set of steps.
5. Explain the cause when the fix depends on it. Number separate causes.
6. Justify non-obvious choices with a linked specification, prior art or reference implementation.
7. State costs, trade-offs, migration steps and what the change leaves unaffected.
8. For performance claims, give a table with the tool, device and run count. Include workloads that should stay unchanged. Make the headline figure match the table's range.
9. Show new API usage in a code block.

## Gotchas

- Leave out what the reviewer can already see, such as test lists, commands run, pass counts, changed files and "Testing" sections.
- Include evidence the reviewer cannot see, such as benchmarks or manual checks on real devices, only when it supports a claim in the description.
- Check each claim against the diff or its evidence. Send the author, outside the description, each question the diff cannot settle and each claim you could not verify. Give the file and line where one applies, and the constraint that prevented verification. Post them as line comments only when asked.

## Example

Title: `select: typeahead searches every option in a virtualised list`

```markdown
Fixes #412

Typeahead in a virtualised select now searches every option and scrolls the match into view. Typing `u` from the top of the country select reaches Uganda.

Previously, typeahead searched only the rendered options, about 30 at a time, so the same keystroke did nothing until the user scrolled near Uganda.

Keystrokes less than 500 ms apart form one query, so `net` reaches Netherlands. The [APG listbox pattern](https://www.w3.org/WAI/ARIA/apg/patterns/listbox/) recommends matching characters typed in rapid succession but sets no interval, so we reuse our combobox's 500 ms.

Selects that load options on demand still search only the loaded options.
```

## Publish

Publish only when asked, using the `gh` or `glab` skill. Report the URL and anything the command could not set, such as reviewers or labels.

## Commit or squash message

Follow the personal commit instructions, with the resulting behaviour as the subject, such as `Search every option in select typeahead`.
