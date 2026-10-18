# Compare harness changes

Use repeated, blind-graded runs when one rerun cannot settle a decision, effects may differ by model, or a change is costly to keep.

## Plan

1. Name the change, its expected effect, and what would show it fails. Define three to six observable criteria for outcomes and proof. Do not show the rubric to the agents doing the task.
2. Choose a task that exercises the change.
3. Hold task, starting state, permissions, instructions, and tools constant. Run both versions on every model to separate model and harness effects.
4. Run each version at least three times per model, in random order. Treat small samples as a trend only.
5. Show the plan, run count, cost, and side effects. Wait for approval.

## Run

1. Give each run its own ordinarily named working directory and user request. Do not mention testing or other runs in prompts. Do not ask agents which skills or files they used.
2. Give each run normal session context and the harness version being tested. Use client options so user-level instructions and skills cannot override the test copies. When testing improve-harness, remove this guide and its link from both copies.
3. Use fresh, non-interactive sessions. Save machine-readable transcripts outside working directories. Limit actions to the task and stub outside effects, such as opening editors. Run one at a time when runs share writable files.

## Grade

1. Check loaded context, use of the tested version, and denied actions. Exclude runs that never used the change, loaded the wrong version, or had unequal permissions.
2. Grade transcripts and outputs, not agent self-reports.
3. Use one judge from another model family where available. Grade all outputs together on one scale, with shuffled labels hiding model and version. Supply the rubric and preserve referenced filenames and paths.
4. Read every output yourself. Resolve disagreements with the judge before recommending.

## Report

Report the change, expected effect, rubric, run count, notes grouped by version and model, judge scores, your assessment, and recommendation. List findings common to both versions separately.

Restore shared locations. List generated session histories and ask the user to remove them so later reviews do not treat them as ordinary work.
